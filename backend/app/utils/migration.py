"""
Utility untuk menjalankan migrasi database secara programmatic
Menggunakan Migration Manager dengan best practice implementation
"""
import logging
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.config.settings import settings
from app.config.database import engine
from app.utils.migration_manager import MigrationManager, MigrationMode

logger = logging.getLogger(__name__)

def get_alembic_config():
    """Membuat konfigurasi Alembic"""
    root_dir = Path(__file__).parent.parent.parent
    alembic_cfg = Config(str(root_dir / "alembic.ini"))
    
    # Override sqlalchemy.url dari settings
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    
    return alembic_cfg

def run_migrations_upgrade(revision: str = "head") -> bool:
    """
    Jalankan upgrade migration
    
    Args:
        revision: Revision ID untuk upgrade (default: "head")
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        alembic_cfg = get_alembic_config()
        logger.info(f"Menjalankan upgrade migration ke: {revision}")
        command.upgrade(alembic_cfg, revision)
        logger.info("Migration upgrade berhasil")
        return True
    except Exception as e:
        logger.error(f"Error saat upgrade migration: {str(e)}", exc_info=True)
        return False

def run_migrations_downgrade(revision: str) -> bool:
    """
    Jalankan downgrade migration
    
    Args:
        revision: Revision ID untuk downgrade
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        alembic_cfg = get_alembic_config()
        logger.info(f"Menjalankan downgrade migration ke: {revision}")
        command.downgrade(alembic_cfg, revision)
        logger.info("Migration downgrade berhasil")
        return True
    except Exception as e:
        logger.error(f"Error saat downgrade migration: {str(e)}", exc_info=True)
        return False

def get_current_revision() -> str:
    """
    Dapatkan revision saat ini dari database
    
    Returns:
        str: Revision ID saat ini, atau None jika error
    """
    try:
        alembic_cfg = get_alembic_config()
        from alembic.runtime.migration import MigrationContext
        from app.config.database import engine
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            return current_rev
    except Exception as e:
        logger.error(f"Error saat mendapatkan current revision: {str(e)}", exc_info=True)
        return None

def check_migrations_pending() -> bool:
    """
    Cek apakah ada migration yang pending
    
    Returns:
        bool: True jika ada migration pending, False jika sudah up-to-date
    """
    try:
        alembic_cfg = get_alembic_config()
        from alembic.script import ScriptDirectory
        
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        current_rev = get_current_revision()
        head_rev = script_dir.get_current_head()
        
        return current_rev != head_rev
    except Exception as e:
        logger.error(f"Error saat mengecek pending migrations: {str(e)}", exc_info=True)
        return False

def get_migration_info() -> dict:
    """
    Dapatkan informasi lengkap tentang migration status
    
    Returns:
        dict: Dictionary dengan info current_revision, head_revision, dan pending
    """
    try:
        alembic_cfg = get_alembic_config()
        from alembic.script import ScriptDirectory
        
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        current_rev = get_current_revision()
        head_rev = script_dir.get_current_head()
        
        return {
            "current_revision": current_rev,
            "head_revision": head_rev,
            "is_pending": current_rev != head_rev,
            "is_up_to_date": current_rev == head_rev
        }
    except Exception as e:
        logger.error(f"Error saat mendapatkan migration info: {str(e)}", exc_info=True)
        return {
            "current_revision": None,
            "head_revision": None,
            "is_pending": False,
            "is_up_to_date": False,
            "error": str(e)
        }

