"""add backdrop urls to entertainment

Revision ID: c4b8f9a1d2e3
Revises: 59e789422cda
Create Date: 2026-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4b8f9a1d2e3"
down_revision: Union[str, Sequence[str], None] = "59e789422cda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "entertainment",
        sa.Column("backdrop_url", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("entertainment", "backdrop_url")
