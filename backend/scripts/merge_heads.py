"""
Script untuk merge multiple heads secara otomatis
"""
import sys
import io
from pathlib import Path
from datetime import datetime

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
from app.utils.migration_manager import MigrationManager
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


def merge_heads_automatic():
    """Merge multiple heads secara otomatis"""
    print("\n" + "=" * 80)
    print("MERGE MULTIPLE HEADS")
    print("=" * 80)
    
    manager = MigrationManager()
    status = manager.get_migration_status()
    
    if not status.get('multiple_heads'):
        print("[OK] Tidak ada multiple heads, tidak perlu merge")
        return True
    
    heads = status.get('heads', [])
    print(f"\nDitemukan {len(heads)} head(s):")
    for i, head in enumerate(heads, 1):
        print(f"  {i}. {head}")
    
    # Extract revision IDs dari heads (format bisa berbeda)
    head_revisions = []
    for head in heads:
        # Head format bisa: "c4f470eb2d52 -> 6d338d47c23b (head), convert_quantity_to_decimal"
        # Atau: "309b15867534 -> add_status_surat_permintaan (head), add_status_to_surat_permintaan_and_nomor_to_surat_jalan"
        # Ambil yang terakhir (head revision)
        if "->" in head:
            parts = head.split("->")
            if len(parts) > 1:
                last_part = parts[-1].strip()
                # Extract revision ID (sebelum " (head)")
                if " (head)" in last_part:
                    rev = last_part.split(" (head)")[0].strip()
                else:
                    rev = last_part.split(",")[0].strip()
                head_revisions.append(rev)
        else:
            head_revisions.append(head.strip())
    
    if len(head_revisions) < 2:
        print("[ERROR] Tidak cukup heads untuk merge")
        return False
    
    print(f"\nHead revisions yang akan di-merge:")
    for rev in head_revisions:
        print(f"  - {rev}")
    
    # Buat merge migration
    alembic_cfg = get_alembic_config()
    merge_message = f"merge_heads_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        print(f"\n[MERGE] Membuat merge migration: {merge_message}")
        print(f"        Merging: {' '.join(head_revisions)}")
        
        command.merge(
            alembic_cfg,
            head_revisions,
            message=merge_message
        )
        
        print("[OK] Merge migration berhasil dibuat!")
        print("\n[INFO] Merge migration file telah dibuat di migrations/versions/")
        print("       Silakan review file tersebut sebelum menjalankan migration")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Gagal membuat merge migration: {str(e)}")
        logger.error(f"Error merging heads: {str(e)}", exc_info=True)
        return False


def main():
    try:
        success = merge_heads_automatic()
        
        if success:
            print("\n" + "=" * 80)
            print("NEXT STEPS:")
            print("=" * 80)
            print("1. Review merge migration file di migrations/versions/")
            print("2. Jalankan migration:")
            print("   python -m scripts.smart_migrate --mode sequential")
            print("=" * 80 + "\n")
            sys.exit(0)
        else:
            print("\n[ERROR] Merge gagal, periksa error di atas")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Merge dibatalkan oleh user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n[ERROR] Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

