"""
Script untuk menambahkan kolom quantity_kondisi_baik dan quantity_kondisi_reject
ke tabel returns di database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import settings
from app.config.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_columns():
    """Menambahkan kolom quantity_kondisi_baik dan quantity_kondisi_reject"""
    
    sql_queries = [
        "ALTER TABLE returns ADD COLUMN quantity_kondisi_baik INT DEFAULT 0",
        "ALTER TABLE returns ADD COLUMN quantity_kondisi_reject INT DEFAULT 0",
    ]
    
    try:
        with engine.connect() as connection:
            for sql in sql_queries:
                try:
                    logger.info(f"Executing: {sql}")
                    connection.execute(text(sql))
                    connection.commit()
                    logger.info("✓ Success")
                except Exception as e:
                    error_msg = str(e)
                    if "Duplicate column name" in error_msg or "already exists" in error_msg.lower():
                        logger.warning(f"⚠ Column already exists, skipping: {error_msg}")
                    else:
                        logger.error(f"✗ Error: {error_msg}")
                        raise
            
            logger.info("\n✅ Migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"\n✗ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Running migration: Add quantity_kondisi_baik and quantity_kondisi_reject")
    print(f"Database: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print("=" * 60)
    print()
    
    success = add_columns()
    
    if success:
        print("\n✅ Kolom berhasil ditambahkan!")
        print("Silakan restart backend server jika perlu.")
    else:
        print("\n❌ Gagal menambahkan kolom. Cek error di atas.")
        sys.exit(1)

