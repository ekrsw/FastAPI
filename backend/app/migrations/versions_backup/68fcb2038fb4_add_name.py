"""add name

Revision ID: 68fcb2038fb4
Revises: bde913766c8b
Create Date: 2025-03-22 23:48:44.891881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68fcb2038fb4'
down_revision: Union[str, None] = 'bde913766c8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
