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
    # Check if table exists before modifying
    from sqlalchemy import inspect
    
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if table exists first
    existing_tables = inspector.get_table_names()
    if 'installed' not in existing_tables:
        # Table doesn't exist, skip this migration
        # The table will be created by another migration or auto-created from models
        return
    
    # Check if column already exists (for safety)
    existing_columns = [col['name'] for col in inspector.get_columns('installed')]
    if 'no_register' not in existing_columns:
        op.add_column('installed', sa.Column('no_register', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Check if table exists before modifying
    from sqlalchemy import inspect
    
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if table and column exist before dropping
    existing_tables = inspector.get_table_names()
    if 'installed' in existing_tables:
        existing_columns = [col['name'] for col in inspector.get_columns('installed')]
        if 'no_register' in existing_columns:
            op.drop_column('installed', 'no_register')
