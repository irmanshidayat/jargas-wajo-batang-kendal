"""
Script untuk membuat tabel surat_jalans dan surat_jalan_items secara manual
Jalankan jika migration cycle tidak bisa diperbaiki
"""
import sys
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import text
from app.config.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create surat_jalans and surat_jalan_items tables"""
    try:
        with engine.connect() as conn:
            # Check if tables already exist
            result = conn.execute(text("SHOW TABLES LIKE 'surat_jalan%'"))
            existing_tables = [row[0] for row in result]
            
            if 'surat_jalans' in existing_tables:
                logger.info("Table surat_jalans already exists")
                return
            
            logger.info("Creating surat_jalans table...")
            conn.execute(text("""
                CREATE TABLE surat_jalans (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nomor_form VARCHAR(255) NOT NULL UNIQUE,
                    kepada VARCHAR(255) NOT NULL,
                    tanggal_pengiriman DATE NOT NULL,
                    nama_pemberi VARCHAR(255) NULL,
                    nama_penerima VARCHAR(255) NULL,
                    tanggal_diterima DATE NULL,
                    project_id INT NOT NULL,
                    created_by INT NOT NULL,
                    updated_by INT NULL,
                    deleted_by INT NULL,
                    is_deleted INT NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX ix_surat_jalans_id (id),
                    INDEX ix_surat_jalans_nomor_form (nomor_form),
                    INDEX ix_surat_jalans_tanggal_pengiriman (tanggal_pengiriman),
                    INDEX ix_surat_jalans_project_id (project_id),
                    INDEX ix_surat_jalans_is_deleted (is_deleted),
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    FOREIGN KEY (updated_by) REFERENCES users(id),
                    FOREIGN KEY (deleted_by) REFERENCES users(id),
                    UNIQUE KEY uq_surat_jalan_nomor_form (nomor_form)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            logger.info("Creating surat_jalan_items table...")
            conn.execute(text("""
                CREATE TABLE surat_jalan_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    surat_jalan_id INT NOT NULL,
                    nama_barang VARCHAR(255) NOT NULL,
                    qty DECIMAL(10, 2) NOT NULL,
                    keterangan TEXT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX ix_surat_jalan_items_id (id),
                    INDEX ix_surat_jalan_items_surat_jalan_id (surat_jalan_id),
                    FOREIGN KEY (surat_jalan_id) REFERENCES surat_jalans(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            conn.commit()
            logger.info("✅ Tables created successfully!")
            
    except Exception as e:
        logger.error(f"❌ Error creating tables: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    create_tables()

