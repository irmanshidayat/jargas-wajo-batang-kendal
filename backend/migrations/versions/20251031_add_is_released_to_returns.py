"""add is_released to returns

Revision ID: add_is_released_returns_20251031
Revises: 
Create Date: 2025-10-31
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_is_released_returns_20251031'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('returns') as batch_op:
        batch_op.add_column(sa.Column('is_released', sa.Integer(), nullable=False, server_default='0'))
        batch_op.create_index('ix_returns_is_released', ['is_released'], unique=False)
    # Remove server default after setting initial values
    with op.batch_alter_table('returns') as batch_op:
        batch_op.alter_column('is_released', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('returns') as batch_op:
        batch_op.drop_index('ix_returns_is_released')
        batch_op.drop_column('is_released')


