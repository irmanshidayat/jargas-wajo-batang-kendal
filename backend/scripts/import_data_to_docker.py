"""
Script untuk import data dari file SQL ke MySQL Docker
Penggunaan:
    python -m scripts.import_data_to_docker backup_data.sql
    python -m scripts.import_data_to_docker backup_data.sql --host mysql --port 3306
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.config.settings import settings


def import_with_mysql_command(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    sql_file: str
) -> bool:
    """Import data menggunakan mysql command"""
    try:
        cmd = [
            "mysql",
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
        ]
        
        if password:
            cmd.append(f"--password={password}")
        
        cmd.append(database)
        
        print(f"[INFO] Menjalankan mysql import...")
        print(f"   Host: {host}:{port}")
        print(f"   Database: {database}")
        print(f"   File: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )
        
        if result.returncode != 0:
            print(f"[ERROR] Import gagal:")
            print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False
        
        print(f"[SUCCESS] Import berhasil!")
        return True
        
    except FileNotFoundError:
        print("[ERROR] mysql command tidak ditemukan!")
        print("   Pastikan MySQL client tools sudah terinstall")
        print("   Atau gunakan opsi --use-python untuk import manual")
        return False
    except Exception as e:
        print(f"[ERROR] Error saat import: {str(e)}")
        return False


def import_with_pymysql(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    sql_file: str
) -> bool:
    """Import data menggunakan pymysql (fallback jika mysql command tidak ada)"""
    try:
        import pymysql
        
        print(f"[INFO] Menghubungkan ke database...")
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            autocommit=False
        )
        
        cursor = conn.cursor()
        
        print(f"[INFO] Membaca file SQL: {sql_file}")
        file_size = Path(sql_file).stat().st_size
        print(f"   Ukuran file: {file_size / 1024 / 1024:.2f} MB")
        
        # Disable foreign key checks temporarily
        print(f"[INFO] Menyiapkan database...")
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        cursor.execute("SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO'")
        cursor.execute("SET AUTOCOMMIT=0")
        cursor.execute("START TRANSACTION")
        
        # Baca dan execute file SQL line by line untuk handle multi-line statements
        print(f"[INFO] Membaca dan menjalankan file SQL...")
        
        current_statement = ""
        executed = 0
        errors = 0
        line_num = 0
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            for line in f:
                line_num += 1
                # Skip comments
                stripped = line.strip()
                if not stripped or stripped.startswith('--') or stripped.startswith('/*'):
                    continue
                
                # Append line to current statement
                current_statement += line
                
                # Check if statement is complete (ends with semicolon)
                if stripped.endswith(';'):
                    # Execute complete statement
                    stmt = current_statement.strip()
                    if stmt and len(stmt) > 5:
                        try:
                            cursor.execute(stmt)
                            executed += 1
                            
                            if executed % 20 == 0:
                                print(f"   Progress: {executed} statements executed (errors: {errors})")
                        except Exception as e:
                            errors += 1
                            error_msg = str(e).lower()
                            # Skip error untuk beberapa statement yang tidak critical
                            if any(skip in error_msg for skip in [
                                'already exists', 'unknown database', 'drop table',
                                'duplicate entry', 'table doesn\'t exist', 'duplicate key'
                            ]):
                                continue
                            # Tampilkan error untuk debugging (maksimal 10 error)
                            if errors <= 10:
                                print(f"[WARNING] Error pada line {line_num}: {str(e)[:150]}")
                                # Debug: print first 200 chars of statement
                                if errors <= 3:
                                    print(f"   Statement: {stmt[:200]}...")
                    
                    # Reset untuk statement berikutnya
                    current_statement = ""
        
        # Execute any remaining statement
        if current_statement.strip():
            try:
                cursor.execute(current_statement.strip())
                executed += 1
            except Exception as e:
                errors += 1
                if errors <= 10:
                    print(f"[WARNING] Error pada final statement: {str(e)[:150]}")
        
        print(f"   Total statements executed: {executed}")
        
        # Commit transaction
        print(f"[INFO] Commit transaction...")
        conn.commit()
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        
        cursor.close()
        conn.close()
        
        print(f"\n[SUCCESS] Import berhasil!")
        print(f"   Statements executed: {executed}")
        if errors > 0:
            print(f"   Warnings/Errors: {errors} (beberapa mungkin tidak critical)")
        return True
        
    except ImportError:
        print("[ERROR] pymysql tidak terinstall!")
        print("   Install dengan: pip install pymysql")
        return False
    except Exception as e:
        print(f"[ERROR] Error saat import: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False


def validate_sql_file(sql_file: str) -> bool:
    """Validasi file SQL sebelum import"""
    if not Path(sql_file).exists():
        print(f"[ERROR] File tidak ditemukan: {sql_file}")
        return False
    
    if not sql_file.endswith('.sql'):
        print(f"[WARNING] File bukan .sql: {sql_file}")
        response = input("   Lanjutkan? (y/n): ")
        if response.lower() != 'y':
            return False
    
    file_size = Path(sql_file).stat().st_size
    if file_size == 0:
        print(f"[ERROR] File kosong: {sql_file}")
        return False
    
    print(f"[INFO] File valid: {sql_file} ({file_size / 1024 / 1024:.2f} MB)")
    return True


def check_database_exists(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str
) -> bool:
    """Cek apakah database sudah ada"""
    try:
        import pymysql
        
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (database,))
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        return exists
    except Exception as e:
        print(f"[WARNING] Tidak bisa cek database: {str(e)}")
        return True  # Assume exists to continue


def main():
    parser = argparse.ArgumentParser(description='Import data ke MySQL Docker')
    parser.add_argument(
        'sql_file',
        type=str,
        help='Path ke file SQL yang akan diimport'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='MySQL host (default: dari settings atau mysql untuk Docker)'
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
    parser.add_argument(
        '--use-python',
        action='store_true',
        help='Gunakan pymysql untuk import (jika mysql command tidak tersedia)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip validasi file SQL'
    )
    
    args = parser.parse_args()
    
    # Konfigurasi database target (Docker)
    # Default untuk Docker: host=mysql, port=3306
    # Tapi bisa juga localhost:3308 jika dari host machine
    host = args.host or "localhost"
    port = args.port or 3308  # Port mapped di docker-compose
    user = args.user or "root"
    password = args.password or ""
    database = args.database or settings.DB_NAME
    
    # Resolve SQL file path
    sql_file = Path(args.sql_file)
    if not sql_file.is_absolute():
        # Coba relative dari root_dir
        sql_file = root_dir / sql_file
    
    print("=" * 60)
    print("IMPORT DATA KE MYSQL DOCKER")
    print("=" * 60)
    print(f"Target Database:")
    print(f"   Host: {host}:{port}")
    print(f"   User: {user}")
    print(f"   Database: {database}")
    print(f"   SQL File: {sql_file}")
    print("=" * 60)
    
    # Validasi file
    if not args.skip_validation:
        if not validate_sql_file(str(sql_file)):
            print("[ERROR] Validasi file gagal!")
            sys.exit(1)
    
    # Cek database
    print(f"\n[INFO] Mengecek database...")
    if not check_database_exists(host, port, user, password, database):
        print(f"[WARNING] Database '{database}' tidak ditemukan!")
        print(f"[INFO] Pastikan migration sudah dijalankan terlebih dahulu")
        response = input("   Lanjutkan? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Import dibatalkan")
            return
    
    # Konfirmasi
    print(f"\n[WARNING] Data yang ada di database '{database}' akan di-overwrite!")
    response = input("   Lanjutkan import? (y/n): ")
    if response.lower() != 'y':
        print("[INFO] Import dibatalkan")
        return
    
    # Import data
    if args.use_python:
        success = import_with_pymysql(host, port, user, password, database, str(sql_file))
    else:
        success = import_with_mysql_command(host, port, user, password, database, str(sql_file))
        if not success:
            print("\n[INFO] Mencoba dengan pymysql sebagai fallback...")
            success = import_with_pymysql(host, port, user, password, database, str(sql_file))
    
    if success:
        print(f"\n[SUCCESS] Data berhasil diimport ke database '{database}'")
        print(f"[INFO] Silakan test login dengan data yang sudah diimport")
    else:
        print(f"\n[ERROR] Import gagal!")
        sys.exit(1)


if __name__ == "__main__":
    main()

