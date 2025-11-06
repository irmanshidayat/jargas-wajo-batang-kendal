"""add_role_and_permission_tables

Revision ID: d3fea6ca00c1
Revises: 309b15867534
Create Date: 2025-11-01 07:59:08.878073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3fea6ca00c1'
down_revision: Union[str, None] = '309b15867534'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    # Create pages table
    op.create_table(
        'pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('path')
    )
    op.create_index(op.f('ix_pages_id'), 'pages', ['id'], unique=False)
    op.create_index(op.f('ix_pages_name'), 'pages', ['name'], unique=True)
    op.create_index(op.f('ix_pages_path'), 'pages', ['path'], unique=True)

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('page_id', sa.Integer(), nullable=False),
        sa.Column('can_create', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('can_read', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('can_update', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('can_delete', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)
    op.create_index(op.f('ix_permissions_page_id'), 'permissions', ['page_id'], unique=False)

    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission')
    )
    op.create_index(op.f('ix_role_permissions_id'), 'role_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_role_permissions_permission_id'), 'role_permissions', ['permission_id'], unique=False)
    op.create_index(op.f('ix_role_permissions_role_id'), 'role_permissions', ['role_id'], unique=False)

    # Create user_permissions table
    op.create_table(
        'user_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'permission_id', name='uq_user_permission')
    )
    op.create_index(op.f('ix_user_permissions_id'), 'user_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_user_permissions_permission_id'), 'user_permissions', ['permission_id'], unique=False)
    op.create_index(op.f('ix_user_permissions_user_id'), 'user_permissions', ['user_id'], unique=False)

    # Add role_id column to users table
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_users_role_id'), 'users', ['role_id'], unique=False)
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key and index for role_id in users table
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_role_id'), table_name='users')
    op.drop_column('users', 'role_id')

    # Drop user_permissions table
    op.drop_index(op.f('ix_user_permissions_user_id'), table_name='user_permissions')
    op.drop_index(op.f('ix_user_permissions_permission_id'), table_name='user_permissions')
    op.drop_index(op.f('ix_user_permissions_id'), table_name='user_permissions')
    op.drop_table('user_permissions')

    # Drop role_permissions table
    op.drop_index(op.f('ix_role_permissions_role_id'), table_name='role_permissions')
    op.drop_index(op.f('ix_role_permissions_permission_id'), table_name='role_permissions')
    op.drop_index(op.f('ix_role_permissions_id'), table_name='role_permissions')
    op.drop_table('role_permissions')

    # Drop permissions table
    op.drop_index(op.f('ix_permissions_page_id'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_id'), table_name='permissions')
    op.drop_table('permissions')

    # Drop pages table
    op.drop_index(op.f('ix_pages_path'), table_name='pages')
    op.drop_index(op.f('ix_pages_name'), table_name='pages')
    op.drop_index(op.f('ix_pages_id'), table_name='pages')
    op.drop_table('pages')

    # Drop roles table
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
