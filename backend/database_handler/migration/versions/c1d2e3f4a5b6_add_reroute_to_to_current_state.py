"""add reroute_to to current_state

Revision ID: c1d2e3f4a5b6
Revises: d0e1f2a3b4c5
Create Date: 2026-07-24 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "current_state",
        sa.Column("reroute_to", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("current_state", "reroute_to")
