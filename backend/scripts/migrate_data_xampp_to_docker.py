"""
Script utama untuk migrasi data dari MySQL XAMPP ke MySQL Docker
Script ini mengkoordinasikan proses export dan import

Penggunaan:
    python -m scripts.migrate_data_xampp_to_docker
    python -m scripts.migrate_data_xampp_to_docker --auto
    python -m scripts.migrate_data_xampp_to_docker --export-only
    python -m scripts.migrate_data_xampp_to_docker --import-only backup_data.sql
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.config.settings import settings


def run_export(
    xampp_host: str = "localhost",
    xampp_port: int = 3306,
    xampp_user: str = "root",
    xampp_password: str = "",
    database: str = None,
    output_file: str = None
) -> Path:
    """Jalankan export dari XAMPP"""
    print("\n" + "=" * 60)
    print("STEP 1: EXPORT DATA DARI XAMPP")
    print("=" * 60)
    
    # Import export script
    from scripts.export_data_from_xampp import export_with_mysqldump, export_with_pymysql
    
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"backup_data_{timestamp}.sql"
    
    output_path = Path(root_dir) / output_file
    database = database or settings.DB_NAME
    
    # Cek apakah file sudah ada
    if output_path.exists():
        response = input(f"\n[WARNING] File {output_path} sudah ada. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Export dibatalkan")
            return None
        output_path.unlink()
    
    # Export dengan mysqldump dulu, fallback ke pymysql
    success = export_with_mysqldump(
        xampp_host, xampp_port, xampp_user, xampp_password,
        database, str(output_path)
    )
    
    if not success:
        print("\n[INFO] Mencoba dengan pymysql sebagai fallback...")
        success = export_with_pymysql(
            xampp_host, xampp_port, xampp_user, xampp_password,
            database, str(output_path)
        )
    
    if success:
        print(f"\n[SUCCESS] Export selesai: {output_path}")
        return output_path
    else:
        print(f"\n[ERROR] Export gagal!")
        return None


def run_import(
    sql_file: str,
    docker_host: str = "localhost",
    docker_port: int = 3308,
    docker_user: str = "root",
    docker_password: str = "",
    database: str = None,
    auto: bool = False
) -> bool:
    """Jalankan import ke Docker"""
    print("\n" + "=" * 60)
    print("STEP 2: IMPORT DATA KE DOCKER")
    print("=" * 60)
    
    # Import import script
    from scripts.import_data_to_docker import (
        import_with_mysql_command,
        import_with_pymysql,
        validate_sql_file,
        check_database_exists
    )
    
    sql_path = Path(sql_file)
    if not sql_path.is_absolute():
        sql_path = root_dir / sql_path
    
    database = database or settings.DB_NAME
    
    # Validasi file
    if not validate_sql_file(str(sql_path)):
        print("[ERROR] Validasi file gagal!")
        return False
    
    # Cek database
    print(f"\n[INFO] Mengecek database...")
    if not check_database_exists(docker_host, docker_port, docker_user, docker_password, database):
        print(f"[WARNING] Database '{database}' tidak ditemukan!")
        print(f"[INFO] Pastikan migration sudah dijalankan terlebih dahulu")
        response = input("   Lanjutkan? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Import dibatalkan")
            return False
    
    # Konfirmasi (skip jika auto mode)
    if not auto:
        print(f"\n[WARNING] Data yang ada di database '{database}' akan di-overwrite!")
        response = input("   Lanjutkan import? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Import dibatalkan")
            return False
    else:
        print(f"\n[INFO] Auto mode: Melanjutkan import ke database '{database}'...")
    
    # Import dengan mysql command dulu, fallback ke pymysql
    success = import_with_mysql_command(
        docker_host, docker_port, docker_user, docker_password,
        database, str(sql_path)
    )
    
    if not success:
        print("\n[INFO] Mencoba dengan pymysql sebagai fallback...")
        success = import_with_pymysql(
            docker_host, docker_port, docker_user, docker_password,
            database, str(sql_path)
        )
    
    if success:
        print(f"\n[SUCCESS] Import selesai ke database '{database}'")
        return True
    else:
        print(f"\n[ERROR] Import gagal!")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Migrasi data dari MySQL XAMPP ke MySQL Docker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  # Full migration (export + import)
  python -m scripts.migrate_data_xampp_to_docker
  
  # Auto (tanpa konfirmasi)
  python -m scripts.migrate_data_xampp_to_docker --auto
  
  # Export saja
  python -m scripts.migrate_data_xampp_to_docker --export-only
  
  # Import saja (dari file yang sudah ada)
  python -m scripts.migrate_data_xampp_to_docker --import-only backup_data.sql
        """
    )
    
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='Auto mode (skip konfirmasi)'
    )
    parser.add_argument(
        '--export-only',
        action='store_true',
        help='Hanya export dari XAMPP'
    )
    parser.add_argument(
        '--import-only',
        type=str,
        metavar='SQL_FILE',
        help='Hanya import ke Docker (butuh path ke file SQL)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Nama file output untuk export'
    )
    
    # XAMPP settings
    parser.add_argument(
        '--xampp-host',
        type=str,
        default='localhost',
        help='XAMPP MySQL host (default: localhost)'
    )
    parser.add_argument(
        '--xampp-port',
        type=int,
        default=3306,
        help='XAMPP MySQL port (default: 3306)'
    )
    parser.add_argument(
        '--xampp-user',
        type=str,
        default='root',
        help='XAMPP MySQL user (default: root)'
    )
    parser.add_argument(
        '--xampp-password',
        type=str,
        default='',
        help='XAMPP MySQL password (default: kosong)'
    )
    
    # Docker settings
    parser.add_argument(
        '--docker-host',
        type=str,
        default='localhost',
        help='Docker MySQL host (default: localhost untuk port mapping)'
    )
    parser.add_argument(
        '--docker-port',
        type=int,
        default=3308,
        help='Docker MySQL port (default: 3308 sesuai docker-compose)'
    )
    parser.add_argument(
        '--docker-user',
        type=str,
        default='root',
        help='Docker MySQL user (default: root)'
    )
    parser.add_argument(
        '--docker-password',
        type=str,
        default='',
        help='Docker MySQL password (default: kosong)'
    )
    parser.add_argument(
        '--database',
        type=str,
        default=None,
        help='Database name (default: dari settings)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MIGRASI DATA: XAMPP -> DOCKER")
    print("=" * 60)
    print(f"XAMPP Source:")
    print(f"   Host: {args.xampp_host}:{args.xampp_port}")
    print(f"   User: {args.xampp_user}")
    print(f"   Database: {args.database or settings.DB_NAME}")
    print(f"\nDocker Target:")
    print(f"   Host: {args.docker_host}:{args.docker_port}")
    print(f"   User: {args.docker_user}")
    print(f"   Database: {args.database or settings.DB_NAME}")
    print("=" * 60)
    
    # Mode: import only
    if args.import_only:
        if not Path(args.import_only).exists():
            sql_path = root_dir / args.import_only
            if not sql_path.exists():
                print(f"[ERROR] File tidak ditemukan: {args.import_only}")
                sys.exit(1)
            sql_file = str(sql_path)
        else:
            sql_file = args.import_only
        
        success = run_import(
            sql_file,
            args.docker_host, args.docker_port,
            args.docker_user, args.docker_password,
            args.database,
            args.auto
        )
        sys.exit(0 if success else 1)
    
    # Mode: export only
    if args.export_only:
        output_path = run_export(
            args.xampp_host, args.xampp_port,
            args.xampp_user, args.xampp_password,
            args.database, args.output
        )
        if output_path:
            print(f"\n[INFO] File export: {output_path}")
            print(f"[INFO] Jalankan import dengan:")
            print(f"   python -m scripts.migrate_data_xampp_to_docker --import-only {output_path.name}")
        sys.exit(0 if output_path else 1)
    
    # Mode: full migration
    print("\n[INFO] Mode: Full Migration (Export + Import)")
    if not args.auto:
        response = input("\nLanjutkan? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Migrasi dibatalkan")
            sys.exit(0)
    
    # Step 1: Export
    output_path = run_export(
        args.xampp_host, args.xampp_port,
        args.xampp_user, args.xampp_password,
        args.database, args.output
    )
    
    if not output_path:
        print("\n[ERROR] Export gagal, migrasi dibatalkan")
        sys.exit(1)
    
    # Step 2: Import
    if not args.auto:
        response = input("\nLanjutkan ke import? (y/n): ")
        if response.lower() != 'y':
            print(f"[INFO] Import dibatalkan. File export tersimpan di: {output_path}")
            sys.exit(0)
    
    success = run_import(
        str(output_path),
        args.docker_host, args.docker_port,
        args.docker_user, args.docker_password,
        args.database,
        args.auto
    )
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] MIGRASI DATA SELESAI!")
        print("=" * 60)
        print(f"[INFO] Data sudah diimport ke MySQL Docker")
        print(f"[INFO] Silakan test login dengan data yang sudah diimport")
        print(f"[INFO] File backup tersimpan di: {output_path}")
    else:
        print("\n[ERROR] Import gagal!")
        print(f"[INFO] File export tersimpan di: {output_path}")
        print(f"[INFO] Coba import manual dengan:")
        print(f"   python -m scripts.migrate_data_xampp_to_docker --import-only {output_path.name}")
        sys.exit(1)


if __name__ == "__main__":
    main()

