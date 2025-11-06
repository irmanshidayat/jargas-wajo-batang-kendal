"""
Script untuk membuat akun admin di database
Jalankan dengan: python -m scripts.create_admin
"""

import sys
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.orm import Session
import bcrypt
from app.config.database import SessionLocal, engine
from app.models.base import Base
from app.models.user.user import User, UserRole  # Import model untuk memastikan tabel dibuat
from app.repositories.user.user_repository import UserRepository
from app.config.settings import settings

# Pastikan tabel dibuat
Base.metadata.create_all(bind=engine)


def get_password_hash(password: str) -> str:
    """Hash password menggunakan bcrypt"""
    # Generate salt dan hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_admin_user():
    """Membuat akun admin di database"""
    db: Session = SessionLocal()
    
    try:
        user_repo = UserRepository(db)
        
        # Cek apakah admin sudah ada
        admin_email = "admin@jargas.apbn"
        existing_admin = user_repo.get_by_email(admin_email)
        
        if existing_admin:
            print(f"[INFO] Akun admin dengan email {admin_email} sudah ada!")
            print(f"   ID: {existing_admin.id}")
            print(f"   Nama: {existing_admin.name}")
            print(f"   Email: {existing_admin.email}")
            
            # Update password dengan bcrypt hash
            admin_password = "admin123"
            print(f"\n[INFO] Mengupdate password admin dengan bcrypt hash...")
            updated_admin = user_repo.update(
                existing_admin.id,
                {
                    "password_hash": get_password_hash(admin_password),
                    "is_active": True,
                    "is_superuser": True,
                    "role": UserRole.ADMIN
                }
            )
            
            if updated_admin:
                print("[SUCCESS] Password admin berhasil diupdate!")
                print(f"   Email: {updated_admin.email}")
                print(f"   Password: {admin_password}")
                print(f"   Is Superuser: {updated_admin.is_superuser}")
                print(f"   Is Active: {updated_admin.is_active}")
            return
        
        # Data admin
        admin_password = "admin123"  # Password default
        admin_data = {
            "email": admin_email,
            "name": "Administrator",
            "password_hash": get_password_hash(admin_password),
            "role": UserRole.ADMIN,
            "is_active": True,
            "is_superuser": True
        }
        
        # Buat admin user
        admin_user = user_repo.create(admin_data)
        
        if admin_user:
            print("[SUCCESS] Akun admin berhasil dibuat!")
            print(f"   ID: {admin_user.id}")
            print(f"   Nama: {admin_user.name}")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: {admin_password}")
            print(f"   Is Superuser: {admin_user.is_superuser}")
            print(f"   Is Active: {admin_user.is_active}")
            print("\n[WARNING] PENTING: Simpan informasi login ini dengan aman!")
        else:
            print("[ERROR] Gagal membuat akun admin!")
            
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Database: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print("=" * 50)
    create_admin_user()

