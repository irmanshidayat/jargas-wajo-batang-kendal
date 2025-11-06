"""add_project_id_to_stock_ins_if_not_exists

Revision ID: 82290d859f86
Revises: ddf3b77ebeb4
Create Date: 2025-11-03 10:30:29.151185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '82290d859f86'
down_revision: Union[str, None] = 'ddf3b77ebeb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if project_id column already exists
    connection = op.get_bind()
    
    # Check if column exists
    result = connection.execute(text("""
        SELECT COUNT(*) as count
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'stock_ins'
        AND COLUMN_NAME = 'project_id'
    """))
    
    count = result.scalar()
    
    if count == 0:
        # Column doesn't exist, add it
        op.add_column('stock_ins', sa.Column('project_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_stock_ins_project_id'), 'stock_ins', ['project_id'], unique=False)
        
        # Try to add foreign key if projects table exists
        try:
            op.create_foreign_key(
                'fk_stock_ins_project_id',
                'stock_ins', 'projects',
                ['project_id'], ['id']
            )
        except Exception:
            # Foreign key might already exist or projects table doesn't exist yet
            pass


def downgrade() -> None:
    # Check if column exists before dropping
    connection = op.get_bind()
    
    result = connection.execute(text("""
        SELECT COUNT(*) as count
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'stock_ins'
        AND COLUMN_NAME = 'project_id'
    """))
    
    count = result.scalar()
    
    if count > 0:
        # Drop foreign key if exists
        try:
            op.drop_constraint('fk_stock_ins_project_id', 'stock_ins', type_='foreignkey')
        except Exception:
            pass
        
        # Drop index
        try:
            op.drop_index(op.f('ix_stock_ins_project_id'), table_name='stock_ins')
        except Exception:
            pass
        
        # Drop column
        op.drop_column('stock_ins', 'project_id')
