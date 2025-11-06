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
from app.config.database import SessionLocal
from app.config.pages_config import PAGES_CONFIG
from app.services.user.page_generator_service import PageGeneratorService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def auto_generate_pages():
    """Generate pages dan permissions dari configuration"""
    db: Session = SessionLocal()
    
    try:
        logger.info("Starting auto-generate pages and permissions...")
        
        generator = PageGeneratorService(db)
        stats = generator.generate_pages_from_config(PAGES_CONFIG)
        
        logger.info(
            f"Auto-generate completed successfully!\n"
            f"  - Created: {stats['created']} pages\n"
            f"  - Updated: {stats['updated']} pages\n"
            f"  - Skipped: {stats['skipped']} pages (custom display_name)"
        )
        
        return stats
    except Exception as e:
        logger.error(f"Error during auto-generate: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    auto_generate_pages()

