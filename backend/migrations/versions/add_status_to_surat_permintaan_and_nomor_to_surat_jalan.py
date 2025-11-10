"""add_status_to_surat_permintaan_and_nomor_to_surat_jalan

Revision ID: add_status_surat_permintaan
Revises: 309b15867534
Create Date: 2025-01-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_status_surat_permintaan'
down_revision: Union[str, None] = '309b15867534'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add status column to surat_permintaans table
    op.add_column('surat_permintaans', sa.Column('status', sa.String(length=50), nullable=False, server_default='Draft'))
    op.create_index(op.f('ix_surat_permintaans_status'), 'surat_permintaans', ['status'], unique=False)
    
    # Add nomor_surat_permintaan column to surat_jalans table
    op.add_column('surat_jalans', sa.Column('nomor_surat_permintaan', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_surat_jalans_nomor_surat_permintaan'), 'surat_jalans', ['nomor_surat_permintaan'], unique=False)


def downgrade() -> None:
    # Drop index and column from surat_jalans
    op.drop_index(op.f('ix_surat_jalans_nomor_surat_permintaan'), table_name='surat_jalans')
    op.drop_column('surat_jalans', 'nomor_surat_permintaan')
    
    # Drop index and column from surat_permintaans
    op.drop_index(op.f('ix_surat_permintaans_status'), table_name='surat_permintaans')
    op.drop_column('surat_permintaans', 'status')



