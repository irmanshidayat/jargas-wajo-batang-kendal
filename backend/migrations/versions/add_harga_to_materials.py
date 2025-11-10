"""add_harga_to_materials

Revision ID: add_harga_materials
Revises: d0b2b8eabbcb
Create Date: 2025-01-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'add_harga_materials'
down_revision: Union[str, None] = 'd0b2b8eabbcb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add harga column to materials table (DECIMAL 15,2 nullable)
    op.add_column('materials', sa.Column('harga', sa.Numeric(precision=15, scale=2), nullable=True))


def downgrade() -> None:
    # Drop harga column from materials table
    op.drop_column('materials', 'harga')

