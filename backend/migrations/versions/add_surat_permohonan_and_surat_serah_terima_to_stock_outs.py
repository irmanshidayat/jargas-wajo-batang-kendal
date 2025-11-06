"""add_surat_permohonan_and_surat_serah_terima_paths_to_stock_outs

Revision ID: add_surat_permohonan_stock_outs
Revises: 2bcb46d867a0
Create Date: 2025-10-31 22:48:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_surat_permohonan_stock_outs'
down_revision: Union[str, None] = '2bcb46d867a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('stock_outs', sa.Column('surat_permohonan_paths', sa.Text(), nullable=True))
    op.add_column('stock_outs', sa.Column('surat_serah_terima_paths', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('stock_outs', 'surat_serah_terima_paths')
    op.drop_column('stock_outs', 'surat_permohonan_paths')

