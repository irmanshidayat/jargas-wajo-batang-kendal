"""make kode_barang nullable in materials

Revision ID: 20251031_make_kode_barang_nullable
Revises: add_is_released_returns_20251031
Create Date: 2025-10-31
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251031_make_kode_barang_nullable'
down_revision = 'add_is_released_returns_20251031'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('materials') as batch_op:
        batch_op.alter_column('kode_barang', existing_type=sa.String(length=100), nullable=True)


def downgrade():
    with op.batch_alter_table('materials') as batch_op:
        batch_op.alter_column('kode_barang', existing_type=sa.String(length=100), nullable=False)


