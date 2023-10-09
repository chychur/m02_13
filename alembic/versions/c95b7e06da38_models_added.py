"""Models added

Revision ID: c95b7e06da38
Revises: 85ef16dea3db
Create Date: 2023-10-07 20:49:26.565005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c95b7e06da38'
down_revision: Union[str, None] = '85ef16dea3db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
