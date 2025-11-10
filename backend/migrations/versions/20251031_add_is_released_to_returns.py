"""add is_released to returns

Revision ID: add_is_released_returns_20251031
Revises: ddf3b77ebeb4
Create Date: 2025-10-31
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_is_released_returns_20251031'
down_revision: Union[str, None] = 'ddf3b77ebeb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if returns table exists and if column already exists
    try:
        connection = op.get_bind()
        inspector = sa.inspect(connection)
        tables = inspector.get_table_names()
        
        if 'returns' not in tables:
            # Tabel returns belum ada, skip migration ini
            # Migration ini seharusnya dijalankan setelah tabel returns dibuat
            return
        
        # Check if column already exists
        columns = [col['name'] for col in inspector.get_columns('returns')]
        if 'is_released' in columns:
            # Column sudah ada, skip
            return
        
        # Add column if table exists and column doesn't exist
        with op.batch_alter_table('returns') as batch_op:
            batch_op.add_column(sa.Column('is_released', sa.Integer(), nullable=False, server_default='0'))
            batch_op.create_index('ix_returns_is_released', ['is_released'], unique=False)
        # Remove server default after setting initial values
        with op.batch_alter_table('returns') as batch_op:
            batch_op.alter_column('is_released', server_default=None)
    except Exception as e:
        # Jika terjadi error (misalnya tabel tidak ada atau kolom sudah ada), skip
        # Migration akan dijalankan lagi jika diperlukan
        pass


def downgrade() -> None:
    with op.batch_alter_table('returns') as batch_op:
        batch_op.drop_index('ix_returns_is_released')
        batch_op.drop_column('is_released')


