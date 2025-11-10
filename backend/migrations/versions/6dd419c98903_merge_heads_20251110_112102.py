"""merge_heads_20251110_112102

Revision ID: 6dd419c98903
Revises: 6d338d47c23b, add_status_surat_permintaan
Create Date: 2025-11-10 11:21:02.987627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6dd419c98903'
down_revision: Union[str, None] = ('6d338d47c23b', 'add_status_surat_permintaan')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
