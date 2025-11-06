"""
Script untuk menambahkan kolom project_id ke tabel materials dan audit_logs
jika belum ada (untuk memperbaiki error migration)
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text

def add_project_id_columns():
    """Menambahkan kolom project_id yang hilang ke tabel materials dan audit_logs"""
    try:
        with engine.connect() as conn:
            # Check and add project_id to materials table
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'materials'
                AND COLUMN_NAME = 'project_id'
            """))
            
            if result.scalar() == 0:
                print("Menambahkan kolom project_id ke tabel materials...")
                conn.execute(text("""
                    ALTER TABLE materials 
                    ADD COLUMN project_id INT NULL
                """))
                conn.commit()
                print("✓ Kolom project_id berhasil ditambahkan ke tabel materials")
                
                # Add index
                print("Menambahkan index untuk project_id di tabel materials...")
                conn.execute(text("""
                    CREATE INDEX ix_materials_project_id ON materials(project_id)
                """))
                conn.commit()
                print("✓ Index ix_materials_project_id berhasil ditambahkan")
                
                # Check if projects table exists before adding foreign key
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'projects'
                """))
                
                if result.scalar() > 0:
                    print("Menambahkan foreign key constraint untuk project_id di tabel materials...")
                    try:
                        conn.execute(text("""
                            ALTER TABLE materials 
                            ADD CONSTRAINT fk_materials_project_id 
                            FOREIGN KEY (project_id) REFERENCES projects(id)
                        """))
                        conn.commit()
                        print("✓ Foreign key constraint fk_materials_project_id berhasil ditambahkan")
                    except Exception as fk_error:
                        print(f"⚠ Warning: Foreign key constraint gagal ditambahkan: {str(fk_error)}")
                        conn.rollback()
                else:
                    print("⚠ Tabel projects belum ada, melewatkan foreign key constraint")
            else:
                print("✓ Kolom project_id sudah ada di tabel materials")
            
            # Check and add project_id to audit_logs table
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'audit_logs'
                AND COLUMN_NAME = 'project_id'
            """))
            
            if result.scalar() == 0:
                print("\nMenambahkan kolom project_id ke tabel audit_logs...")
                conn.execute(text("""
                    ALTER TABLE audit_logs 
                    ADD COLUMN project_id INT NULL
                """))
                conn.commit()
                print("✓ Kolom project_id berhasil ditambahkan ke tabel audit_logs")
                
                # Add index
                print("Menambahkan index untuk project_id di tabel audit_logs...")
                conn.execute(text("""
                    CREATE INDEX ix_audit_logs_project_id ON audit_logs(project_id)
                """))
                conn.commit()
                print("✓ Index ix_audit_logs_project_id berhasil ditambahkan")
                
                # Check if projects table exists before adding foreign key
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'projects'
                """))
                
                if result.scalar() > 0:
                    print("Menambahkan foreign key constraint untuk project_id di tabel audit_logs...")
                    try:
                        conn.execute(text("""
                            ALTER TABLE audit_logs 
                            ADD CONSTRAINT fk_audit_logs_project_id 
                            FOREIGN KEY (project_id) REFERENCES projects(id)
                        """))
                        conn.commit()
                        print("✓ Foreign key constraint fk_audit_logs_project_id berhasil ditambahkan")
                    except Exception as fk_error:
                        print(f"⚠ Warning: Foreign key constraint gagal ditambahkan: {str(fk_error)}")
                        conn.rollback()
                else:
                    print("⚠ Tabel projects belum ada, melewatkan foreign key constraint")
            else:
                print("✓ Kolom project_id sudah ada di tabel audit_logs")
            
            print("\n✓ Semua kolom project_id sudah tersedia")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    add_project_id_columns()

