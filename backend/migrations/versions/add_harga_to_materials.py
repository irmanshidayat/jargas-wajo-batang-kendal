"""add_harga_to_materials

Revision ID: add_harga_materials
Revises: d0b2b8eabbcb
Create Date: 2025-01-22 10:00:00.000000

"""
import logging
from typing import Sequence, Union
from pathlib import Path
import sys

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import mysql

# Add migrations directory to path untuk import utils
migrations_dir = Path(__file__).parent.parent
sys.path.insert(0, str(migrations_dir.parent))

from migrations.utils import (
    table_exists,
    column_exists,
    safe_add_column,
    safe_drop_column
)

# Setup logger
logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = 'add_harga_materials'
down_revision: Union[str, None] = 'd0b2b8eabbcb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add harga column to materials table (DECIMAL 15,2 nullable)"""
    logger.info("Starting migration: add_harga_to_materials")
    
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Check if table exists
    if not table_exists(inspector, 'materials'):
        logger.warning("Table 'materials' tidak ditemukan, skip migration")
        return
    
    # Add harga column dengan safety check (idempotent)
    safe_add_column(
        inspector,
        'materials',
        'harga',
        sa.Numeric(precision=15, scale=2),
        nullable=True
    )
    
    logger.info("✅ Migration completed successfully")


def downgrade() -> None:
    """Drop harga column from materials table"""
    logger.info("Starting downgrade: add_harga_to_materials")
    
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Check if table exists
    if not table_exists(inspector, 'materials'):
        logger.warning("Table 'materials' tidak ditemukan, skip downgrade")
        return
    
    # Drop harga column dengan safety check (idempotent)
    safe_drop_column(inspector, 'materials', 'harga')
    
    logger.info("✅ Downgrade completed successfully")

