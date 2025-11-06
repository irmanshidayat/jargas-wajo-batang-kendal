"""
Script untuk menambahkan kolom project_id ke tabel stock_ins
jika belum ada (untuk memperbaiki error migration)
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text

def add_stock_ins_project_id():
    """Menambahkan kolom project_id yang hilang ke tabel stock_ins"""
    try:
        with engine.connect() as conn:
            # Check and add project_id to stock_ins table
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'stock_ins'
                AND COLUMN_NAME = 'project_id'
            """))
            
            if result.scalar() == 0:
                print("Menambahkan kolom project_id ke tabel stock_ins...")
                conn.execute(text("""
                    ALTER TABLE stock_ins 
                    ADD COLUMN project_id INT NULL
                """))
                conn.commit()
                print("✓ Kolom project_id berhasil ditambahkan ke tabel stock_ins")
                
                # Add index
                print("Menambahkan index untuk project_id di tabel stock_ins...")
                try:
                    conn.execute(text("""
                        CREATE INDEX ix_stock_ins_project_id ON stock_ins(project_id)
                    """))
                    conn.commit()
                    print("✓ Index ix_stock_ins_project_id berhasil ditambahkan")
                except Exception as idx_error:
                    error_msg = str(idx_error).lower()
                    if "duplicate" in error_msg or "already exists" in error_msg:
                        print("✓ Index ix_stock_ins_project_id sudah ada")
                    else:
                        print(f"⚠ Warning: Index gagal ditambahkan: {str(idx_error)}")
                        conn.rollback()
                
                # Check if projects table exists before adding foreign key
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'projects'
                """))
                
                if result.scalar() > 0:
                    print("Menambahkan foreign key constraint untuk project_id di tabel stock_ins...")
                    try:
                        conn.execute(text("""
                            ALTER TABLE stock_ins 
                            ADD CONSTRAINT fk_stock_ins_project_id 
                            FOREIGN KEY (project_id) REFERENCES projects(id)
                        """))
                        conn.commit()
                        print("✓ Foreign key constraint fk_stock_ins_project_id berhasil ditambahkan")
                    except Exception as fk_error:
                        error_msg = str(fk_error).lower()
                        if "duplicate" in error_msg or "already exists" in error_msg:
                            print("✓ Foreign key constraint fk_stock_ins_project_id sudah ada")
                        else:
                            print(f"⚠ Warning: Foreign key constraint gagal ditambahkan: {str(fk_error)}")
                        conn.rollback()
                else:
                    print("⚠ Tabel projects belum ada, melewatkan foreign key constraint")
            else:
                print("✓ Kolom project_id sudah ada di tabel stock_ins")
            
            print("\n✓ Kolom project_id di tabel stock_ins sudah tersedia")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Menambahkan kolom project_id ke tabel stock_ins")
    print("=" * 60)
    add_stock_ins_project_id()

