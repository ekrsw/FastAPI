"""M

Revision ID: 3f3f7a2b19b4
Revises: 68fcb2038fb4
Create Date: 2025-03-22 23:57:49.710362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f3f7a2b19b4'
down_revision: Union[str, None] = '68fcb2038fb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
