"""add clothing metadata

Revision ID: 0f98756f0977
Revises: a29a933af622
Create Date: 2026-07-21 01:58:14.878685

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "0f98756f0977"
down_revision: Union[str, Sequence[str], None] = "a29a933af622"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "clothing",
        sa.Column(
            "condition",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "favorite",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "purchase_date",
            sa.Date(),
            nullable=True,
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "purchase_price",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "currency",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "last_worn",
            sa.Date(),
            nullable=True,
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "times_worn",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("clothing", "notes")
    op.drop_column("clothing", "times_worn")
    op.drop_column("clothing", "last_worn")
    op.drop_column("clothing", "currency")
    op.drop_column("clothing", "purchase_price")
    op.drop_column("clothing", "purchase_date")
    op.drop_column("clothing", "favorite")
    op.drop_column("clothing", "condition")