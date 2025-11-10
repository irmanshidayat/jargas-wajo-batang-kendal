"""add_no_register_to_installed

Revision ID: 309b15867534
Revises: create_surat_jalan_tables
Create Date: 2025-11-01 06:14:15.428611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '309b15867534'
down_revision: Union[str, None] = 'create_surat_jalan_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column already exists (for safety)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('installed')]
    
    if 'no_register' not in columns:
        op.add_column('installed', sa.Column('no_register', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('installed', 'no_register')
