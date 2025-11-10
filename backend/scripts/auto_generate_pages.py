"""
Script untuk auto-generate pages dan permissions dari configuration.
Script ini dipanggil saat backend startup.
Jalankan manual dengan: python -m scripts.auto_generate_pages
"""

import sys
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from app.config.database import SessionLocal, engine
from app.config.settings import settings
from app.config.pages_config import PAGES_CONFIG
from app.services.user.page_generator_service import PageGeneratorService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_database_connection() -> bool:
    """
    Test koneksi database sebelum menjalankan auto-generate.
    Returns True jika koneksi berhasil, False jika gagal.
    """
    try:
        # Test koneksi dengan engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test: OK")
        return True
    except OperationalError as e:
        error_msg = str(e)
        if "Access denied" in error_msg or "1045" in error_msg:
            logger.error(
                f"❌ Database connection failed: Access denied\n"
                f"   Periksa kredensial database di file .env:\n"
                f"   - DB_HOST={settings.DB_HOST}\n"
                f"   - DB_USER={settings.DB_USER}\n"
                f"   - DB_PASSWORD={'***' if settings.DB_PASSWORD else '(kosong)'}\n"
                f"   - DB_NAME={settings.DB_NAME}\n"
                f"   Pastikan password MySQL sesuai dengan yang di .env"
            )
        elif "Can't connect" in error_msg or "2003" in error_msg:
            logger.error(
                f"❌ Database connection failed: Cannot connect to MySQL server\n"
                f"   Periksa:\n"
                f"   - MySQL/XAMPP sudah berjalan?\n"
                f"   - DB_HOST={settings.DB_HOST} benar?\n"
                f"   - DB_PORT={settings.DB_PORT} benar?"
            )
        else:
            logger.error(f"❌ Database connection failed: {error_msg}")
        return False
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {str(e)}")
        return False


def auto_generate_pages():
    """Generate pages dan permissions dari configuration"""
    # Test koneksi database terlebih dahulu
    if not test_database_connection():
        raise ConnectionError(
            "Database connection failed. Periksa konfigurasi database di file .env"
        )
    
    db: Session = SessionLocal()
    
    try:
        logger.info("Starting auto-generate pages and permissions...")
        
        generator = PageGeneratorService(db)
        stats = generator.generate_pages_from_config(PAGES_CONFIG)
        
        logger.info(
            f"✅ Auto-generate completed successfully!\n"
            f"   - Created: {stats['created']} pages\n"
            f"   - Updated: {stats['updated']} pages\n"
            f"   - Skipped: {stats['skipped']} pages (custom display_name)"
        )
        
        return stats
    except OperationalError as e:
        error_msg = str(e)
        if "Access denied" in error_msg or "1045" in error_msg:
            logger.error(
                f"❌ Database access denied during auto-generate\n"
                f"   Periksa kredensial database di file .env"
            )
        else:
            logger.error(f"❌ Database error during auto-generate: {error_msg}")
        raise
    except Exception as e:
        logger.error(f"❌ Error during auto-generate: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    auto_generate_pages()

