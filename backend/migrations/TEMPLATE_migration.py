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

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

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
# HELPER FUNCTIONS (Optional - bisa dipindah ke file terpisah untuk reusability)
# ============================================================================

def table_exists(inspector, table_name: str) -> bool:
    """Check if table exists"""
    return table_name in inspector.get_table_names()


def column_exists(inspector, table_name: str, column_name: str) -> bool:
    """Check if column exists in table"""
    if not table_exists(inspector, table_name):
        return False
    existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in existing_columns


def index_exists(inspector, table_name: str, index_name: str) -> bool:
    """Check if index exists"""
    if not table_exists(inspector, table_name):
        return False
    existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in existing_indexes


# ============================================================================
# UPGRADE FUNCTION
# ============================================================================

def upgrade() -> None:
    """
    Upgrade: Deskripsi perubahan yang dilakukan
    
    Best Practice Checklist:
    - [ ] Safety checks lengkap (table/column exists)
    - [ ] Idempotent (bisa dijalankan berulang)
    - [ ] Error handling dengan logging
    - [ ] Nullable columns untuk backward compatibility
    - [ ] Data migration jika perlu
    """
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # ========================================================================
    # PATTERN 1: Add Column
    # ========================================================================
    table_name = 'your_table_name'
    column_name = 'new_column'
    
    if not table_exists(inspector, table_name):
        logger.warning(f"Table '{table_name}' tidak ditemukan, skip migration")
        return
    
    if not column_exists(inspector, table_name, column_name):
        try:
            op.add_column(
                table_name,
                sa.Column(column_name, sa.String(255), nullable=True)
            )
            logger.info(f"✅ Berhasil menambahkan kolom '{column_name}'")
        except Exception as e:
            logger.error(f"❌ Error menambahkan kolom '{column_name}': {str(e)}")
            if 'duplicate column' not in str(e).lower():
                raise
    else:
        logger.info(f"Kolom '{column_name}' sudah ada, skip")
    
    # ========================================================================
    # PATTERN 2: Add Column dengan Default Value
    # ========================================================================
    # op.add_column(
    #     table_name,
    #     sa.Column('status', sa.String(50), nullable=False, server_default='active')
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
    # PATTERN 4: Add Index
    # ========================================================================
    # index_name = f'ix_{table_name}_{column_name}'
    # if not index_exists(inspector, table_name, index_name):
    #     try:
    #         op.create_index(index_name, table_name, [column_name], unique=False)
    #         logger.info(f"✅ Berhasil membuat index '{index_name}'")
    #     except Exception as e:
    #         logger.error(f"❌ Error membuat index '{index_name}': {str(e)}")
    
    # ========================================================================
    # PATTERN 5: Data Migration
    # ========================================================================
    # # Step 1: Add column nullable
    # op.add_column(table_name, sa.Column('new_field', sa.String(255), nullable=True))
    # 
    # # Step 2: Migrate existing data
    # connection.execute(text("""
    #     UPDATE your_table_name 
    #     SET new_field = CONCAT(old_field1, ' ', old_field2)
    #     WHERE new_field IS NULL
    # """))
    # 
    # # Step 3: Make NOT NULL (setelah data di-migrate)
    # op.alter_column(table_name, 'new_field', nullable=False)
    
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


# ============================================================================
# DOWNGRADE FUNCTION
# ============================================================================

def downgrade() -> None:
    """
    Downgrade: Rollback perubahan yang dilakukan di upgrade()
    
    Best Practice:
    - [ ] Reverse order dari upgrade (LIFO - Last In First Out)
    - [ ] Safety checks lengkap
    - [ ] Error handling dengan logging
    - [ ] Backup data jika perlu sebelum drop
    """
    connection = op.get_bind()
    inspector = inspect(connection)
    
    table_name = 'your_table_name'
    column_name = 'new_column'
    
    # Safety check
    if not table_exists(inspector, table_name):
        logger.warning(f"Table '{table_name}' tidak ditemukan, skip downgrade")
        return
    
    # ========================================================================
    # PATTERN 1: Drop Column (reverse order dari upgrade)
    # ========================================================================
    if column_exists(inspector, table_name, column_name):
        try:
            op.drop_column(table_name, column_name)
            logger.info(f"✅ Berhasil menghapus kolom '{column_name}'")
        except Exception as e:
            logger.error(f"❌ Error menghapus kolom '{column_name}': {str(e)}")
            if 'unknown column' not in str(e).lower():
                raise
    else:
        logger.info(f"Kolom '{column_name}' tidak ada, skip")
    
    # ========================================================================
    # PATTERN 2: Drop Index
    # ========================================================================
    # index_name = f'ix_{table_name}_{column_name}'
    # if index_exists(inspector, table_name, index_name):
    #     try:
    #         op.drop_index(index_name, table_name=table_name)
    #         logger.info(f"✅ Berhasil menghapus index '{index_name}'")
    #     except Exception as e:
    #         logger.error(f"❌ Error menghapus index '{index_name}': {str(e)}")
    
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

