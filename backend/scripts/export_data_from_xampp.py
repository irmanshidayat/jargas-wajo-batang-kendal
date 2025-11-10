"""
Script untuk export data dari MySQL XAMPP ke file SQL
Penggunaan:
    python -m scripts.export_data_from_xampp
    python -m scripts.export_data_from_xampp --output backup_data.sql
    python -m scripts.export_data_from_xampp --tables users,projects --output partial_backup.sql
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.config.settings import settings


def get_mysqldump_command(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    output_file: str,
    tables: list = None
) -> list:
    """Membuat command mysqldump"""
    cmd = [
        "mysqldump",
        f"--host={host}",
        f"--port={port}",
        f"--user={user}",
    ]
    
    if password:
        cmd.append(f"--password={password}")
    
    cmd.extend([
        "--single-transaction",
        "--routines",
        "--triggers",
        "--default-character-set=utf8mb4",
        "--skip-lock-tables",
        database
    ])
    
    # Jika hanya tabel tertentu
    if tables:
        cmd.extend(tables)
    
    return cmd


def export_with_mysqldump(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    output_file: str,
    tables: list = None
) -> bool:
    """Export data menggunakan mysqldump"""
    try:
        cmd = get_mysqldump_command(host, port, user, password, database, output_file, tables)
        
        print(f"[INFO] Menjalankan mysqldump...")
        print(f"   Host: {host}:{port}")
        print(f"   Database: {database}")
        if tables:
            print(f"   Tables: {', '.join(tables)}")
        print(f"   Output: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )
        
        if result.returncode != 0:
            print(f"[ERROR] mysqldump gagal:")
            print(result.stderr)
            return False
        
        # Cek ukuran file
        file_size = Path(output_file).stat().st_size
        print(f"[SUCCESS] Export berhasil!")
        print(f"   File: {output_file}")
        print(f"   Ukuran: {file_size / 1024 / 1024:.2f} MB")
        return True
        
    except FileNotFoundError:
        print("[ERROR] mysqldump tidak ditemukan!")
        print("   Pastikan MySQL client tools sudah terinstall")
        print("   Atau gunakan opsi --use-python untuk export manual")
        return False
    except Exception as e:
        print(f"[ERROR] Error saat export: {str(e)}")
        return False


def export_with_pymysql(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    output_file: str,
    tables: list = None
) -> bool:
    """Export data menggunakan pymysql (fallback jika mysqldump tidak ada)"""
    try:
        import pymysql
        
        print(f"[INFO] Menghubungkan ke database...")
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # Get list of tables
        if tables:
            table_list = tables
        else:
            cursor.execute("SHOW TABLES")
            table_list = [row[0] for row in cursor.fetchall()]
        
        print(f"[INFO] Mengexport {len(table_list)} tabel...")
        print(f"   Tables: {', '.join(table_list)}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"-- MySQL dump dari {database}\n")
            f.write(f"-- Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Host: {host}:{port}\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=0;\n")
            f.write("SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO';\n")
            f.write("SET AUTOCOMMIT=0;\n")
            f.write("START TRANSACTION;\n\n")
            
            # Export each table
            for table in table_list:
                print(f"   [INFO] Mengexport tabel: {table}")
                
                # Get table structure
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_table = cursor.fetchone()[1]
                f.write(f"\n-- Table structure for table `{table}`\n")
                f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                f.write(f"{create_table};\n\n")
                
                # Get table data
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                row_count = cursor.fetchone()[0]
                
                if row_count > 0:
                    f.write(f"-- Dumping data for table `{table}`\n")
                    cursor.execute(f"SELECT * FROM `{table}`")
                    
                    # Get column names
                    columns = [desc[0] for desc in cursor.description]
                    
                    # Fetch data in batches
                    batch_size = 1000
                    cursor.execute(f"SELECT * FROM `{table}`")
                    
                    first_row = True
                    while True:
                        rows = cursor.fetchmany(batch_size)
                        if not rows:
                            break
                        
                        for row in rows:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                elif isinstance(val, bytes):
                                    values.append(f"0x{val.hex()}")
                                else:
                                    # Escape string
                                    val_str = str(val).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")
                                    values.append(f"'{val_str}'")
                            
                            if first_row:
                                f.write(f"INSERT INTO `{table}` (`{'`, `'.join(columns)}`) VALUES\n")
                                first_row = False
                            else:
                                f.write(",\n")
                            
                            f.write(f"({', '.join(values)})")
                    
                    f.write(";\n\n")
                    print(f"      [OK] {row_count} rows exported")
                else:
                    print(f"      [OK] Tabel kosong")
            
            # Write footer
            f.write("COMMIT;\n")
            f.write("SET FOREIGN_KEY_CHECKS=1;\n")
        
        cursor.close()
        conn.close()
        
        # Cek ukuran file
        file_size = Path(output_file).stat().st_size
        print(f"\n[SUCCESS] Export berhasil!")
        print(f"   File: {output_file}")
        print(f"   Ukuran: {file_size / 1024 / 1024:.2f} MB")
        return True
        
    except ImportError:
        print("[ERROR] pymysql tidak terinstall!")
        print("   Install dengan: pip install pymysql")
        return False
    except Exception as e:
        print(f"[ERROR] Error saat export: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Export data dari MySQL XAMPP')
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Nama file output (default: backup_data_YYYYMMDD_HHMMSS.sql)'
    )
    parser.add_argument(
        '--tables', '-t',
        type=str,
        default=None,
        help='Daftar tabel yang akan diexport (comma-separated, contoh: users,projects)'
    )
    parser.add_argument(
        '--use-python',
        action='store_true',
        help='Gunakan pymysql untuk export (jika mysqldump tidak tersedia)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='MySQL host (default: dari settings atau localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='MySQL port (default: dari settings atau 3306)'
    )
    parser.add_argument(
        '--user',
        type=str,
        default=None,
        help='MySQL user (default: dari settings atau root)'
    )
    parser.add_argument(
        '--password',
        type=str,
        default=None,
        help='MySQL password (default: dari settings)'
    )
    parser.add_argument(
        '--database',
        type=str,
        default=None,
        help='Database name (default: dari settings)'
    )
    
    args = parser.parse_args()
    
    # Konfigurasi database source (XAMPP)
    host = args.host or "localhost"
    port = args.port or 3306
    user = args.user or "root"
    password = args.password or ""
    database = args.database or settings.DB_NAME
    
    # Parse tables
    tables = None
    if args.tables:
        tables = [t.strip() for t in args.tables.split(',')]
    
    # Generate output filename
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"backup_data_{timestamp}.sql"
    
    # Pastikan output file di folder backend
    output_path = Path(root_dir) / output_file
    
    print("=" * 60)
    print("EXPORT DATA DARI MYSQL XAMPP")
    print("=" * 60)
    print(f"Source Database:")
    print(f"   Host: {host}:{port}")
    print(f"   User: {user}")
    print(f"   Database: {database}")
    print(f"   Output: {output_path}")
    print("=" * 60)
    
    # Cek apakah file sudah ada
    if output_path.exists():
        response = input(f"\n[WARNING] File {output_path} sudah ada. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Export dibatalkan")
            return
        output_path.unlink()
    
    # Export data
    if args.use_python:
        success = export_with_pymysql(host, port, user, password, database, str(output_path), tables)
    else:
        success = export_with_mysqldump(host, port, user, password, database, str(output_path), tables)
        if not success:
            print("\n[INFO] Mencoba dengan pymysql sebagai fallback...")
            success = export_with_pymysql(host, port, user, password, database, str(output_path), tables)
    
    if success:
        print(f"\n[SUCCESS] Data berhasil diexport ke: {output_path}")
        print(f"[INFO] File siap untuk diimport ke MySQL Docker")
    else:
        print(f"\n[ERROR] Export gagal!")
        sys.exit(1)


if __name__ == "__main__":
    main()

