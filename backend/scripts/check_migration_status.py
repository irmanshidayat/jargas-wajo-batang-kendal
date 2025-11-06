"""
Script untuk mengecek status migration database
Penggunaan: python -m scripts.check_migration_status
"""
import sys
import os
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.utils.migration import get_migration_info, get_current_revision
from app.config.settings import settings

def main():
    print("=" * 80)
    print("CEK STATUS MIGRATION DATABASE")
    print("=" * 80)
    print(f"Database: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print()
    
    try:
        # Get migration info
        info = get_migration_info()
        
        if info.get("error"):
            print(f"❌ ERROR: {info['error']}")
            return
        
        current = info.get("current_revision") or "Tidak ada migration (database baru)"
        head = info.get("head_revision") or "Tidak ada migration files"
        is_pending = info.get("is_pending", False)
        is_up_to_date = info.get("is_up_to_date", False)
        
        print(f"📌 Current Revision: {current}")
        print(f"🎯 Head Revision: {head}")
        print()
        
        if is_up_to_date:
            print("✅ Status: Database UP-TO-DATE")
            print("   Tidak ada migration yang perlu dijalankan")
        elif is_pending:
            print("⚠️  Status: Ada PENDING MIGRATION")
            print(f"   Perlu upgrade dari {current} ke {head}")
            print()
            print("   Untuk menjalankan migration:")
            print("   - python -m scripts.migrate_cli upgrade")
            print("   - python -m scripts.run_migrations")
        else:
            print("⚠️  Status: UNKNOWN")
            print("   Periksa koneksi database dan migration files")
        
        print()
        print("=" * 80)
        print("Auto-Migrate Configuration:")
        print(f"  AUTO_MIGRATE: {settings.AUTO_MIGRATE}")
        print(f"  AUTO_MIGRATE_ONLY_IF_PENDING: {settings.AUTO_MIGRATE_ONLY_IF_PENDING}")
        if not settings.AUTO_MIGRATE:
            print()
            print("  💡 Untuk mengaktifkan auto-migrate, tambahkan di .env:")
            print("     AUTO_MIGRATE=true")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

