"""create_surat_jalan_tables

Revision ID: create_surat_jalan_tables
Revises: 82b36e17b6fd
Create Date: 2025-01-20 10:00:00.000000

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

from migrations.utils import table_exists

# Setup logger
logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = 'create_surat_jalan_tables'
down_revision: Union[str, None] = '82b36e17b6fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create surat_jalans and surat_jalan_items tables"""
    logger.info("Starting migration: create_surat_jalan_tables")
    
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Create surat_jalans table
    if not table_exists(inspector, 'surat_jalans'):
        op.create_table(
            'surat_jalans',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nomor_form', sa.String(length=255), nullable=False),
            sa.Column('kepada', sa.String(length=255), nullable=False),
            sa.Column('tanggal_pengiriman', sa.Date(), nullable=False),
            sa.Column('nama_pemberi', sa.String(length=255), nullable=True),
            sa.Column('nama_penerima', sa.String(length=255), nullable=True),
            sa.Column('tanggal_diterima', sa.Date(), nullable=True),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('updated_by', sa.Integer(), nullable=True),
            sa.Column('deleted_by', sa.Integer(), nullable=True),
            sa.Column('is_deleted', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('nomor_form', name='uq_surat_jalan_number'),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
            sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
            sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ),
        )
        op.create_index(op.f('ix_surat_jalans_id'), 'surat_jalans', ['id'], unique=False)
        op.create_index(op.f('ix_surat_jalans_nomor_form'), 'surat_jalans', ['nomor_form'], unique=True)
        op.create_index(op.f('ix_surat_jalans_tanggal_pengiriman'), 'surat_jalans', ['tanggal_pengiriman'], unique=False)
        op.create_index(op.f('ix_surat_jalans_project_id'), 'surat_jalans', ['project_id'], unique=False)
        op.create_index(op.f('ix_surat_jalans_is_deleted'), 'surat_jalans', ['is_deleted'], unique=False)
        logger.info("✅ Tabel 'surat_jalans' berhasil dibuat")
    else:
        logger.info("Tabel 'surat_jalans' sudah ada, skip")

    # Create surat_jalan_items table
    if not table_exists(inspector, 'surat_jalan_items'):
        op.create_table(
            'surat_jalan_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('surat_jalan_id', sa.Integer(), nullable=False),
            sa.Column('nama_barang', sa.String(length=255), nullable=False),
            sa.Column('qty', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('keterangan', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['surat_jalan_id'], ['surat_jalans.id'], ),
        )
        op.create_index(op.f('ix_surat_jalan_items_id'), 'surat_jalan_items', ['id'], unique=False)
        op.create_index(op.f('ix_surat_jalan_items_surat_jalan_id'), 'surat_jalan_items', ['surat_jalan_id'], unique=False)
        logger.info("✅ Tabel 'surat_jalan_items' berhasil dibuat")
    else:
        logger.info("Tabel 'surat_jalan_items' sudah ada, skip")
    
    logger.info("✅ Migration completed successfully")


def downgrade() -> None:
    """Drop surat_jalan_items and surat_jalans tables"""
    logger.info("Starting downgrade: create_surat_jalan_tables")
    
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Drop surat_jalan_items table (dengan safety check)
    if table_exists(inspector, 'surat_jalan_items'):
        try:
            op.drop_index(op.f('ix_surat_jalan_items_surat_jalan_id'), table_name='surat_jalan_items')
            op.drop_index(op.f('ix_surat_jalan_items_id'), table_name='surat_jalan_items')
            op.drop_table('surat_jalan_items')
            logger.info("✅ Tabel 'surat_jalan_items' berhasil dihapus")
        except Exception as e:
            logger.error(f"❌ Error menghapus tabel 'surat_jalan_items': {str(e)}")
            raise
    else:
        logger.info("Tabel 'surat_jalan_items' tidak ada, skip")

    # Drop surat_jalans table (dengan safety check)
    if table_exists(inspector, 'surat_jalans'):
        try:
            op.drop_index(op.f('ix_surat_jalans_is_deleted'), table_name='surat_jalans')
            op.drop_index(op.f('ix_surat_jalans_project_id'), table_name='surat_jalans')
            op.drop_index(op.f('ix_surat_jalans_tanggal_pengiriman'), table_name='surat_jalans')
            op.drop_index(op.f('ix_surat_jalans_nomor_form'), table_name='surat_jalans')
            op.drop_index(op.f('ix_surat_jalans_id'), table_name='surat_jalans')
            op.drop_table('surat_jalans')
            logger.info("✅ Tabel 'surat_jalans' berhasil dihapus")
        except Exception as e:
            logger.error(f"❌ Error menghapus tabel 'surat_jalans': {str(e)}")
            raise
    else:
        logger.info("Tabel 'surat_jalans' tidak ada, skip")
    
    logger.info("✅ Downgrade completed successfully")

