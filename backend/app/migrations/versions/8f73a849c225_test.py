"""test

Revision ID: 8f73a849c225
Revises: 96583cee8382
Create Date: 2025-03-23 05:03:03.871529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f73a849c225'
down_revision: Union[str, None] = '96583cee8382'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
