"""Add loan status, due_date and fine_amount

Revision ID: c4d8a1f0e2b3
Revises: b7f2c9d1a8e4
Create Date: 2026-01-06 02:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c4d8a1f0e2b3"
down_revision: Union[str, Sequence[str], None] = "b7f2c9d1a8e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    loanstatus = sa.Enum("ACTIVE", "RETURNED", "OVERDUE", name="loanstatus")
    if dialect == "postgresql":
        loanstatus.create(bind, checkfirst=True)

    op.add_column(
        "loans",
        sa.Column(
            "status",
            loanstatus,
            nullable=False,
            server_default=sa.text("'ACTIVE'"),
        ),
    )

    op.add_column("loans", sa.Column("fine_amount", sa.Numeric(10, 2), nullable=True))

    # Add due_date as nullable first to backfill existing rows.
    op.add_column("loans", sa.Column("due_date", sa.Date(), nullable=True))

    if dialect == "postgresql":
        op.execute(sa.text("UPDATE loans SET due_date = loan_dt + INTERVAL '14 days' WHERE due_date IS NULL"))
    else:
        # SQLite fallback: store as date string.
        op.execute(sa.text("UPDATE loans SET due_date = date(loan_dt, '+14 days') WHERE due_date IS NULL"))

    op.alter_column("loans", "due_date", existing_type=sa.Date(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    op.drop_column("loans", "due_date")
    op.drop_column("loans", "fine_amount")
    op.drop_column("loans", "status")

    loanstatus = sa.Enum("ACTIVE", "RETURNED", "OVERDUE", name="loanstatus")
    if dialect == "postgresql":
        loanstatus.drop(bind, checkfirst=True)
