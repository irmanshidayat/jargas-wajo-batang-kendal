"""
Smart Migration Script dengan Best Practice Implementation
- Multi-mode support (sequential, head, auto)
- Auto-fix dependency cycle dengan dry-run dan confirmation
- Detailed migration history tracking
- Validasi sebelum upgrade

Penggunaan:
    python -m scripts.smart_migrate                    # Upgrade dengan mode default
    python -m scripts.smart_migrate --mode sequential    # Sequential mode
    python -m scripts.smart_migrate --mode head          # Head mode (fallback)
    python -m scripts.smart_migrate --mode auto           # Auto mode (smart selection)
    python -m scripts.smart_migrate --status              # Cek status migration
    python -m scripts.smart_migrate --validate           # Validasi migration chain
    python -m scripts.smart_migrate --fix-cycles         # Fix dependency cycles
    python -m scripts.smart_migrate --dry-run            # Simulate tanpa eksekusi
"""
import sys
import argparse
import io
from pathlib import Path

# Fix encoding untuk Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.utils.migration_manager import MigrationManager, MigrationMode
from app.config.settings import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_status(manager: MigrationManager):
    """Print migration status dengan format yang rapi"""
    status = manager.get_migration_status()
    
    print("\n" + "=" * 80)
    print("MIGRATION STATUS")
    print("=" * 80)
    print(f"Current Revision: {status.get('current_revision') or 'None (database baru)'}")
    print(f"Head Revision:    {status.get('head_revision') or 'Tidak ditemukan'}")
    print(f"Mode:             {status.get('mode', 'N/A')}")
    # Use ASCII-safe characters for Windows compatibility
    up_to_date = status.get('is_up_to_date')
    has_pending = status.get('has_pending')
    print(f"Up-to-date:       {'[OK] Ya' if up_to_date else '[NO] Tidak'}")
    print(f"Has Pending:      {'[YES] Ya' if has_pending else '[NO] Tidak'}")
    
    # Multiple heads
    if status.get('multiple_heads'):
        print(f"\n[WARNING] MULTIPLE HEADS DETECTED:")
        for head in status.get('heads', []):
            print(f"   - {head}")
    else:
        print(f"Multiple Heads:   [NO] Tidak")
    
    # Cycles
    if status.get('has_cycles'):
        print(f"\n[WARNING] CYCLES DETECTED:")
        for cycle in status.get('cycles', []):
            print(f"   {' -> '.join(cycle)} -> {cycle[0]}")
    else:
        print(f"Cycles:           [NO] Tidak")
    
    # Validation
    if status.get('is_valid'):
        print(f"Validation:       [OK] Valid")
    else:
        print(f"\n[ERROR] VALIDATION ERRORS:")
        for error in status.get('validation_errors', []):
            print(f"   - {error}")
    
    print("=" * 80 + "\n")


def print_migration_path(manager: MigrationManager):
    """Print sequential migration path"""
    current = manager.get_current_revision()
    path = manager.get_sequential_path(current)
    
    if not path:
        print("Tidak ada migration path yang ditemukan")
        return
    
    print("\n" + "=" * 80)
    print("SEQUENTIAL MIGRATION PATH")
    print("=" * 80)
    print(f"From: {current or 'None (database baru)'}")
    print(f"To:   {manager.get_head_revision()}")
    print(f"\nPath ({len(path)} migration(s)):")
    for i, rev in enumerate(path, 1):
        print(f"  {i}. {rev}")
    print("=" * 80 + "\n")


