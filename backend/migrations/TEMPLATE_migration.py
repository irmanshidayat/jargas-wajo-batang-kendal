"""
Template Migration File - Best Practice

Copy file ini ke folder versions/ dan rename sesuai kebutuhan migration Anda.
Hapus komentar template setelah selesai.

Naming: {timestamp}_{deskripsi_singkat}.py
Contoh: 20251031_add_user_status_column.py

⚠️ PENTING: File ini HARUS di-copy ke folder versions/ dan di-rename!
Jangan biarkan file template di folder versions/ karena akan menyebabkan error.
"""

import logging
from typing import Sequence, Union
from pathlib import Path
import sys

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

# Add migrations directory to path untuk import utils
migrations_dir = Path(__file__).parent.parent
sys.path.insert(0, str(migrations_dir.parent))

from migrations.utils import (
    table_exists,
    column_exists,
    index_exists,
    foreign_key_exists,
    safe_add_column,
    safe_drop_column,
    safe_create_index,
    safe_drop_index,
    get_table_columns,
    get_table_indexes,
    validate_migration_prerequisites
)

# Setup logger untuk migration
logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
# Ganti dengan revision ID yang unik (bisa generate dengan: alembic revision -m "description")
revision: str = 'your_unique_revision_id'
# Ganti dengan revision ID sebelumnya (cek dengan: alembic current)
down_revision: Union[str, None] = 'previous_revision_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ============================================================================
# UPGRADE FUNCTION
# ============================================================================

def upgrade() -> None:
    """
    Upgrade: Deskripsi perubahan yang dilakukan
    
    Best Practice Checklist:
    - [ ] Gunakan fungsi dari migrations.utils untuk konsistensi
    - [ ] Safety checks lengkap (table/column exists) - sudah ada di utils
    - [ ] Idempotent (bisa dijalankan berulang) - sudah ada di utils
    - [ ] Error handling dengan logging - sudah ada di utils
    - [ ] Nullable columns untuk backward compatibility
    - [ ] Data migration jika perlu
    """
    logger.info(f"Starting migration: {revision}")
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # ========================================================================
    # PATTERN 1: Add Column (Menggunakan safe_add_column dari utils)
    # ========================================================================
    table_name = 'your_table_name'
    column_name = 'new_column'
    
    # safe_add_column sudah melakukan safety check (idempotent)
    safe_add_column(
        inspector,
        table_name,
        column_name,
        sa.String(255),
        nullable=True
    )
    
    # ========================================================================
    # PATTERN 2: Add Column dengan Default Value (Menggunakan safe_add_column)
    # ========================================================================
    # safe_add_column(
    #     inspector,
    #     table_name,
    #     'status',
    #     sa.String(50),
    #     nullable=False,
    #     server_default='active'
    # )
    
    # ========================================================================
    # PATTERN 3: Modify Column
    # ========================================================================
    # if column_exists(inspector, table_name, 'old_column'):
    #     op.alter_column(
    #         table_name,
    #         'old_column',
    #         existing_type=sa.String(100),
    #         type_=sa.String(255),
    #         existing_nullable=True,
    #         nullable=False
    #     )
    
    # ========================================================================
    # PATTERN 4: Add Index (Menggunakan safe_create_index dari utils)
    # ========================================================================
    # index_name = f'ix_{table_name}_{column_name}'
    # safe_create_index(
    #     inspector,
    #     table_name,
    #     index_name,
    #     [column_name],
    #     unique=False
    # )
    
    # ========================================================================
    # PATTERN 5: Data Migration
    # ========================================================================
    # # Step 1: Add column nullable (menggunakan safe_add_column)
    # safe_add_column(
    #     inspector,
    #     table_name,
    #     'new_field',
    #     sa.String(255),
    #     nullable=True
    # )
    # 
    # # Step 2: Migrate existing data
    # connection.execute(text("""
    #     UPDATE your_table_name 
    #     SET new_field = CONCAT(old_field1, ' ', old_field2)
    #     WHERE new_field IS NULL
    # """))
    # 
    # # Step 3: Make NOT NULL (setelah data di-migrate)
    # if column_exists(inspector, table_name, 'new_field'):
    #     op.alter_column(table_name, 'new_field', nullable=False)
    
    # ========================================================================
    # PATTERN 6: Create Table
    # ========================================================================
    # if not table_exists(inspector, 'new_table'):
    #     op.create_table(
    #         'new_table',
    #         sa.Column('id', sa.Integer(), nullable=False),
    #         sa.Column('name', sa.String(255), nullable=False),
    #         sa.PrimaryKeyConstraint('id')
    #     )
    #     logger.info("✅ Berhasil membuat table 'new_table'")
    
    # ========================================================================
    # PATTERN 7: Add Foreign Key
    # ========================================================================
    # op.create_foreign_key(
    #     'fk_table_name_foreign_id',
    #     'table_name',
    #     'foreign_table',
    #     ['foreign_id'],
    #     ['id']
    # )
    
    logger.info("✅ Migration completed successfully")


# ============================================================================
# DOWNGRADE FUNCTION
# ============================================================================

def downgrade() -> None:
    """
    Downgrade: Rollback perubahan yang dilakukan di upgrade()
    
    Best Practice:
    - [ ] Gunakan fungsi dari migrations.utils untuk konsistensi
    - [ ] Reverse order dari upgrade (LIFO - Last In First Out)
    - [ ] Safety checks lengkap - sudah ada di utils
    - [ ] Error handling dengan logging - sudah ada di utils
    - [ ] Backup data jika perlu sebelum drop
    """
    logger.info(f"Starting downgrade: {revision}")
    connection = op.get_bind()
    inspector = inspect(connection)
    
    table_name = 'your_table_name'
    column_name = 'new_column'
    
    # ========================================================================
    # PATTERN 1: Drop Column (Menggunakan safe_drop_column dari utils)
    # Reverse order dari upgrade (LIFO - Last In First Out)
    # ========================================================================
    # safe_drop_column sudah melakukan safety check (idempotent)
    safe_drop_column(inspector, table_name, column_name)
    
    # ========================================================================
    # PATTERN 2: Drop Index (Menggunakan safe_drop_index dari utils)
    # ========================================================================
    # index_name = f'ix_{table_name}_{column_name}'
    # safe_drop_index(inspector, table_name, index_name)
    
    # ========================================================================
    # PATTERN 3: Drop Foreign Key
    # ========================================================================
    # op.drop_constraint('fk_table_name_foreign_id', table_name, type_='foreignkey')
    
    # ========================================================================
    # PATTERN 4: Drop Table
    # ========================================================================
    # if table_exists(inspector, 'new_table'):
    #     op.drop_table('new_table')
    #     logger.info("✅ Berhasil menghapus table 'new_table'")
    
    # ========================================================================
    # PATTERN 5: Data Rollback (jika perlu backup data)
    # ========================================================================
    # # Backup data sebelum drop (jika perlu)
    # connection.execute(text("""
    #     CREATE TABLE IF NOT EXISTS backup_table AS
    #     SELECT id, column_to_drop FROM your_table
    # """))
    # 
    # # Drop column
    # op.drop_column('your_table', 'column_to_drop')
    
    logger.info("✅ Downgrade completed successfully")

