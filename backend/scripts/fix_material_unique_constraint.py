"""
Script untuk memperbaiki unique constraint pada materials table
Menghapus unique constraint global dan membuat composite unique (project_id, kode_barang)
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text

def fix_unique_constraint():
    """Memperbaiki unique constraint pada materials"""
    try:
        with engine.connect() as conn:
            print("Mengecek constraint/index yang ada...")
            
            # Cek apakah index/constraint ix_materials_kode_barang ada
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'materials'
                AND INDEX_NAME = 'ix_materials_kode_barang'
            """))
            
            has_index = result.scalar() > 0
            
            if has_index:
                print("Menghapus index ix_materials_kode_barang...")
                conn.execute(text("DROP INDEX ix_materials_kode_barang ON materials"))
                conn.commit()
                print("✓ Index ix_materials_kode_barang berhasil dihapus")
            
            # Cek apakah ada constraint unique lainnya pada kode_barang
            result = conn.execute(text("""
                SELECT CONSTRAINT_NAME
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'materials'
                AND CONSTRAINT_TYPE = 'UNIQUE'
                AND CONSTRAINT_NAME LIKE '%kode_barang%'
            """))
            
            constraints = result.fetchall()
            for constraint in constraints:
                constraint_name = constraint[0]
                print(f"Menghapus constraint {constraint_name}...")
                try:
                    conn.execute(text(f"ALTER TABLE materials DROP INDEX {constraint_name}"))
                    conn.commit()
                    print(f"✓ Constraint {constraint_name} berhasil dihapus")
                except Exception as e:
                    print(f"⚠ Gagal menghapus constraint {constraint_name}: {str(e)}")
                    # Coba dengan format lain
                    try:
                        conn.execute(text(f"ALTER TABLE materials DROP CONSTRAINT {constraint_name}"))
                        conn.commit()
                        print(f"✓ Constraint {constraint_name} berhasil dihapus (alternatif)")
                    except Exception as e2:
                        print(f"⚠ Gagal menghapus constraint {constraint_name} dengan alternatif: {str(e2)}")
            
            # Cek apakah composite unique constraint sudah ada
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'materials'
                AND CONSTRAINT_NAME = 'uq_material_project_kode'
            """))
            
            has_composite = result.scalar() > 0
            
            if not has_composite:
                print("\nMembuat composite unique constraint (project_id, kode_barang)...")
                conn.execute(text("""
                    ALTER TABLE materials
                    ADD CONSTRAINT uq_material_project_kode
                    UNIQUE (project_id, kode_barang)
                """))
                conn.commit()
                print("✓ Composite unique constraint uq_material_project_kode berhasil dibuat")
            else:
                print("✓ Composite unique constraint uq_material_project_kode sudah ada")
            
            print("\n✓ Semua constraint sudah diperbaiki!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_unique_constraint()

