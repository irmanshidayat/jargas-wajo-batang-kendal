"""
Script untuk menghapus semua data dari database jargas_apbn
kecuali tabel: users, roles, pages, permissions

Jalankan dengan: python -m scripts.clear_database_except_users
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from app.config.database import SessionLocal, engine
from app.config.settings import settings

# Tabel yang TIDAK boleh dihapus
PROTECTED_TABLES = {
    "users",
    "roles", 
    "pages",
    "permissions"
}

# Urutan penghapusan berdasarkan foreign key dependencies
# Urutan dari child ke parent untuk menghindari constraint violations
DELETE_ORDER = [
    # 1. Tabel child/detail items
    "surat_jalan_items",
    "surat_permintaan_items",
    "user_permissions",  # FK ke users (protected) dan permissions (protected)
    "user_menu_preferences",  # FK ke users (protected) dan pages (protected)
    "role_permissions",  # FK ke roles (protected) dan permissions (protected)
    "user_projects",  # FK ke users (protected) dan projects
    
    # 2. Tabel transaksi/inventory
    "notifications",  # FK ke mandors, materials
    "audit_logs",  # FK ke users (protected), projects
    "returns",  # FK ke mandors, materials, stock_outs, projects
    "installed",  # FK ke materials, mandors, stock_outs
    "stock_outs",  # FK ke mandors, materials, projects
    "stock_ins",  # FK ke materials, projects
    "surat_jalans",  # FK ke projects, stock_outs
    "surat_permintaans",  # FK ke projects
    
    # 3. Tabel master data
    "materials",
    "mandors",  # FK ke projects
    "projects",
]


def get_table_count(db: Session, table_name: str) -> int:
    """Mendapatkan jumlah data di tabel"""
    try:
        result = db.execute(text(f"SELECT COUNT(*) as count FROM `{table_name}`"))
        row = result.fetchone()
        return row[0] if row else 0
    except Exception as e:
        print(f"[WARNING] Tidak bisa menghitung data di tabel {table_name}: {str(e)}")
        return 0


def get_all_tables(db: Session) -> List[str]:
    """Mendapatkan semua nama tabel di database"""
    try:
        result = db.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result.fetchall()]
        return tables
    except Exception as e:
        print(f"[ERROR] Tidak bisa mendapatkan daftar tabel: {str(e)}")
        raise


def delete_table_data(db: Session, table_name: str) -> int:
    """Menghapus semua data dari tabel"""
    try:
        result = db.execute(text(f"DELETE FROM `{table_name}`"))
        db.commit()
        return result.rowcount
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Gagal menghapus data dari tabel {table_name}: {str(e)}")
        raise


def get_table_statistics(db: Session, tables: List[str]) -> Dict[str, int]:
    """Mendapatkan statistik jumlah data per tabel"""
    stats = {}
    for table in tables:
        if table not in PROTECTED_TABLES:
            count = get_table_count(db, table)
            if count > 0:
                stats[table] = count
    return stats


def clear_database_except_protected():
    """Menghapus semua data kecuali tabel yang dilindungi"""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("HAPUS DATA DATABASE JARGAS_APBN")
        print("=" * 70)
        print(f"\n[INFO] Database: {settings.DB_NAME}")
        print(f"[INFO] Host: {settings.DB_HOST}:{settings.DB_PORT}")
        print(f"[INFO] Tabel yang DILINDUNGI (tidak akan dihapus):")
        for table in sorted(PROTECTED_TABLES):
            print(f"   - {table}")
        
        # Dapatkan semua tabel
        print("\n[INFO] Mendapatkan daftar tabel...")
        all_tables = get_all_tables(db)
        print(f"[INFO] Ditemukan {len(all_tables)} tabel di database")
        
        # Filter tabel yang akan dihapus
        tables_to_delete = [t for t in all_tables if t not in PROTECTED_TABLES]
        
        if not tables_to_delete:
            print("\n[SUCCESS] Tidak ada tabel yang perlu dihapus (semua tabel dilindungi)")
            return
        
        # Dapatkan statistik sebelum penghapusan
        print("\n[INFO] Menghitung data per tabel...")
        stats_before = get_table_statistics(db, tables_to_delete)
        
        if not stats_before:
            print("\n[SUCCESS] Semua tabel sudah kosong, tidak ada data yang perlu dihapus.")
            return
        
        # Tampilkan ringkasan data yang akan dihapus
        print("\n" + "=" * 70)
        print("RINGKASAN DATA YANG AKAN DIHAPUS:")
        print("=" * 70)
        total_records = 0
        for table in DELETE_ORDER:
            if table in stats_before:
                count = stats_before[table]
                total_records += count
                print(f"   {table:30s} : {count:6d} records")
        
        # Tabel yang tidak ada di DELETE_ORDER tapi ada di database
        other_tables = [t for t in tables_to_delete if t not in DELETE_ORDER]
        if other_tables:
            print("\n[WARNING] Tabel berikut tidak ada di urutan DELETE_ORDER:")
            for table in other_tables:
                if table in stats_before:
                    count = stats_before[table]
                    total_records += count
                    print(f"   {table:30s} : {count:6d} records")
        
        print("=" * 70)
        print(f"TOTAL RECORDS YANG AKAN DIHAPUS: {total_records:,}")
        print("=" * 70)
        
        # Konfirmasi
        print("\n" + "⚠️ " * 35)
        print("PERINGATAN: Operasi ini TIDAK DAPAT DIBATALKAN!")
        print("Semua data di atas akan dihapus PERMANEN.")
        print("⚠️ " * 35)
        
        confirm = input("\nApakah Anda yakin ingin melanjutkan? (ketik 'YA' untuk konfirmasi): ")
        if confirm != "YA":
            print("\n[INFO] Operasi dibatalkan oleh user.")
            return
        
        # Mulai proses penghapusan
        print("\n[INFO] Memulai proses penghapusan...")
        print("[INFO] Menonaktifkan foreign key checks sementara...")
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        db.commit()
        
        deleted_stats = {}
        total_deleted = 0
        
        try:
            # Hapus data sesuai urutan
            for table in DELETE_ORDER:
                if table in tables_to_delete:
                    count_before = get_table_count(db, table)
                    if count_before > 0:
                        print(f"[INFO] Menghapus data dari tabel '{table}'...", end=" ")
                        deleted_count = delete_table_data(db, table)
                        deleted_stats[table] = deleted_count
                        total_deleted += deleted_count
                        print(f"✅ {deleted_count:,} records dihapus")
            
            # Hapus tabel lain yang tidak ada di DELETE_ORDER
            for table in other_tables:
                if table in tables_to_delete:
                    count_before = get_table_count(db, table)
                    if count_before > 0:
                        print(f"[WARNING] Menghapus data dari tabel '{table}' (tidak ada di urutan standar)...", end=" ")
                        deleted_count = delete_table_data(db, table)
                        deleted_stats[table] = deleted_count
                        total_deleted += deleted_count
                        print(f"✅ {deleted_count:,} records dihapus")
        
        finally:
            # Aktifkan kembali foreign key checks
            print("\n[INFO] Mengaktifkan kembali foreign key checks...")
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            db.commit()
        
        # Verifikasi hasil
        print("\n[INFO] Memverifikasi hasil penghapusan...")
        stats_after = get_table_statistics(db, tables_to_delete)
        
        if stats_after:
            print("\n[WARNING] Masih ada data di beberapa tabel:")
            for table, count in stats_after.items():
                print(f"   {table}: {count} records")
        else:
            print("[SUCCESS] Semua tabel (kecuali yang dilindungi) sudah kosong!")
        
        # Ringkasan
        print("\n" + "=" * 70)
        print("RINGKASAN PENGHAPUSAN:")
        print("=" * 70)
        print(f"Total records yang dihapus: {total_deleted:,}")
        print(f"Tabel yang dihapus: {len(deleted_stats)}")
        print("=" * 70)
        
        print("\n[SUCCESS] Proses penghapusan selesai!")
        
    except Exception as e:
        db.rollback()
        # Pastikan foreign key checks diaktifkan kembali meskipun ada error
        try:
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            db.commit()
        except:
            pass
        print(f"\n[ERROR] Error saat menghapus data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        clear_database_except_protected()
        print("\n" + "=" * 70)
        print("[SUCCESS] Script selesai dijalankan!")
        print("=" * 70)
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"[ERROR] Script gagal: {str(e)}")
        print("=" * 70)
        sys.exit(1)

