"""add_surat_permohonan_and_surat_serah_terima_paths_to_stock_outs

Menambahkan kolom surat_permohonan_paths dan surat_serah_terima_paths 
ke tabel stock_outs untuk menyimpan path file surat permohonan dan surat serah terima.

Revision ID: add_surat_permohonan_stock_outs
Revises: 2bcb46d867a0
Create Date: 2025-10-31 22:48:00.000000
"""
import logging
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# Setup logger untuk migration
logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = 'add_surat_permohonan_stock_outs'
down_revision: Union[str, None] = '2bcb46d867a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade: Menambahkan kolom surat_permohonan_paths dan surat_serah_terima_paths
    ke tabel stock_outs.
    
    Best Practice:
    - Idempotent: Cek table dan column sebelum operasi
    - Safe: Handle error dengan logging yang proper
    - Nullable: Kolom dibuat nullable untuk backward compatibility
    """
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Safety check: Pastikan table stock_outs exists
    existing_tables = inspector.get_table_names()
    
    if 'stock_outs' not in existing_tables:
        logger.warning("Table 'stock_outs' tidak ditemukan, skip migration")
        return
    
    # Get existing columns untuk idempotency check
    existing_columns = [col['name'] for col in inspector.get_columns('stock_outs')]
    
    # Add surat_permohonan_paths column
    if 'surat_permohonan_paths' not in existing_columns:
        try:
            op.add_column(
                'stock_outs',
                sa.Column('surat_permohonan_paths', sa.Text(), nullable=True)
            )
            logger.info("✅ Berhasil menambahkan kolom 'surat_permohonan_paths'")
        except Exception as e:
            logger.error(f"❌ Error menambahkan kolom 'surat_permohonan_paths': {str(e)}")
            # Re-raise untuk fail migration jika memang error kritis
            # Atau pass jika memang sudah ada (idempotency)
            if 'duplicate column' not in str(e).lower():
                raise
    else:
        logger.info("Kolom 'surat_permohonan_paths' sudah ada, skip")
    
    # Add surat_serah_terima_paths column
    if 'surat_serah_terima_paths' not in existing_columns:
        try:
            op.add_column(
                'stock_outs',
                sa.Column('surat_serah_terima_paths', sa.Text(), nullable=True)
            )
            logger.info("✅ Berhasil menambahkan kolom 'surat_serah_terima_paths'")
        except Exception as e:
            logger.error(f"❌ Error menambahkan kolom 'surat_serah_terima_paths': {str(e)}")
            if 'duplicate column' not in str(e).lower():
                raise
    else:
        logger.info("Kolom 'surat_serah_terima_paths' sudah ada, skip")


def downgrade() -> None:
    """
    Downgrade: Menghapus kolom surat_permohonan_paths dan surat_serah_terima_paths
    dari tabel stock_outs.
    
    Best Practice:
    - Idempotent: Cek column sebelum drop
    - Safe: Handle error dengan logging
    - Order: Drop dalam urutan terbalik dari upgrade
    """
    connection = op.get_bind()
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Safety check: Pastikan table stock_outs exists
    if 'stock_outs' not in existing_tables:
        logger.warning("Table 'stock_outs' tidak ditemukan, skip downgrade")
        return
    
    # Get existing columns untuk idempotency check
    existing_columns = [col['name'] for col in inspector.get_columns('stock_outs')]
    
    # Drop surat_serah_terima_paths (drop yang terakhir ditambahkan dulu)
    if 'surat_serah_terima_paths' in existing_columns:
        try:
            op.drop_column('stock_outs', 'surat_serah_terima_paths')
            logger.info("✅ Berhasil menghapus kolom 'surat_serah_terima_paths'")
        except Exception as e:
            logger.error(f"❌ Error menghapus kolom 'surat_serah_terima_paths': {str(e)}")
            # Re-raise jika error kritis
            if 'unknown column' not in str(e).lower():
                raise
    else:
        logger.info("Kolom 'surat_serah_terima_paths' tidak ada, skip")
    
    # Drop surat_permohonan_paths
    if 'surat_permohonan_paths' in existing_columns:
        try:
            op.drop_column('stock_outs', 'surat_permohonan_paths')
            logger.info("✅ Berhasil menghapus kolom 'surat_permohonan_paths'")
        except Exception as e:
            logger.error(f"❌ Error menghapus kolom 'surat_permohonan_paths': {str(e)}")
            if 'unknown column' not in str(e).lower():
                raise
    else:
        logger.info("Kolom 'surat_permohonan_paths' tidak ada, skip")

