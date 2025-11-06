"""
Script untuk memastikan project_id di materials menjadi NOT NULL
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text

def make_materials_project_id_not_null():
    """Memastikan project_id di materials menjadi NOT NULL"""
    try:
        with engine.connect() as conn:
            print("Memastikan project_id di materials menjadi NOT NULL...")
            
            # Cek apakah kolom masih nullable
            result = conn.execute(text("""
                SELECT IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'materials'
                AND COLUMN_NAME = 'project_id'
            """))
            
            column_info = result.fetchone()
            if column_info and column_info[0] == 'YES':
                # Cek apakah masih ada data NULL
                result = conn.execute(text("SELECT COUNT(*) FROM materials WHERE project_id IS NULL"))
                null_count = result.scalar()
                
                if null_count > 0:
                    print(f"⚠ Masih ada {null_count} record dengan project_id NULL, memperbaiki...")
                    
                    # Dapatkan default project
                    result = conn.execute(text("SELECT id FROM projects ORDER BY id LIMIT 1"))
                    default_project = result.fetchone()
                    
                    if default_project:
                        default_project_id = default_project[0]
                        conn.execute(text("""
                            UPDATE materials 
                            SET project_id = :project_id 
                            WHERE project_id IS NULL
                        """), {"project_id": default_project_id})
                        conn.commit()
                        print(f"✓ {null_count} record berhasil diupdate ke project_id {default_project_id}")
                    else:
                        print("❌ Tidak ada project di database, tidak bisa memperbaiki")
                        return False
                
                # Ubah menjadi NOT NULL
                print("Mengubah project_id menjadi NOT NULL...")
                conn.execute(text("""
                    ALTER TABLE materials
                    MODIFY COLUMN project_id INT NOT NULL
                """))
                conn.commit()
                print("✓ Kolom project_id berhasil diubah menjadi NOT NULL")
            else:
                print("✓ Kolom project_id sudah NOT NULL")
            
            print("\n✓ Selesai!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    make_materials_project_id_not_null()

