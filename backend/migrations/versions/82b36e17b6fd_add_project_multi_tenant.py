"""add_project_multi_tenant

Revision ID: 82b36e17b6fd
Revises: add_surat_permohonan_stock_outs
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union
import logging

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

logger = logging.getLogger(__name__)


# revision identifiers, used by Alembic.
revision: str = '82b36e17b6fd'
down_revision: Union[str, None] = '80cb2c36260b'  # Setelah migration users
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migration untuk menambahkan multi-tenant support dengan projects
    Pastikan tabel users sudah ada sebelum membuat user_projects
    """
    import logging
    logger = logging.getLogger(__name__)
    
    connection = op.get_bind()
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # CRITICAL: Pastikan tabel users sudah ada sebelum membuat user_projects
    if 'users' not in existing_tables:
        error_msg = "Tabel 'users' belum ada! Migration ini membutuhkan tabel users. Pastikan migration untuk membuat tabel users sudah dijalankan terlebih dahulu."
        logger.error(f"❌ {error_msg}")
        raise RuntimeError(error_msg)
    
    # Create projects table if it doesn't exist
    if 'projects' not in existing_tables:
        logger.info("Membuat tabel 'projects'...")
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
        logger.info("✅ Tabel 'projects' berhasil dibuat")
    else:
        logger.info("Tabel 'projects' sudah ada, skip")

    # Create user_projects table if it doesn't exist
    # Pastikan tabel users dan projects sudah ada
    if 'user_projects' not in existing_tables:
        if 'users' not in existing_tables:
            raise RuntimeError("Tabel 'users' belum ada! Migration ini membutuhkan tabel users.")
        if 'projects' not in existing_tables:
            raise RuntimeError("Tabel 'projects' belum ada! Migration ini membutuhkan tabel projects.")
        
        logger.info("Membuat tabel 'user_projects'...")
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
        logger.info("✅ Tabel 'user_projects' berhasil dibuat")
    else:
        logger.info("Tabel 'user_projects' sudah ada, skip")

    # Helper function to add project_id column safely
    def add_project_id_safely(table_name: str):
        if table_name in existing_tables:
            existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
            if 'project_id' not in existing_columns:
                try:
                    logger.info(f"Menambahkan kolom 'project_id' ke tabel '{table_name}'...")
                    op.add_column(table_name, sa.Column('project_id', sa.Integer(), nullable=True))
                    op.create_index(op.f(f'ix_{table_name}_project_id'), table_name, ['project_id'], unique=False)
                    # Pastikan tabel projects sudah ada sebelum membuat foreign key
                    if 'projects' in existing_tables:
                        op.create_foreign_key(f'fk_{table_name}_project_id', table_name, 'projects', ['project_id'], ['id'])
                    logger.info(f"✅ Kolom 'project_id' berhasil ditambahkan ke tabel '{table_name}'")
                except Exception as e:
                    # Column, index, or foreign key might already exist
                    logger.warning(f"⚠️  Warning saat menambahkan project_id ke {table_name}: {str(e)}")
                    # Jangan raise error, lanjutkan migration
            else:
                logger.info(f"Kolom 'project_id' sudah ada di tabel '{table_name}', skip")

    # Add project_id to materials table (nullable untuk backward compatibility)
    add_project_id_safely('materials')

    # Add project_id to mandors table
    add_project_id_safely('mandors')

    # Add project_id to stock_ins table
    add_project_id_safely('stock_ins')

    # Add project_id to stock_outs table
    add_project_id_safely('stock_outs')

    # Add project_id to installed table
    add_project_id_safely('installed')

    # Add project_id to returns table
    add_project_id_safely('returns')

    # Add project_id to audit_logs table
    add_project_id_safely('audit_logs')


def downgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Helper function to drop project_id column safely
    def drop_project_id_safely(table_name: str):
        if table_name in existing_tables:
            existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
            if 'project_id' in existing_columns:
                try:
                    op.drop_constraint(f'fk_{table_name}_project_id', table_name, type_='foreignkey')
                except Exception:
                    pass
                try:
                    op.drop_index(op.f(f'ix_{table_name}_project_id'), table_name=table_name)
                except Exception:
                    pass
                try:
                    op.drop_column(table_name, 'project_id')
                except Exception:
                    pass

    # Drop foreign keys and indexes for project_id
    drop_project_id_safely('audit_logs')
    drop_project_id_safely('returns')
    drop_project_id_safely('installed')
    drop_project_id_safely('stock_outs')
    drop_project_id_safely('stock_ins')
    drop_project_id_safely('mandors')
    drop_project_id_safely('materials')

    # Drop user_projects table if it exists
    if 'user_projects' in existing_tables:
        try:
            op.drop_index(op.f('ix_user_projects_project_id'), table_name='user_projects')
            op.drop_index(op.f('ix_user_projects_user_id'), table_name='user_projects')
            op.drop_index(op.f('ix_user_projects_id'), table_name='user_projects')
            op.drop_table('user_projects')
        except Exception:
            pass

    # Drop projects table if it exists
    if 'projects' in existing_tables:
        try:
            op.drop_index(op.f('ix_projects_code'), table_name='projects')
            op.drop_index(op.f('ix_projects_name'), table_name='projects')
            op.drop_index(op.f('ix_projects_id'), table_name='projects')
            op.drop_table('projects')
        except Exception:
            pass

