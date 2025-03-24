"""M

Revision ID: 96583cee8382
Revises: e1d7f38958df
Create Date: 2025-03-23 04:57:17.501895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96583cee8382'
down_revision: Union[str, None] = 'e1d7f38958df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
