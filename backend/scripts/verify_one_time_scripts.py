"""
Script untuk memverifikasi apakah script one-time migration masih diperlukan.
Script ini akan mengecek apakah kolom/tabel yang ditambahkan oleh script one-time
sudah ada di database atau sudah ada di migration Alembic.

Jalankan dengan: python -m scripts.verify_one_time_scripts
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text
from typing import Dict, List, Tuple

def check_column_exists(table: str, column: str) -> bool:
    """Cek apakah kolom sudah ada di database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = :table
                AND COLUMN_NAME = :column
            """), {"table": table, "column": column})
            
            return result.scalar() > 0
    except Exception as e:
        print(f"  ⚠ Error checking column {table}.{column}: {str(e)}")
        return False

def check_table_exists(table: str) -> bool:
    """Cek apakah tabel sudah ada di database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = :table
            """), {"table": table})
            
            return result.scalar() > 0
    except Exception as e:
        print(f"  ⚠ Error checking table {table}: {str(e)}")
        return False

def check_index_exists(table: str, index: str) -> bool:
    """Cek apakah index sudah ada di database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = :table
                AND INDEX_NAME = :index
            """), {"table": table, "index": index})
            
            return result.scalar() > 0
    except Exception as e:
        print(f"  ⚠ Error checking index {table}.{index}: {str(e)}")
        return False

def verify_one_time_scripts():
    """Verifikasi semua script one-time migration"""
    
    # Daftar script one-time dan kolom/tabel yang ditambahkan
    scripts_to_verify = {
        "add_project_id_columns.py": {
            "columns": [
                ("materials", "project_id"),
                ("audit_logs", "project_id"),
            ],
            "indexes": [
                ("materials", "ix_materials_project_id"),
                ("audit_logs", "ix_audit_logs_project_id"),
            ],
            "description": "Menambahkan kolom project_id ke materials dan audit_logs"
        },
        "add_stock_ins_project_id.py": {
            "columns": [
                ("stock_ins", "project_id"),
            ],
            "indexes": [
                ("stock_ins", "ix_stock_ins_project_id"),
            ],
            "description": "Menambahkan kolom project_id ke stock_ins"
        },
        "add_stock_outs_project_id.py": {
            "columns": [
                ("stock_outs", "project_id"),
            ],
            "indexes": [
                ("stock_outs", "ix_stock_outs_project_id"),
            ],
            "description": "Menambahkan kolom project_id ke stock_outs"
        },
        "add_returns_kondisi_columns.py": {
            "columns": [
                ("returns", "quantity_kondisi_baik"),
                ("returns", "quantity_kondisi_reject"),
            ],
            "description": "Menambahkan kolom quantity_kondisi_baik dan quantity_kondisi_reject ke returns"
        },
        "add_stock_outs_surat_columns.py": {
            "columns": [
                ("stock_outs", "surat_permohonan_paths"),
                ("stock_outs", "surat_serah_terima_paths"),
            ],
            "description": "Menambahkan kolom surat_permohonan_paths dan surat_serah_terima_paths ke stock_outs"
        },
        "add_role_column.py": {
            "columns": [
                ("users", "role"),
            ],
            "description": "Menambahkan kolom role ke users"
        },
        "add_role_id_column.py": {
            "columns": [
                ("users", "role_id"),
            ],
            "indexes": [
                ("users", "ix_users_role_id"),
            ],
            "description": "Menambahkan kolom role_id ke users"
        },
        "create_surat_jalan_tables_manual.py": {
            "tables": [
                "surat_jalans",
                "surat_jalan_items",
            ],
            "description": "Membuat tabel surat_jalans dan surat_jalan_items secara manual"
        },
    }
    
    print("=" * 80)
    print("VERIFIKASI SCRIPT ONE-TIME MIGRATION")
    print("=" * 80)
    print()
    
    results = {}
    
    for script_name, checks in scripts_to_verify.items():
        print(f"📋 {script_name}")
        print(f"   {checks.get('description', 'N/A')}")
        
        all_exist = True
        missing_items = []
        
        # Cek kolom
        if "columns" in checks:
            for table, column in checks["columns"]:
                exists = check_column_exists(table, column)
                status = "✓" if exists else "✗"
                print(f"   {status} Kolom {table}.{column}: {'Ada' if exists else 'TIDAK ADA'}")
                if not exists:
                    all_exist = False
                    missing_items.append(f"Kolom {table}.{column}")
        
        # Cek tabel
        if "tables" in checks:
            for table in checks["tables"]:
                exists = check_table_exists(table)
                status = "✓" if exists else "✗"
                print(f"   {status} Tabel {table}: {'Ada' if exists else 'TIDAK ADA'}")
                if not exists:
                    all_exist = False
                    missing_items.append(f"Tabel {table}")
        
        # Cek index
        if "indexes" in checks:
            for table, index in checks["indexes"]:
                exists = check_index_exists(table, index)
                status = "✓" if exists else "✗"
                print(f"   {status} Index {table}.{index}: {'Ada' if exists else 'TIDAK ADA'}")
                if not exists:
                    all_exist = False
                    missing_items.append(f"Index {table}.{index}")
        
        results[script_name] = {
            "all_exist": all_exist,
            "missing_items": missing_items
        }
        
        if all_exist:
            print(f"   ✅ Status: SEMUA SUDAH ADA - Script bisa di-archive/hapus")
        else:
            print(f"   ⚠️  Status: MASIH DIPERLUKAN - Ada yang belum ada: {', '.join(missing_items)}")
        
        print()
    
    # Summary
    print("=" * 80)
    print("RINGKASAN")
    print("=" * 80)
    
    safe_to_archive = [name for name, result in results.items() if result["all_exist"]]
    still_needed = [name for name, result in results.items() if not result["all_exist"]]
    
    print(f"\n✅ Script yang AMAN untuk di-archive/hapus ({len(safe_to_archive)}):")
    for name in safe_to_archive:
        print(f"   - {name}")
    
    if still_needed:
        print(f"\n⚠️  Script yang MASIH DIPERLUKAN ({len(still_needed)}):")
        for name in still_needed:
            missing = results[name]["missing_items"]
            print(f"   - {name}")
            print(f"     Missing: {', '.join(missing)}")
    
    print()
    print("=" * 80)
    print("REKOMENDASI")
    print("=" * 80)
    print("1. Script yang 'AMAN untuk di-archive' bisa dipindah ke folder archive")
    print("2. Script yang 'MASIH DIPERLUKAN' harus dipertahankan atau dijalankan")
    print("3. Pastikan semua kolom/tabel sudah ada di migration Alembic sebelum menghapus")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    try:
        verify_one_time_scripts()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

