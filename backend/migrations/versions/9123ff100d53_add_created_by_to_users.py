"""add_created_by_to_users

Revision ID: 9123ff100d53
Revises: add_harga_materials
Create Date: 2025-11-11 10:34:16.597353

"""
import logging
from typing import Sequence, Union
from pathlib import Path
import sys

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


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

# Setup logger
logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = '9123ff100d53'
down_revision: Union[str, None] = 'add_harga_materials'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    logger.info(f"Starting migration: add_created_by_to_users")
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Check if users table exists
    if not table_exists(inspector, 'users'):
        logger.warning("Tabel 'users' tidak ditemukan, skip migration")
        return
    
    # Add created_by column if not exists
    if not column_exists(inspector, 'users', 'created_by'):
        logger.info("Menambahkan kolom 'created_by' ke tabel 'users'...")
        op.add_column('users', sa.Column('created_by', sa.Integer(), nullable=True))
        logger.info("✅ Kolom 'created_by' berhasil ditambahkan")
    else:
        logger.info("Kolom 'created_by' sudah ada, skip")
    
    # Add foreign key constraint if not exists
    if not foreign_key_exists(inspector, 'users', 'created_by'):
        logger.info("Menambahkan foreign key constraint untuk 'created_by'...")
        op.create_foreign_key(
            'fk_users_created_by',
            'users',
            'users',
            ['created_by'],
            ['id'],
            ondelete='SET NULL'
        )
        logger.info("✅ Foreign key constraint berhasil ditambahkan")
    else:
        logger.info("Foreign key constraint untuk 'created_by' sudah ada, skip")
    
    # Add index if not exists
    if not index_exists(inspector, 'users', 'ix_users_created_by'):
        logger.info("Menambahkan index untuk 'created_by'...")
        op.create_index('ix_users_created_by', 'users', ['created_by'])
        logger.info("✅ Index 'ix_users_created_by' berhasil ditambahkan")
    else:
        logger.info("Index 'ix_users_created_by' sudah ada, skip")
    
    logger.info("✅ Migration completed successfully")


def downgrade() -> None:
    logger.info(f"Starting downgrade: add_created_by_to_users")
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Check if users table exists
    if not table_exists(inspector, 'users'):
        logger.warning("Tabel 'users' tidak ditemukan, skip downgrade")
        return
    
    # Drop index if exists
    if index_exists(inspector, 'users', 'ix_users_created_by'):
        logger.info("Menghapus index 'ix_users_created_by'...")
        op.drop_index('ix_users_created_by', table_name='users')
        logger.info("✅ Index 'ix_users_created_by' berhasil dihapus")
    
    # Drop foreign key constraint if exists
    if foreign_key_exists(inspector, 'users', 'created_by'):
        logger.info("Menghapus foreign key constraint untuk 'created_by'...")
        op.drop_constraint('fk_users_created_by', 'users', type_='foreignkey')
        logger.info("✅ Foreign key constraint berhasil dihapus")
    
    # Drop column if exists
    if column_exists(inspector, 'users', 'created_by'):
        logger.info("Menghapus kolom 'created_by' dari tabel 'users'...")
        op.drop_column('users', 'created_by')
        logger.info("✅ Kolom 'created_by' berhasil dihapus")
    
    logger.info("✅ Downgrade completed successfully")
