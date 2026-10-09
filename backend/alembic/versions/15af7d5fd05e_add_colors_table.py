"""add colors table

Revision ID: 15af7d5fd05e
Revises: 0f98756f0977
Create Date: 2026-07-21 02:23:47.429332

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "15af7d5fd05e"
down_revision: Union[str, Sequence[str], None] = "0f98756f0977"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "colors",

        sa.Column(
            "name",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "slug",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "hex_code",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "rgb_value",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "color_family",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "undertone",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "brightness",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "saturation",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "description",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "is_neutral",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )

    op.create_index(
        op.f("ix_colors_id"),
        "colors",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_colors_id"),
        table_name="colors",
    )

    op.drop_table("colors")