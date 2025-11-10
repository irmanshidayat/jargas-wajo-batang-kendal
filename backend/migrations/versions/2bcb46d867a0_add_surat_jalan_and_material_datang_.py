"""add_surat_jalan_and_material_datang_paths_to_stock_ins

Revision ID: 2bcb46d867a0
Revises: (base)
Create Date: 2025-10-31 22:37:33.876207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '2bcb46d867a0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Check if stock_ins table exists before adding columns
    existing_tables = inspector.get_table_names()
    
    if 'stock_ins' in existing_tables:
        # Check if columns already exist
        existing_columns = [col['name'] for col in inspector.get_columns('stock_ins')]
        
        if 'surat_jalan_paths' not in existing_columns:
            op.add_column('stock_ins', sa.Column('surat_jalan_paths', sa.Text(), nullable=True))
        
        if 'material_datang_paths' not in existing_columns:
            op.add_column('stock_ins', sa.Column('material_datang_paths', sa.Text(), nullable=True))
    
    # Check if users table exists before modifying
    if 'users' in existing_tables:
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'role' in existing_columns:
            # Check current type
            role_column = next((col for col in inspector.get_columns('users') if col['name'] == 'role'), None)
            if role_column:
                current_type = str(role_column['type'])
                # Only alter if it's not already an Enum
                if 'ENUM' not in current_type.upper() and 'userrole' not in current_type:
                    try:
                        op.alter_column('users', 'role',
                                   existing_type=mysql.VARCHAR(length=50),
                                   type_=sa.Enum('ADMIN', 'GUDANG', 'MANDOR', name='userrole'),
                                   existing_nullable=False,
                                   existing_server_default=sa.text("'gudang'"))
                    except Exception:
                        # If enum already exists or operation fails, skip
                        pass
        
        # Check if index exists before creating
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('users')]
        if 'ix_users_role' not in existing_indexes:
            try:
                op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
            except Exception:
                # Index might already exist or column doesn't support indexing
                pass


def downgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Check if users table exists
    if 'users' in existing_tables:
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('users')]
        if 'ix_users_role' in existing_indexes:
            try:
                op.drop_index(op.f('ix_users_role'), table_name='users')
            except Exception:
                pass
        
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        if 'role' in existing_columns:
            try:
                op.alter_column('users', 'role',
                           existing_type=sa.Enum('ADMIN', 'GUDANG', 'MANDOR', name='userrole'),
                           type_=mysql.VARCHAR(length=50),
                           existing_nullable=False,
                           existing_server_default=sa.text("'gudang'"))
            except Exception:
                pass
    
    # Check if stock_ins table exists
    if 'stock_ins' in existing_tables:
        existing_columns = [col['name'] for col in inspector.get_columns('stock_ins')]
        
        if 'material_datang_paths' in existing_columns:
            try:
                op.drop_column('stock_ins', 'material_datang_paths')
            except Exception:
                pass
        
        if 'surat_jalan_paths' in existing_columns:
            try:
                op.drop_column('stock_ins', 'surat_jalan_paths')
            except Exception:
                pass
