"""add_stock_out_fields_to_surat_jalan

Revision ID: d0b2b8eabbcb
Revises: 6dd419c98903
Create Date: 2025-11-10 11:46:03.852197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0b2b8eabbcb'
down_revision: Union[str, None] = '6dd419c98903'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add nomor_barang_keluar column (nullable, with index)
    op.add_column('surat_jalans', sa.Column('nomor_barang_keluar', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_surat_jalans_nomor_barang_keluar'), 'surat_jalans', ['nomor_barang_keluar'], unique=False)
    
    # Add stock_out_id column (nullable, with index and foreign key)
    op.add_column('surat_jalans', sa.Column('stock_out_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_surat_jalans_stock_out_id'), 'surat_jalans', ['stock_out_id'], unique=False)
    op.create_foreign_key(
        'fk_surat_jalans_stock_out_id',
        'surat_jalans',
        'stock_outs',
        ['stock_out_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop foreign key and index for stock_out_id
    op.drop_constraint('fk_surat_jalans_stock_out_id', 'surat_jalans', type_='foreignkey')
    op.drop_index(op.f('ix_surat_jalans_stock_out_id'), table_name='surat_jalans')
    op.drop_column('surat_jalans', 'stock_out_id')
    
    # Drop index and column for nomor_barang_keluar
    op.drop_index(op.f('ix_surat_jalans_nomor_barang_keluar'), table_name='surat_jalans')
    op.drop_column('surat_jalans', 'nomor_barang_keluar')
