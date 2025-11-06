"""add_show_in_menu_to_pages

Revision ID: c4f470eb2d52
Revises: 82290d859f86
Create Date: 2025-11-04 04:21:55.660930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4f470eb2d52'
down_revision: Union[str, None] = '82290d859f86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
