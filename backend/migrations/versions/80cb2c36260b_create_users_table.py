"""create_users_table

Revision ID: 80cb2c36260b
Revises: add_surat_permohonan_stock_outs
Create Date: 2025-11-10 18:46:20.655634

"""
from typing import Sequence, Union
import logging

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = '80cb2c36260b'
down_revision: Union[str, None] = 'add_surat_permohonan_stock_outs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Membuat tabel users jika belum ada
    Migration ini dibuat untuk memastikan tabel users ada sebelum migration lain yang membutuhkannya
    """
    connection = op.get_bind()
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Cek apakah tabel users sudah ada
    if 'users' in existing_tables:
        logger.info("Tabel 'users' sudah ada, skip migration")
        return
    
    # Buat tabel users
    logger.info("Membuat tabel 'users'...")
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='gudang'),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Buat index
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    
    logger.info("✅ Tabel 'users' berhasil dibuat")


def downgrade() -> None:
    """
    Drop tabel users (hati-hati, ini akan menghapus semua data users!)
    """
    connection = op.get_bind()
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    if 'users' in existing_tables:
        logger.warning("Menghapus tabel 'users'...")
        op.drop_index(op.f('ix_users_role'), table_name='users')
        op.drop_index(op.f('ix_users_email'), table_name='users')
        op.drop_index(op.f('ix_users_id'), table_name='users')
        op.drop_table('users')
        logger.info("Tabel 'users' berhasil dihapus")
    else:
        logger.info("Tabel 'users' tidak ada, skip downgrade")
