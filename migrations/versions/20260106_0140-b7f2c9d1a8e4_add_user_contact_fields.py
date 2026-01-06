"""Add user contact fields

Revision ID: b7f2c9d1a8e4
Revises: a3c1b4d2e9f0
Create Date: 2026-01-06 01:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b7f2c9d1a8e4"
down_revision: Union[str, Sequence[str], None] = "a3c1b4d2e9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(), nullable=True))
    op.add_column("users", sa.Column("address", sa.String(), nullable=True))
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    # Backfill email for existing rows, keeping uniqueness.
    op.execute(sa.text("UPDATE users SET email = username || '@example.com' WHERE email IS NULL"))

    op.alter_column("users", "email", existing_type=sa.String(), nullable=False)
    op.create_unique_constraint(op.f("uq_users_email"), "users", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_users_email"), "users", type_="unique")
    op.drop_column("users", "is_active")
    op.drop_column("users", "address")
    op.drop_column("users", "phone")
    op.drop_column("users", "email")
