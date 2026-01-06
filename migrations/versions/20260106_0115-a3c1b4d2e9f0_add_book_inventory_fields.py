"""Add book inventory fields

Revision ID: a3c1b4d2e9f0
Revises: 9c5249293b89
Create Date: 2026-01-06 01:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a3c1b4d2e9f0"
down_revision: Union[str, Sequence[str], None] = "9c5249293b89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("books", sa.Column("publisher", sa.String(), nullable=True))
    op.add_column(
        "books",
        sa.Column("language", sa.String(), nullable=False, server_default=sa.text("'es'")),
    )
    op.add_column("books", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "books",
        sa.Column("stock", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("books", "stock")
    op.drop_column("books", "description")
    op.drop_column("books", "language")
    op.drop_column("books", "publisher")
