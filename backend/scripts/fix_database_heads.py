"""
Script untuk membersihkan multiple heads di database
"""
import sys
import io
from pathlib import Path

# Fix encoding untuk Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from alembic import command
from alembic.config import Config
from app.config.settings import settings
from app.config.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_alembic_config():
    """Membuat konfigurasi Alembic"""
    alembic_cfg = Config(str(root_dir / "alembic.ini"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    return alembic_cfg


def get_database_heads():
    """Dapatkan semua heads dari database"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            heads = [row[0] for row in result]
            return heads
    except Exception as e:
        logger.error(f"Error getting database heads: {str(e)}")
        return []


def fix_database_heads(target_revision: str = None):
    """Fix multiple heads di database dengan stamp ke target revision"""
    print("\n" + "=" * 80)
    print("FIX MULTIPLE HEADS DI DATABASE")
    print("=" * 80)
    
    # Get current heads
    current_heads = get_database_heads()
    
    if not current_heads:
        print("[OK] Database belum ada migration version")
        return True
    
    print(f"\nDitemukan {len(current_heads)} revision(s) di database:")
    for i, head in enumerate(current_heads, 1):
        print(f"  {i}. {head}")
    
    if len(current_heads) == 1:
        print("[OK] Hanya ada 1 revision, tidak perlu fix")
        return True
    
    # Jika tidak ada target, gunakan yang pertama (atau yang paling baru)
    if not target_revision:
        # Gunakan yang pertama sebagai default
        target_revision = current_heads[0]
        print(f"\n[INFO] Menggunakan revision pertama sebagai target: {target_revision}")
    
    print(f"\n[FIX] Membersihkan multiple heads...")
    print(f"      Target revision: {target_revision}")
    
    try:
        # Hapus semua rows dari alembic_version
        with engine.connect() as connection:
            connection.execute(text("DELETE FROM alembic_version"))
            connection.commit()
        
        # Stamp dengan target revision
        alembic_cfg = get_alembic_config()
        command.stamp(alembic_cfg, target_revision)
        
        print(f"[OK] Database berhasil di-stamp ke: {target_revision}")
        
        # Verify
        new_heads = get_database_heads()
        if len(new_heads) == 1 and new_heads[0] == target_revision:
            print(f"[OK] Verifikasi berhasil: database sekarang di revision {target_revision}")
            return True
        else:
            print(f"[WARNING] Verifikasi: database memiliki {len(new_heads)} revision(s)")
            return False
            
    except Exception as e:
        print(f"[ERROR] Gagal fix database heads: {str(e)}")
        logger.error(f"Error fixing database heads: {str(e)}", exc_info=True)
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix multiple heads di database")
    parser.add_argument(
        "--target", "-t",
        type=str,
        help="Target revision untuk stamp (default: revision pertama yang ditemukan)"
    )
    
    args = parser.parse_args()
    
    try:
        success = fix_database_heads(args.target)
        
        if success:
            print("\n" + "=" * 80)
            print("NEXT STEPS:")
            print("=" * 80)
            print("1. Database heads sudah dibersihkan")
            print("2. Jalankan migration:")
            print("   python -m scripts.smart_migrate --mode sequential")
            print("=" * 80 + "\n")
            sys.exit(0)
        else:
            print("\n[ERROR] Fix gagal, periksa error di atas")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Fix dibatalkan oleh user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n[ERROR] Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

