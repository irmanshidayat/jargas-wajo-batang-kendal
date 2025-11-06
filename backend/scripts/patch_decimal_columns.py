"""
Script untuk memperbaiki tipe kolom quantity menjadi DECIMAL(10,2) secara langsung.
Jalankan dengan: python -m scripts.patch_decimal_columns
"""
from pathlib import Path
import sys
from typing import List, Tuple

# Tambahkan root directory ke sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import text
from app.config.database import engine


TABLE_COLUMNS: List[Tuple[str, str]] = [
    ("surat_permintaan_items", "qty"),
    ("stock_ins", "quantity"),
    ("stock_outs", "quantity"),
    ("installed", "quantity"),
    ("returns", "quantity_kembali"),
    ("returns", "quantity_kondisi_baik"),
    ("returns", "quantity_kondisi_reject"),
]


def is_decimal(conn, table: str, column: str) -> bool:
    sql = text(
        """
        SELECT COLUMN_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = :table
          AND COLUMN_NAME = :column
        """
    )
    row = conn.execute(sql, {"table": table, "column": column}).fetchone()
    if not row:
        return False
    return "decimal" in str(row[0]).lower() or "numeric" in str(row[0]).lower()


def patch_decimal_columns():
    with engine.begin() as conn:
        for table, column in TABLE_COLUMNS:
            try:
                if is_decimal(conn, table, column):
                    print(f"[SKIP] {table}.{column} sudah DECIMAL")
                    continue

                # Untuk kolom returns.quantity_kondisi_baik dan returns.quantity_kondisi_reject boleh NULL
                nullable = "NULL" if table == "returns" and column in ("quantity_kondisi_baik", "quantity_kondisi_reject") else "NOT NULL"
                alter_sql = text(
                    f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` DECIMAL(10,2) {nullable}"
                )
                conn.execute(alter_sql)
                print(f"[OK] {table}.{column} diubah ke DECIMAL(10,2) {nullable}")
            except Exception as e:
                print(f"[ERROR] Gagal mengubah {table}.{column}: {e}")


if __name__ == "__main__":
    patch_decimal_columns()


