"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
import logging
from typing import Sequence, Union
from pathlib import Path
import sys

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
${imports if imports else ""}

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
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    logger.info(f"Starting migration: ${message}")
    connection = op.get_bind()
    inspector = inspect(connection)
    
    ${upgrades if upgrades else "pass"}
    
    logger.info("✅ Migration completed successfully")


def downgrade() -> None:
    logger.info(f"Starting downgrade: ${message}")
    connection = op.get_bind()
    inspector = inspect(connection)
    
    ${downgrades if downgrades else "pass"}
    
    logger.info("✅ Downgrade completed successfully")
