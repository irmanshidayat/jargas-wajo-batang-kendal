"""
Script untuk menjalankan migrasi database menggunakan Alembic
Penggunaan:
    - Upgrade ke versi terbaru: python -m scripts.run_migrations
    - Upgrade ke versi tertentu: python -m scripts.run_migrations --revision <revision_id>
    - Downgrade: python -m scripts.run_migrations --downgrade --revision <revision_id>
    - Show current version: python -m scripts.run_migrations --current
    - Show history: python -m scripts.run_migrations --history
"""
import sys
import os
import argparse
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from alembic import command
from alembic.config import Config
from app.config.settings import settings

def get_alembic_config():
    """Membuat konfigurasi Alembic"""
    alembic_cfg = Config(str(root_dir / "alembic.ini"))
    
    # Override sqlalchemy.url dari settings
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    
    return alembic_cfg

def upgrade(revision: str = "head"):
    """Upgrade database ke versi tertentu"""
    alembic_cfg = get_alembic_config()
    print(f"🔄 Memulai upgrade database ke revision: {revision}")
    try:
        command.upgrade(alembic_cfg, revision)
        print(f"✅ Upgrade berhasil!")
    except Exception as e:
        print(f"❌ Error saat upgrade: {str(e)}")
        raise

def downgrade(revision: str):
    """Downgrade database ke versi tertentu"""
    alembic_cfg = get_alembic_config()
    print(f"🔄 Memulai downgrade database ke revision: {revision}")
    try:
        command.downgrade(alembic_cfg, revision)
        print(f"✅ Downgrade berhasil!")
    except Exception as e:
        print(f"❌ Error saat downgrade: {str(e)}")
        raise

def show_current():
    """Menampilkan versi migration saat ini"""
    alembic_cfg = get_alembic_config()
    try:
        command.current(alembic_cfg)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def show_history():
    """Menampilkan history migration"""
    alembic_cfg = get_alembic_config()
    try:
        command.history(alembic_cfg)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def show_stamp(revision: str):
    """Stamp database dengan revision tertentu tanpa menjalankan migration"""
    alembic_cfg = get_alembic_config()
    print(f"🔄 Stamping database dengan revision: {revision}")
    try:
        command.stamp(alembic_cfg, revision)
        print(f"✅ Stamping berhasil!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Jalankan migrasi database Alembic")
    parser.add_argument(
        "--revision", "-r",
        type=str,
        default="head",
        help="Revision ID untuk upgrade/downgrade (default: head)"
    )
    parser.add_argument(
        "--downgrade", "-d",
        action="store_true",
        help="Jalankan downgrade instead of upgrade"
    )
    parser.add_argument(
        "--current", "-c",
        action="store_true",
        help="Tampilkan versi migration saat ini"
    )
    parser.add_argument(
        "--history", "-h",
        action="store_true",
        help="Tampilkan history migration"
    )
    parser.add_argument(
        "--stamp", "-s",
        type=str,
        help="Stamp database dengan revision tertentu (tanpa menjalankan migration)"
    )
    
    args = parser.parse_args()
    
    if args.current:
        show_current()
    elif args.history:
        show_history()
    elif args.stamp:
        show_stamp(args.stamp)
    elif args.downgrade:
        if args.revision == "head":
            print("❌ Error: Downgrade memerlukan --revision")
            sys.exit(1)
        downgrade(args.revision)
    else:
        upgrade(args.revision)

if __name__ == "__main__":
    main()

