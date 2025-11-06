"""
Script untuk menambahkan kolom surat_permohonan_paths dan surat_serah_terima_paths 
ke tabel stock_outs jika belum ada
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text

def add_columns():
    """Menambahkan kolom yang hilang ke tabel stock_outs"""
    try:
        with engine.connect() as conn:
            # Check if column exists and add if not
            # MySQL doesn't support IF NOT EXISTS in ALTER TABLE, so we need to check first
            
            # Check surat_permohonan_paths
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'stock_outs'
                AND COLUMN_NAME = 'surat_permohonan_paths'
            """))
            
            if result.scalar() == 0:
                print("Menambahkan kolom surat_permohonan_paths...")
                conn.execute(text("""
                    ALTER TABLE stock_outs 
                    ADD COLUMN surat_permohonan_paths TEXT NULL
                """))
                conn.commit()
                print("✓ Kolom surat_permohonan_paths berhasil ditambahkan")
            else:
                print("✓ Kolom surat_permohonan_paths sudah ada")
            
            # Check surat_serah_terima_paths
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'stock_outs'
                AND COLUMN_NAME = 'surat_serah_terima_paths'
            """))
            
            if result.scalar() == 0:
                print("Menambahkan kolom surat_serah_terima_paths...")
                conn.execute(text("""
                    ALTER TABLE stock_outs 
                    ADD COLUMN surat_serah_terima_paths TEXT NULL
                """))
                conn.commit()
                print("✓ Kolom surat_serah_terima_paths berhasil ditambahkan")
            else:
                print("✓ Kolom surat_serah_terima_paths sudah ada")
            
            print("\n✓ Semua kolom sudah tersedia di tabel stock_outs")
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    add_columns()

