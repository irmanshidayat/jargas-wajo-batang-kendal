"""
Script untuk memperbaiki nilai role user yang ada
Jalankan dengan: python -m scripts.fix_user_roles
"""

import sys
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.config.database import engine
from sqlalchemy import text

def fix_user_roles():
    """Memperbaiki nilai role user yang ada"""
    try:
        with engine.connect() as conn:
            print("[INFO] Memperbaiki nilai role user...")
            # Update lowercase ke uppercase
            result = conn.execute(text(
                "UPDATE users SET role = 'GUDANG' WHERE role = 'gudang'"
            ))
            conn.commit()
            print(f"[SUCCESS] {result.rowcount} user(s) diperbaiki!")
            
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        raise

if __name__ == "__main__":
    fix_user_roles()

