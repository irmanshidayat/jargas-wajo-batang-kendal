"""
Script untuk menghapus semua data dari tabel materials
Jalankan dengan: python -m scripts.delete_materials_data
"""

import sys
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import SessionLocal, engine
from app.config.settings import settings
from app.models.inventory.material import Material

def delete_all_materials():
    """Menghapus semua data dari tabel materials"""
    db: Session = SessionLocal()
    try:
        # Hitung jumlah data sebelum dihapus
        count_before = db.query(Material).count()
        print(f"[INFO] Jumlah data materials sebelum dihapus: {count_before}")
        
        if count_before == 0:
            print("[SUCCESS] Tabel materials sudah kosong, tidak ada data yang perlu dihapus.")
            return
        
        # Konfirmasi
        print(f"\n[WARNING] PERINGATAN: Akan menghapus {count_before} data dari tabel materials!")
        print(f"   Database: {settings.DB_NAME}")
        print(f"   Host: {settings.DB_HOST}:{settings.DB_PORT}")
        print(f"\n[INFO] Menonaktifkan foreign key checks sementara...")
        
        # Nonaktifkan foreign key checks sementara
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        db.commit()
        
        try:
            # Hapus semua data menggunakan SQL DELETE
            deleted_count = db.query(Material).delete()
            db.commit()
            
            print(f"[SUCCESS] Berhasil menghapus {deleted_count} data dari tabel materials")
        finally:
            # Aktifkan kembali foreign key checks
            print(f"[INFO] Mengaktifkan kembali foreign key checks...")
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            db.commit()
        
        print(f"[SUCCESS] Tabel materials sekarang kosong")
        
    except Exception as e:
        db.rollback()
        # Pastikan foreign key checks diaktifkan kembali meskipun ada error
        try:
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            db.commit()
        except:
            pass
        print(f"[ERROR] Error saat menghapus data: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("HAPUS DATA TABEL MATERIALS")
    print("=" * 60)
    print()
    
    try:
        delete_all_materials()
        print("\n" + "=" * 60)
        print("[SUCCESS] Proses selesai!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"[ERROR] Proses gagal: {str(e)}")
        print("=" * 60)
        sys.exit(1)

