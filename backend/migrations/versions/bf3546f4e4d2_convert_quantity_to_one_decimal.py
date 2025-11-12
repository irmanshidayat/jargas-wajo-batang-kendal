"""convert_quantity_to_one_decimal

Revision ID: bf3546f4e4d2
Revises: 9123ff100d53
Create Date: 2025-11-12 15:57:51.764573

"""
import logging
from typing import Sequence, Union
from pathlib import Path
import sys

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# Add migrations directory to path untuk import utils
migrations_dir = Path(__file__).parent.parent
sys.path.insert(0, str(migrations_dir.parent))

from migrations.utils import (
    table_exists,
    column_exists,
    index_exists,
    foreign_key_exists,
    safe_add_column,
    safe_drop_column,
    safe_create_index,
    safe_drop_index,
    get_table_columns,
    get_table_indexes,
    validate_migration_prerequisites
)

# Setup logger
logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = 'bf3546f4e4d2'
down_revision: Union[str, None] = '9123ff100d53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    logger.info(f"Starting migration: convert_quantity_to_one_decimal")
    connection = op.get_bind()
    inspector = inspect(connection)
    
    pass
    
    logger.info("✅ Migration completed successfully")


def downgrade() -> None:
    logger.info(f"Starting downgrade: convert_quantity_to_one_decimal")
    connection = op.get_bind()
    inspector = inspect(connection)
    
    pass
    
    logger.info("✅ Downgrade completed successfully")
