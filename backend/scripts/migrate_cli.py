"""
CLI sederhana untuk menjalankan migrasi database
Alternatif yang lebih sederhana dari run_migrations.py

Penggunaan:
    python -m scripts.migrate_cli upgrade          # Upgrade ke head
    python -m scripts.migrate_cli upgrade <rev>    # Upgrade ke revision tertentu
    python -m scripts.migrate_cli downgrade <rev>  # Downgrade ke revision
    python -m scripts.migrate_cli current          # Show current version
    python -m scripts.migrate_cli history          # Show history
"""
import sys
import os
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
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    return alembic_cfg

def main():
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python -m scripts.migrate_cli upgrade [revision]")
        print("  python -m scripts.migrate_cli downgrade <revision>")
        print("  python -m scripts.migrate_cli current")
        print("  python -m scripts.migrate_cli history")
        sys.exit(1)
    
    command_name = sys.argv[1]
    alembic_cfg = get_alembic_config()
    
    try:
        if command_name == "upgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            print(f"🔄 Upgrading database ke: {revision}")
            command.upgrade(alembic_cfg, revision)
            print("✅ Upgrade berhasil!")
        
        elif command_name == "downgrade":
            if len(sys.argv) < 3:
                print("❌ Error: Downgrade memerlukan revision")
                sys.exit(1)
            revision = sys.argv[2]
            print(f"🔄 Downgrading database ke: {revision}")
            command.downgrade(alembic_cfg, revision)
            print("✅ Downgrade berhasil!")
        
        elif command_name == "current":
            print("📌 Current migration version:")
            command.current(alembic_cfg)
        
        elif command_name == "history":
            print("📜 Migration history:")
            command.history(alembic_cfg)
        
        else:
            print(f"❌ Command tidak dikenal: {command_name}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

