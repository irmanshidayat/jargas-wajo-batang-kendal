"""
Script untuk menambahkan kolom role ke tabel users
Jalankan dengan: python -m scripts.add_role_column
"""

import sys
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.config.database import engine
from sqlalchemy import text

def add_role_column():
    """Menambahkan kolom role ke tabel users"""
    try:
        with engine.connect() as conn:
            # Cek apakah kolom sudah ada
            result = conn.execute(text(
                "SELECT COUNT(*) as count FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'role'"
            ))
            exists = result.fetchone()[0] > 0
            
            if exists:
                print("[INFO] Kolom 'role' sudah ada di tabel users")
                return
            
            # Tambahkan kolom role
            print("[INFO] Menambahkan kolom 'role' ke tabel users...")
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'GUDANG' NOT NULL"
            ))
            # Update existing rows jika ada
            conn.execute(text(
                "UPDATE users SET role = 'GUDANG' WHERE role IS NULL OR role = ''"
            ))
            conn.commit()
            print("[SUCCESS] Kolom 'role' berhasil ditambahkan!")
            
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        if 'Duplicate column name' in str(e):
            print("[INFO] Kolom 'role' sudah ada")
        else:
            raise

if __name__ == "__main__":
    add_role_column()

