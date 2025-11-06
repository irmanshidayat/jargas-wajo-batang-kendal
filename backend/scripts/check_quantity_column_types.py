"""
Script untuk mengecek tipe kolom quantity di database
Jalankan dengan: python -m scripts.check_quantity_column_types
"""
import sys
import os
from pathlib import Path

# Tambahkan root directory ke path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.config.database import engine
from sqlalchemy import text

def check_quantity_columns():
    """Cek tipe kolom quantity di semua tabel yang relevan"""
    try:
        with engine.connect() as conn:
            tables_to_check = [
                ('stock_ins', 'quantity'),
                ('stock_outs', 'quantity'),
                ('installed', 'quantity'),
                ('returns', 'quantity_kembali'),
                ('returns', 'quantity_kondisi_baik'),
                ('returns', 'quantity_kondisi_reject'),
                ('surat_permintaan_items', 'qty'),
            ]
            
            print("=" * 80)
            print("CEK TIPE KOLOM QUANTITY DI DATABASE")
            print("=" * 80)
            
            for table_name, column_name in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT 
                        COLUMN_NAME,
                        DATA_TYPE,
                        COLUMN_TYPE,
                        IS_NULLABLE,
                        COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = '{table_name}'
                    AND COLUMN_NAME = '{column_name}'
                """))
                
                row = result.fetchone()
                if row:
                    print(f"\n[TABEL] {table_name}.{column_name}")
                    print(f"   DATA_TYPE: {row[1]}")
                    print(f"   COLUMN_TYPE: {row[2]}")
                    print(f"   IS_NULLABLE: {row[3]}")
                    print(f"   COLUMN_DEFAULT: {row[4]}")
                    
                    # Cek apakah sudah DECIMAL
                    if 'decimal' in str(row[2]).lower() or 'numeric' in str(row[2]).lower():
                        print(f"   [OK] Status: SUDAH DECIMAL")
                    elif 'int' in str(row[2]).lower():
                        print(f"   [ERROR] Status: MASIH INTEGER (perlu migration!)")
                    else:
                        print(f"   [WARNING] Status: TIPE LAIN ({row[2]})")
                else:
                    print(f"\n[ERROR] Kolom {table_name}.{column_name} tidak ditemukan!")
            
            print("\n" + "=" * 80)
            print("CEK STATUS MIGRATION")
            print("=" * 80)
            
            # Cek apakah migration sudah dijalankan
            result = conn.execute(text("""
                SELECT version_num 
                FROM alembic_version 
                ORDER BY version_num DESC 
                LIMIT 1
            """))
            current_version = result.fetchone()
            if current_version:
                print(f"Current migration version: {current_version[0]}")
                target_version = "6d338d47c23b"
                if target_version == current_version[0]:
                    print(f"[OK] Migration convert_quantity_to_decimal sudah dijalankan")
                else:
                    print(f"[WARNING] Migration convert_quantity_to_decimal belum dijalankan (current: {current_version[0]})")
            else:
                print("[ERROR] Tidak ada migration version di database")
            
            print("\n" + "=" * 80)
            
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_quantity_columns()

