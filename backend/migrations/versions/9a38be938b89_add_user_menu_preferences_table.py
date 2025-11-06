"""add_user_menu_preferences_table

Revision ID: 9a38be938b89
Revises: c4f470eb2d52
Create Date: 2025-11-04 04:32:16.711415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a38be938b89'
down_revision: Union[str, None] = 'c4f470eb2d52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_menu_preferences table
    op.create_table(
        'user_menu_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('page_id', sa.Integer(), nullable=False),
        sa.Column('show_in_menu', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'page_id', name='uq_user_menu_preference')
    )
    op.create_index(op.f('ix_user_menu_preferences_id'), 'user_menu_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_user_menu_preferences_user_id'), 'user_menu_preferences', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_menu_preferences_page_id'), 'user_menu_preferences', ['page_id'], unique=False)


def downgrade() -> None:
    # Drop user_menu_preferences table
    op.drop_index(op.f('ix_user_menu_preferences_page_id'), table_name='user_menu_preferences')
    op.drop_index(op.f('ix_user_menu_preferences_user_id'), table_name='user_menu_preferences')
    op.drop_index(op.f('ix_user_menu_preferences_id'), table_name='user_menu_preferences')
    op.drop_table('user_menu_preferences')
