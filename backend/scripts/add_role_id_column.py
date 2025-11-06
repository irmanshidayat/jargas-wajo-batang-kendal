"""Script untuk menambahkan kolom role_id ke tabel users"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.database import engine
from sqlalchemy import text

def add_role_id_column():
    """Tambahkan kolom role_id jika belum ada"""
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'role_id'
            """))
            
            count = result.fetchone()[0]
            
            if count == 0:
                print("Menambahkan kolom role_id ke tabel users...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role_id INT NULL,
                    ADD INDEX ix_users_role_id (role_id)
                """))
                
                # Add foreign key jika tabel roles sudah ada
                try:
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD CONSTRAINT fk_users_role_id 
                        FOREIGN KEY (role_id) REFERENCES roles(id)
                    """))
                except Exception as e:
                    print(f"Warning: Foreign key constraint mungkin sudah ada atau tabel roles belum ada: {e}")
                
                conn.commit()
                print("Kolom role_id berhasil ditambahkan!")
            else:
                print("Kolom role_id sudah ada, tidak perlu menambahkan.")
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_role_id_column()

