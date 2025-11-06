"""add_project_multi_tenant

Revision ID: 82b36e17b6fd
Revises: d3fea6ca00c1
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82b36e17b6fd'
down_revision: Union[str, None] = 'd3fea6ca00c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_code'), 'projects', ['code'], unique=True)

    # Create user_projects table
    op.create_table(
        'user_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_owner', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'project_id', name='uq_user_project')
    )
    op.create_index(op.f('ix_user_projects_id'), 'user_projects', ['id'], unique=False)
    op.create_index(op.f('ix_user_projects_user_id'), 'user_projects', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_projects_project_id'), 'user_projects', ['project_id'], unique=False)

    # Add project_id to materials table (nullable untuk backward compatibility)
    op.add_column('materials', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_materials_project_id'), 'materials', ['project_id'], unique=False)
    op.create_foreign_key('fk_materials_project_id', 'materials', 'projects', ['project_id'], ['id'])

    # Add project_id to mandors table
    op.add_column('mandors', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_mandors_project_id'), 'mandors', ['project_id'], unique=False)
    op.create_foreign_key('fk_mandors_project_id', 'mandors', 'projects', ['project_id'], ['id'])

    # Add project_id to stock_ins table
    op.add_column('stock_ins', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_stock_ins_project_id'), 'stock_ins', ['project_id'], unique=False)
    op.create_foreign_key('fk_stock_ins_project_id', 'stock_ins', 'projects', ['project_id'], ['id'])

    # Add project_id to stock_outs table
    op.add_column('stock_outs', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_stock_outs_project_id'), 'stock_outs', ['project_id'], unique=False)
    op.create_foreign_key('fk_stock_outs_project_id', 'stock_outs', 'projects', ['project_id'], ['id'])

    # Add project_id to installed table
    op.add_column('installed', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_installed_project_id'), 'installed', ['project_id'], unique=False)
    op.create_foreign_key('fk_installed_project_id', 'installed', 'projects', ['project_id'], ['id'])

    # Add project_id to returns table
    op.add_column('returns', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_returns_project_id'), 'returns', ['project_id'], unique=False)
    op.create_foreign_key('fk_returns_project_id', 'returns', 'projects', ['project_id'], ['id'])

    # Add project_id to audit_logs table
    op.add_column('audit_logs', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_audit_logs_project_id'), 'audit_logs', ['project_id'], unique=False)
    op.create_foreign_key('fk_audit_logs_project_id', 'audit_logs', 'projects', ['project_id'], ['id'])


def downgrade() -> None:
    # Drop foreign keys and indexes for project_id
    op.drop_constraint('fk_audit_logs_project_id', 'audit_logs', type_='foreignkey')
    op.drop_index(op.f('ix_audit_logs_project_id'), table_name='audit_logs')
    op.drop_column('audit_logs', 'project_id')

    op.drop_constraint('fk_returns_project_id', 'returns', type_='foreignkey')
    op.drop_index(op.f('ix_returns_project_id'), table_name='returns')
    op.drop_column('returns', 'project_id')

    op.drop_constraint('fk_installed_project_id', 'installed', type_='foreignkey')
    op.drop_index(op.f('ix_installed_project_id'), table_name='installed')
    op.drop_column('installed', 'project_id')

    op.drop_constraint('fk_stock_outs_project_id', 'stock_outs', type_='foreignkey')
    op.drop_index(op.f('ix_stock_outs_project_id'), table_name='stock_outs')
    op.drop_column('stock_outs', 'project_id')

    op.drop_constraint('fk_stock_ins_project_id', 'stock_ins', type_='foreignkey')
    op.drop_index(op.f('ix_stock_ins_project_id'), table_name='stock_ins')
    op.drop_column('stock_ins', 'project_id')

    op.drop_constraint('fk_mandors_project_id', 'mandors', type_='foreignkey')
    op.drop_index(op.f('ix_mandors_project_id'), table_name='mandors')
    op.drop_column('mandors', 'project_id')

    op.drop_constraint('fk_materials_project_id', 'materials', type_='foreignkey')
    op.drop_index(op.f('ix_materials_project_id'), table_name='materials')
    op.drop_column('materials', 'project_id')

    # Drop user_projects table
    op.drop_index(op.f('ix_user_projects_project_id'), table_name='user_projects')
    op.drop_index(op.f('ix_user_projects_user_id'), table_name='user_projects')
    op.drop_index(op.f('ix_user_projects_id'), table_name='user_projects')
    op.drop_table('user_projects')

    # Drop projects table
    op.drop_index(op.f('ix_projects_code'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')