def check_database_empty() -> bool:
    """
    Cek apakah database kosong (tidak ada tabel sama sekali atau tidak ada tabel alembic_version)
    
    Returns:
        bool: True jika database kosong, False jika sudah ada tabel
    """
    try:
        with engine.connect() as connection:
            # Cek apakah ada tabel alembic_version
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Jika tidak ada tabel sama sekali, database kosong
            if len(tables) == 0:
                logger.info("Database kosong: tidak ada tabel sama sekali")
                return True
            
            # Jika ada tabel tapi tidak ada alembic_version, berarti belum pernah migration
            if "alembic_version" not in tables:
                logger.info("Database kosong: tidak ada tabel alembic_version (belum pernah migration)")
                return True
            
            # Cek apakah tabel alembic_version ada tapi kosong
            try:
                result = connection.execute(text("SELECT COUNT(*) as count FROM alembic_version"))
                row = result.fetchone()
                if row and row[0] == 0:
                    logger.info("Database kosong: tabel alembic_version ada tapi kosong")
                    return True
            except (OperationalError, ProgrammingError) as e:
                # Jika error saat query alembic_version, anggap database kosong
                logger.warning(f"Error saat cek alembic_version: {str(e)}, anggap database kosong")
                return True
            
            # Database tidak kosong
            return False
            
    except (OperationalError, ProgrammingError) as e:
        # Error koneksi atau database tidak ada
        error_msg = str(e).lower()
        if "doesn't exist" in error_msg or "unknown database" in error_msg:
            logger.warning(f"Database {settings.DB_NAME} belum ada: {str(e)}")
        else:
            logger.warning(f"Error saat cek database empty: {str(e)}")
        # Anggap database kosong jika error
        return True
    except Exception as e:
        logger.error(f"Unexpected error saat cek database empty: {str(e)}", exc_info=True)
        # Anggap database kosong jika error
        return True

def auto_migrate_safe(only_if_pending: bool = True) -> dict:
    """
    Jalankan auto-migrate dengan validasi dan safety checks (Best Practice)
    Menggunakan Migration Manager baru dengan sequential mode sebagai default
    
    Args:
        only_if_pending: Jika True, hanya migrate jika ada pending migration
                        TAPI akan di-ignore jika database kosong (force migration)
    
    Returns:
        dict: Status hasil migration dengan detail
    """
    try:
        # Cek apakah database kosong terlebih dahulu
        is_database_empty = check_database_empty()
        
        # Jika database kosong, force migration meskipun only_if_pending=True
        if is_database_empty:
            logger.info("🔍 Database kosong terdeteksi, akan melakukan initial migration...")
            only_if_pending = False  # Override untuk force migration
        
        # Gunakan Migration Manager baru
        manager = MigrationManager()
        
        # Get migration status
        status = manager.get_migration_status()
        
        result = {
            "success": False,
            "migrated": False,
            "message": "",
            "current_revision": status.get("current_revision"),
            "head_revision": status.get("head_revision"),
            "error": None,
            "mode": manager.mode.value,
            "is_database_empty": is_database_empty
        }
        
        # Cek apakah sudah up-to-date
        if status.get("is_up_to_date") and not is_database_empty:
            result["success"] = True
            result["migrated"] = False
            result["message"] = "Database sudah up-to-date, tidak ada migration yang perlu dijalankan"
            logger.info(f"Database sudah up-to-date (revision: {result['current_revision']})")
            return result
        
        # Jika only_if_pending=True dan tidak ada pending, skip (kecuali database kosong)
        if only_if_pending and not status.get("has_pending") and not is_database_empty:
            result["success"] = True
            result["migrated"] = False
            result["message"] = "Tidak ada pending migration"
            logger.info("Tidak ada pending migration, skip auto-migrate")
            return result
        
        # Jika database kosong atau ada pending, jalankan migration
        if is_database_empty:
            logger.info(f"🚀 Memulai initial migration ke {result['head_revision']} (mode: {manager.mode.value})")
        else:
            logger.info(f"🔄 Memulai auto-migration dari {result['current_revision']} ke {result['head_revision']} (mode: {manager.mode.value})")
        
        upgrade_result = manager.upgrade()
        
        # Map result dari manager ke format yang diharapkan
        result["success"] = upgrade_result.get("success", False)
        result["migrated"] = upgrade_result.get("success", False) and len(upgrade_result.get("applied", [])) > 0
        result["message"] = upgrade_result.get("message", "")
        result["current_revision"] = upgrade_result.get("final_revision") or upgrade_result.get("current_revision")
        
        if upgrade_result.get("errors"):
            result["error"] = "; ".join(upgrade_result["errors"])
        
        if result["migrated"]:
            if is_database_empty:
                logger.info(f"✅ Initial migration berhasil: {result['message']}")
            else:
                logger.info(f"✅ Auto-migration berhasil: {result['message']}")
        else:
            logger.warning(f"⚠️ {result['message']}")
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error saat auto-migrate: {error_msg}", exc_info=True)
        return {
            "success": False,
            "migrated": False,
            "message": f"Error saat auto-migrate: {error_msg}",
            "current_revision": None,
            "head_revision": None,
            "error": error_msg,
            "is_database_empty": False
        }