def fix_cycles_interactive(manager: MigrationManager):
    """Fix dependency cycles dengan interactive confirmation"""
    cycles = manager.detect_cycles()
    
    if not cycles:
        print("[OK] Tidak ada cycle yang terdeteksi")
        return
    
    print("\n" + "=" * 80)
    print("DEPENDENCY CYCLE DETECTION")
    print("=" * 80)
    print(f"Ditemukan {len(cycles)} cycle(s):\n")
    
    for i, cycle in enumerate(cycles, 1):
        print(f"Cycle {i}: {' -> '.join(cycle)} -> {cycle[0]}")
    
    suggestions = manager.suggest_cycle_fix(cycles)
    
    if not suggestions:
        print("\n⚠️  Tidak ada saran perbaikan yang dapat dihasilkan")
        print("   Perlu perbaikan manual pada migration files")
        return
    
    print("\n" + "=" * 80)
    print("SUGGESTED FIXES")
    print("=" * 80)
    for rev, new_down in suggestions.items():
        migrations = manager.parse_migration_files()
        old_down = migrations[rev].down_revision if rev in migrations else None
        print(f"\nRevision: {rev}")
        print(f"  Current down_revision: {old_down or 'None'}")
        print(f"  Suggested down_revision: {new_down or 'None'}")
    
    print("\n" + "=" * 80)
    response = input("Apakah Anda ingin menerapkan perbaikan ini? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("Perbaikan dibatalkan")
        return
    
    # Apply fixes (dry-run dulu)
    print("\n⚠️  PERHATIAN: Fitur auto-fix akan mengubah file migration!")
    print("   Pastikan Anda sudah commit perubahan sebelumnya")
    response2 = input("Lanjutkan? (yes/no): ").strip().lower()
    
    if response2 not in ['yes', 'y']:
        print("Perbaikan dibatalkan")
        return
    
    # TODO: Implement actual file modification
    # Untuk sekarang, hanya print suggestion
    print("\n⚠️  Fitur auto-fix file modification belum diimplementasikan")
    print("   Silakan edit file migration secara manual berdasarkan suggestion di atas")
    print("\n   File yang perlu diubah:")
    migrations = manager.parse_migration_files()
    for rev in suggestions.keys():
        if rev in migrations:
            print(f"   - {migrations[rev].file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Smart Migration Script dengan Best Practice",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python -m scripts.smart_migrate                    # Upgrade dengan mode default
  python -m scripts.smart_migrate --mode sequential  # Sequential mode (recommended)
  python -m scripts.smart_migrate --mode head         # Head mode (fallback)
  python -m scripts.smart_migrate --status           # Cek status
  python -m scripts.smart_migrate --validate         # Validasi chain
  python -m scripts.smart_migrate --fix-cycles       # Fix cycles
  python -m scripts.smart_migrate --dry-run           # Simulate
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["sequential", "head", "auto"],
        default=None,
        help="Migration mode (default: dari settings.MIGRATION_MODE)"
    )
    
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Tampilkan status migration"
    )
    
    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Validasi migration chain"
    )
    
    parser.add_argument(
        "--fix-cycles", "-f",
        action="store_true",
        help="Deteksi dan fix dependency cycles"
    )
    
    parser.add_argument(
        "--path", "-p",
        action="store_true",
        help="Tampilkan sequential migration path"
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Simulate migration tanpa eksekusi"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    mode = None
    if args.mode:
        mode = MigrationMode(args.mode)
    else:
        mode_str = settings.MIGRATION_MODE or "sequential"
        mode = MigrationMode(mode_str)
    
    # Create manager
    manager = MigrationManager(mode=mode)
    
    try:
        # Status command
        if args.status:
            print_status(manager)
            return
        
        # Validate command
        if args.validate:
            is_valid, errors = manager.validate_migration_chain()
            print("\n" + "=" * 80)
            print("MIGRATION CHAIN VALIDATION")
            print("=" * 80)
            if is_valid:
                print("[OK] Migration chain valid")
            else:
                print("[ERROR] Migration chain memiliki masalah:")
                for error in errors:
                    print(f"   - {error}")
            print("=" * 80 + "\n")
            return
        
        # Fix cycles command
        if args.fix_cycles:
            fix_cycles_interactive(manager)
            return
        
        # Path command
        if args.path:
            print_migration_path(manager)
            return
        
        # Upgrade command (default)
        print(f"\n🔄 Starting migration dengan mode: {mode.value}")
        if args.dry_run:
            print("🔍 DRY-RUN MODE: Tidak akan mengubah database\n")
        
        # Show status sebelum upgrade
        print_status(manager)
        
        # Execute upgrade
        result = manager.upgrade(mode=mode, dry_run=args.dry_run)
        
        # Print result
        print("\n" + "=" * 80)
        print("MIGRATION RESULT")
        print("=" * 80)
        print(f"Success:  {'[OK] Ya' if result.get('success') else '[FAIL] Tidak'}")
        print(f"Mode:     {result.get('mode', 'N/A')}")
        print(f"Message:  {result.get('message', 'N/A')}")
        
        if result.get('applied'):
            print(f"\nApplied migrations ({len(result['applied'])}):")
            for rev in result['applied']:
                print(f"  [OK] {rev}")
        
        if result.get('failed'):
            print(f"\nFailed migrations ({len(result['failed'])}):")
            for fail in result['failed']:
                print(f"  [FAIL] {fail.get('revision', 'N/A')}: {fail.get('error', 'N/A')}")
        
        if result.get('errors'):
            print(f"\nErrors:")
            for error in result['errors']:
                print(f"  [ERROR] {error}")
        
        if result.get('final_revision'):
            print(f"\nFinal Revision: {result['final_revision']}")
        
        print("=" * 80 + "\n")
        
        # Show status setelah upgrade
        if not args.dry_run and result.get('success'):
            print_status(manager)
        
        # Exit code
        sys.exit(0 if result.get('success') else 1)
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Migration dibatalkan oleh user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n[ERROR] Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

