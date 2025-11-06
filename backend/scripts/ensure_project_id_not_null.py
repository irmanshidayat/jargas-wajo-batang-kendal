"""
Script untuk memastikan semua data existing punya project_id dan ubah kolom menjadi NOT NULL
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text

def ensure_project_id_not_null():
    """Memastikan semua data punya project_id dan kolom menjadi NOT NULL"""
    try:
        with engine.connect() as conn:
            print("Memastikan semua data existing punya project_id...")
            
            # Step 1: Buat atau dapatkan default project
            result = conn.execute(text("SELECT id FROM projects WHERE code = 'DEFAULT' LIMIT 1"))
            default_project = result.fetchone()
            
            if not default_project:
                print("Membuat default project...")
                conn.execute(text("""
                    INSERT INTO projects (name, code, description, is_active, created_at, updated_at)
                    VALUES ('Default Project', 'DEFAULT', 'Project default untuk data existing', 1, NOW(), NOW())
                """))
                conn.commit()
                result = conn.execute(text("SELECT id FROM projects WHERE code = 'DEFAULT' LIMIT 1"))
                default_project = result.fetchone()
            
            default_project_id = default_project[0]
            print(f"✓ Default project ID: {default_project_id}")
            
            # Step 2: Assign data existing ke default project
            tables_with_project_id = [
                'materials',
                'mandors',
                'stock_ins',
                'stock_outs',
                'installed',
                'returns',
                'audit_logs'
            ]
            
            for table in tables_with_project_id:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) FROM {table} WHERE project_id IS NULL
                """))
                null_count = result.scalar()
                
                if null_count > 0:
                    print(f"Memperbarui {null_count} record di tabel {table}...")
                    conn.execute(text(f"""
                        UPDATE {table} 
                        SET project_id = :project_id 
                        WHERE project_id IS NULL
                    """), {"project_id": default_project_id})
                    conn.commit()
                    print(f"✓ {null_count} record di {table} berhasil diupdate")
                else:
                    print(f"✓ Semua record di {table} sudah punya project_id")
            
            # Step 3: Assign semua user ke default project
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM users u
                WHERE NOT EXISTS (
                    SELECT 1 FROM user_projects up 
                    WHERE up.user_id = u.id AND up.project_id = :project_id
                )
            """), {"project_id": default_project_id})
            
            users_without_project = result.scalar()
            
            if users_without_project > 0:
                print(f"Memperbarui {users_without_project} user ke default project...")
                conn.execute(text("""
                    INSERT IGNORE INTO user_projects (user_id, project_id, is_active, is_owner, created_at, updated_at)
                    SELECT u.id, :project_id, 1, 1, NOW(), NOW()
                    FROM users u
                    WHERE NOT EXISTS (
                        SELECT 1 FROM user_projects up 
                        WHERE up.user_id = u.id AND up.project_id = :project_id
                    )
                """), {"project_id": default_project_id})
                conn.commit()
                print(f"✓ {users_without_project} user berhasil di-assign ke default project")
            else:
                print("✓ Semua user sudah punya akses ke default project")
            
            # Step 4: Ubah project_id menjadi NOT NULL (skip jika sudah NOT NULL)
            print("\nMengubah kolom project_id menjadi NOT NULL...")
            for table in tables_with_project_id:
                # Cek apakah kolom masih nullable
                result = conn.execute(text(f"""
                    SELECT IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = '{table}'
                    AND COLUMN_NAME = 'project_id'
                """))
                
                column_info = result.fetchone()
                if column_info and column_info[0] == 'YES':
                    print(f"Mengubah project_id di tabel {table} menjadi NOT NULL...")
                    try:
                        conn.execute(text(f"""
                            ALTER TABLE {table}
                            MODIFY COLUMN project_id INT NOT NULL
                        """))
                        conn.commit()
                        print(f"✓ Kolom project_id di {table} berhasil diubah menjadi NOT NULL")
                    except Exception as e:
                        print(f"⚠ Gagal mengubah project_id di {table}: {str(e)}")
                        # Cek apakah masih ada data NULL
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table} WHERE project_id IS NULL"))
                        null_count = result.scalar()
                        if null_count > 0:
                            print(f"  ⚠ Masih ada {null_count} record dengan project_id NULL di {table}")
                else:
                    print(f"✓ Kolom project_id di {table} sudah NOT NULL")
            
            print("\n✓ Semua data sudah diperbaiki!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    ensure_project_id_not_null()

