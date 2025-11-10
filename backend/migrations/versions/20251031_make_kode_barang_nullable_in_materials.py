"""make kode_barang nullable in materials

Revision ID: 20251031_make_kode_barang_nullable
Revises: 82290d859f86
Create Date: 2025-10-31
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251031_make_kode_barang_nullable'
down_revision: Union[str, None] = '82290d859f86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table('materials') as batch_op:
        batch_op.alter_column('kode_barang', existing_type=sa.String(length=100), nullable=True)


def downgrade():
    with op.batch_alter_table('materials') as batch_op:
        batch_op.alter_column('kode_barang', existing_type=sa.String(length=100), nullable=False)


