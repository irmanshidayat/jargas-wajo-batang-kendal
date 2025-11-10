"""Script untuk debug surat permintaan - cek database dan test endpoint"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config.settings import Settings
from app.models.inventory.surat_permintaan import SuratPermintaan
from app.models.project.project import Project
from app.models.user.user import User
import json

settings = Settings()

# Database connection
DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("DEBUG SURAT PERMINTAAN")
print("=" * 80)

# 1. Cek total data surat permintaan
print("\n1. Cek Total Data Surat Permintaan:")
total = db.query(SuratPermintaan).filter(SuratPermintaan.is_deleted == 0).count()
print(f"   Total surat permintaan (tidak deleted): {total}")

# 2. Cek per project
print("\n2. Cek Data Per Project:")
projects = db.query(Project).all()
for project in projects:
    count = db.query(SuratPermintaan).filter(
        SuratPermintaan.project_id == project.id,
        SuratPermintaan.is_deleted == 0
    ).count()
    print(f"   Project {project.name} (ID: {project.id}, Code: {project.code}): {count} data")

# 3. Cek beberapa data terbaru
print("\n3. Data Terbaru (5 terakhir):")
recent = db.query(SuratPermintaan).filter(
    SuratPermintaan.is_deleted == 0
).order_by(SuratPermintaan.created_at.desc()).limit(5).all()

if recent:
    for sp in recent:
        print(f"   - ID: {sp.id}, Nomor: {sp.nomor_surat}, Project ID: {sp.project_id}, Tanggal: {sp.tanggal}")
else:
    print("   Tidak ada data surat permintaan")

# 4. Cek users untuk test authentication
print("\n4. Cek Users untuk Test:")
users = db.query(User).limit(3).all()
for user in users:
    print(f"   - ID: {user.id}, Email: {user.email}, Name: {user.name}")

# 5. Test query dengan filter project_id
print("\n5. Test Query dengan Project ID:")
if projects:
    test_project = projects[0]
    test_data = db.query(SuratPermintaan).filter(
        SuratPermintaan.project_id == test_project.id,
        SuratPermintaan.is_deleted == 0
    ).limit(3).all()
    print(f"   Project ID {test_project.id} ({test_project.name}): {len(test_data)} data ditemukan")
    for sp in test_data:
        print(f"     - {sp.nomor_surat}")

print("\n" + "=" * 80)
print("SELESAI")
print("=" * 80)

db.close()



