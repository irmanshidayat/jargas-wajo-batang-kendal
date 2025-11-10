"""convert_quantity_to_decimal

Revision ID: 6d338d47c23b
Revises: c4f470eb2d52
Create Date: 2025-11-05 08:45:25.561663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '6d338d47c23b'
down_revision: Union[str, None] = 'c4f470eb2d52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert surat_permintaan_items.qty from INTEGER to DECIMAL(10,2)
    op.alter_column('surat_permintaan_items', 'qty',
                    type_=sa.Numeric(10, 2),
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    postgresql_using='qty::numeric(10,2)',
                    mysql_using='CAST(qty AS DECIMAL(10,2))')
    
    # Convert stock_ins.quantity from INTEGER to DECIMAL(10,2)
    op.alter_column('stock_ins', 'quantity',
                    type_=sa.Numeric(10, 2),
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    postgresql_using='quantity::numeric(10,2)',
                    mysql_using='CAST(quantity AS DECIMAL(10,2))')
    
    # Convert stock_outs.quantity from INTEGER to DECIMAL(10,2)
    op.alter_column('stock_outs', 'quantity',
                    type_=sa.Numeric(10, 2),
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    postgresql_using='quantity::numeric(10,2)',
                    mysql_using='CAST(quantity AS DECIMAL(10,2))')
    
    # Convert installed.quantity from INTEGER to DECIMAL(10,2)
    op.alter_column('installed', 'quantity',
                    type_=sa.Numeric(10, 2),
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    postgresql_using='quantity::numeric(10,2)',
                    mysql_using='CAST(quantity AS DECIMAL(10,2))')
    
    # Convert returns.quantity_kembali from INTEGER to DECIMAL(10,2)
    op.alter_column('returns', 'quantity_kembali',
                    type_=sa.Numeric(10, 2),
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    postgresql_using='quantity_kembali::numeric(10,2)',
                    mysql_using='CAST(quantity_kembali AS DECIMAL(10,2))')
    
    # Convert returns.quantity_kondisi_baik from INTEGER to DECIMAL(10,2)
    op.alter_column('returns', 'quantity_kondisi_baik',
                    type_=sa.Numeric(10, 2),
                    existing_type=sa.Integer(),
                    existing_nullable=True,
                    postgresql_using='quantity_kondisi_baik::numeric(10,2)',
                    mysql_using='CAST(quantity_kondisi_baik AS DECIMAL(10,2))')
    
    # Convert returns.quantity_kondisi_reject from INTEGER to DECIMAL(10,2)
    op.alter_column('returns', 'quantity_kondisi_reject',
                    type_=sa.Numeric(10, 2),
                    existing_type=sa.Integer(),
                    existing_nullable=True,
                    postgresql_using='quantity_kondisi_reject::numeric(10,2)',
                    mysql_using='CAST(quantity_kondisi_reject AS DECIMAL(10,2))')


def downgrade() -> None:
    # Convert back to INTEGER - MySQL will truncate decimal part
    op.alter_column('returns', 'quantity_kondisi_reject',
                    type_=sa.Integer(),
                    existing_type=sa.Numeric(10, 2),
                    existing_nullable=True,
                    mysql_using='CAST(quantity_kondisi_reject AS UNSIGNED)')
    
    op.alter_column('returns', 'quantity_kondisi_baik',
                    type_=sa.Integer(),
                    existing_type=sa.Numeric(10, 2),
                    existing_nullable=True,
                    mysql_using='CAST(quantity_kondisi_baik AS UNSIGNED)')
    
    op.alter_column('returns', 'quantity_kembali',
                    type_=sa.Integer(),
                    existing_type=sa.Numeric(10, 2),
                    existing_nullable=False,
                    mysql_using='CAST(quantity_kembali AS UNSIGNED)')
    
    op.alter_column('installed', 'quantity',
                    type_=sa.Integer(),
                    existing_type=sa.Numeric(10, 2),
                    existing_nullable=False,
                    mysql_using='CAST(quantity AS UNSIGNED)')
    
    op.alter_column('stock_outs', 'quantity',
                    type_=sa.Integer(),
                    existing_type=sa.Numeric(10, 2),
                    existing_nullable=False,
                    mysql_using='CAST(quantity AS UNSIGNED)')
    
    op.alter_column('stock_ins', 'quantity',
                    type_=sa.Integer(),
                    existing_type=sa.Numeric(10, 2),
                    existing_nullable=False,
                    mysql_using='CAST(quantity AS UNSIGNED)')
    
    op.alter_column('surat_permintaan_items', 'qty',
                    type_=sa.Integer(),
                    existing_type=sa.Numeric(10, 2),
                    existing_nullable=False,
                    mysql_using='CAST(qty AS UNSIGNED)')
