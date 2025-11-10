"""
Migration Utilities - Helper Functions untuk Reusability

Fungsi-fungsi helper ini bisa digunakan di semua migration files
untuk memastikan konsistensi dan mengurangi duplikasi code.
"""
import logging
from typing import List, Optional, Tuple
from sqlalchemy import inspect, Engine, Connection

logger = logging.getLogger(__name__)


def table_exists(inspector: inspect.Inspector, table_name: str) -> bool:
    """
    Check if table exists in database
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table to check
    
    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        existing_tables = inspector.get_table_names()
        return table_name in existing_tables
    except Exception as e:
        logger.error(f"Error checking table existence: {str(e)}")
        return False


def column_exists(inspector: inspect.Inspector, table_name: str, column_name: str) -> bool:
    """
    Check if column exists in table
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
        column_name: Name of column to check
    
    Returns:
        bool: True if column exists, False otherwise
    """
    try:
        if not table_exists(inspector, table_name):
            return False
        existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in existing_columns
    except Exception as e:
        logger.error(f"Error checking column existence: {str(e)}")
        return False


def index_exists(inspector: inspect.Inspector, table_name: str, index_name: str) -> bool:
    """
    Check if index exists in table
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
        index_name: Name of index to check
    
    Returns:
        bool: True if index exists, False otherwise
    """
    try:
        if not table_exists(inspector, table_name):
            return False
        existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
        return index_name in existing_indexes
    except Exception as e:
        logger.error(f"Error checking index existence: {str(e)}")
        return False


def foreign_key_exists(inspector: inspect.Inspector, table_name: str, fk_name: str) -> bool:
    """
    Check if foreign key constraint exists
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
        fk_name: Name of foreign key constraint
    
    Returns:
        bool: True if foreign key exists, False otherwise
    """
    try:
        if not table_exists(inspector, table_name):
            return False
        existing_fks = [fk['name'] for fk in inspector.get_foreign_keys(table_name)]
        return fk_name in existing_fks
    except Exception as e:
        logger.error(f"Error checking foreign key existence: {str(e)}")
        return False


def get_table_columns(inspector: inspect.Inspector, table_name: str) -> List[str]:
    """
    Get list of column names in table
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
    
    Returns:
        List[str]: List of column names
    """
    try:
        if not table_exists(inspector, table_name):
            return []
        return [col['name'] for col in inspector.get_columns(table_name)]
    except Exception as e:
        logger.error(f"Error getting table columns: {str(e)}")
        return []


def get_table_indexes(inspector: inspect.Inspector, table_name: str) -> List[str]:
    """
    Get list of index names in table
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
    
    Returns:
        List[str]: List of index names
    """
    try:
        if not table_exists(inspector, table_name):
            return []
        return [idx['name'] for idx in inspector.get_indexes(table_name)]
    except Exception as e:
        logger.error(f"Error getting table indexes: {str(e)}")
        return []


def safe_add_column(
    inspector: inspect.Inspector,
    table_name: str,
    column_name: str,
    column_type,
    nullable: bool = True,
    server_default: Optional[str] = None
) -> bool:
    """
    Safely add column to table (idempotent)
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
        column_name: Name of column to add
        column_type: SQLAlchemy column type
        nullable: Whether column is nullable
        server_default: Server default value
    
    Returns:
        bool: True if column was added, False if already exists
    """
    from alembic import op
    import sqlalchemy as sa
    
    if not table_exists(inspector, table_name):
        logger.warning(f"Table '{table_name}' tidak ditemukan, skip add column")
        return False
    
    if column_exists(inspector, table_name, column_name):
        logger.info(f"Column '{column_name}' sudah ada di table '{table_name}', skip")
        return False
    
    try:
        column = sa.Column(column_name, column_type, nullable=nullable)
        if server_default:
            column.server_default = sa.text(server_default)
        
        op.add_column(table_name, column)
        logger.info(f"✅ Berhasil menambahkan kolom '{column_name}' ke table '{table_name}'")
        return True
    except Exception as e:
        logger.error(f"❌ Error menambahkan kolom '{column_name}': {str(e)}")
        if 'duplicate column' not in str(e).lower():
            raise
        return False


def safe_drop_column(
    inspector: inspect.Inspector,
    table_name: str,
    column_name: str
) -> bool:
    """
    Safely drop column from table (idempotent)
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
        column_name: Name of column to drop
    
    Returns:
        bool: True if column was dropped, False if doesn't exist
    """
    from alembic import op
    
    if not table_exists(inspector, table_name):
        logger.warning(f"Table '{table_name}' tidak ditemukan, skip drop column")
        return False
    
    if not column_exists(inspector, table_name, column_name):
        logger.info(f"Column '{column_name}' tidak ada di table '{table_name}', skip")
        return False
    
    try:
        op.drop_column(table_name, column_name)
        logger.info(f"✅ Berhasil menghapus kolom '{column_name}' dari table '{table_name}'")
        return True
    except Exception as e:
        logger.error(f"❌ Error menghapus kolom '{column_name}': {str(e)}")
        if 'unknown column' not in str(e).lower():
            raise
        return False


def safe_create_index(
    inspector: inspect.Inspector,
    table_name: str,
    index_name: str,
    columns: List[str],
    unique: bool = False
) -> bool:
    """
    Safely create index (idempotent)
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
        index_name: Name of index
        columns: List of column names
        unique: Whether index is unique
    
    Returns:
        bool: True if index was created, False if already exists
    """
    from alembic import op
    
    if not table_exists(inspector, table_name):
        logger.warning(f"Table '{table_name}' tidak ditemukan, skip create index")
        return False
    
    if index_exists(inspector, table_name, index_name):
        logger.info(f"Index '{index_name}' sudah ada, skip")
        return False
    
    try:
        op.create_index(index_name, table_name, columns, unique=unique)
        logger.info(f"✅ Berhasil membuat index '{index_name}'")
        return True
    except Exception as e:
        logger.error(f"❌ Error membuat index '{index_name}': {str(e)}")
        if 'duplicate key' not in str(e).lower():
            raise
        return False


def safe_drop_index(
    inspector: inspect.Inspector,
    table_name: str,
    index_name: str
) -> bool:
    """
    Safely drop index (idempotent)
    
    Args:
        inspector: SQLAlchemy Inspector instance
        table_name: Name of table
        index_name: Name of index to drop
    
    Returns:
        bool: True if index was dropped, False if doesn't exist
    """
    from alembic import op
    
    if not table_exists(inspector, table_name):
        logger.warning(f"Table '{table_name}' tidak ditemukan, skip drop index")
        return False
    
    if not index_exists(inspector, table_name, index_name):
        logger.info(f"Index '{index_name}' tidak ada, skip")
        return False
    
    try:
        op.drop_index(index_name, table_name=table_name)
        logger.info(f"✅ Berhasil menghapus index '{index_name}'")
        return True
    except Exception as e:
        logger.error(f"❌ Error menghapus index '{index_name}': {str(e)}")
        raise


def validate_migration_prerequisites(
    inspector: inspect.Inspector,
    required_tables: List[str],
    required_columns: Optional[dict] = None
) -> Tuple[bool, List[str]]:
    """
    Validate prerequisites sebelum migration
    
    Args:
        inspector: SQLAlchemy Inspector instance
        required_tables: List of required table names
        required_columns: Dict of {table_name: [column_names]}
    
    Returns:
        tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required tables
    for table_name in required_tables:
        if not table_exists(inspector, table_name):
            errors.append(f"Required table '{table_name}' tidak ditemukan")
    
    # Check required columns
    if required_columns:
        for table_name, columns in required_columns.items():
            if not table_exists(inspector, table_name):
                errors.append(f"Table '{table_name}' tidak ditemukan untuk column check")
                continue
            
            for column_name in columns:
                if not column_exists(inspector, table_name, column_name):
                    errors.append(f"Required column '{column_name}' tidak ditemukan di table '{table_name}'")
    
    return len(errors) == 0, errors

