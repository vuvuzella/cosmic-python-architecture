"""merge head

Revision ID: 64dc4f62bc00
Revises: a3c55bc47f7d
Create Date: 2024-06-22 14:45:56.273000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64dc4f62bc00'
down_revision: Union[str, None] = 'a3c55bc47f7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
