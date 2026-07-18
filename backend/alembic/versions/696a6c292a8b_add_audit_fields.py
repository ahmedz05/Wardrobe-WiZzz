"""Add audit fields

Revision ID: 696a6c292a8b
Revises: ea1e52fba78f
Create Date: 2026-07-18 15:11:02.004980
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "696a6c292a8b"
down_revision: Union[str, Sequence[str], None] = "ea1e52fba78f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # -------------------------
    # Categories
    # -------------------------
    op.add_column(
        "categories",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "categories",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.add_column(
        "categories",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # -------------------------
    # Clothing
    # -------------------------
    op.add_column(
        "clothing",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.add_column(
        "clothing",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # -------------------------
    # Subcategories
    # -------------------------
    op.add_column(
        "subcategories",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "subcategories",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.add_column(
        "subcategories",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # -------------------------
    # User Profiles
    # -------------------------
    op.add_column(
        "user_profiles",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "user_profiles",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.add_column(
        "user_profiles",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # -------------------------
    # Users
    # -------------------------
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Users
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "is_active")

    # User Profiles
    op.drop_column("user_profiles", "updated_at")
    op.drop_column("user_profiles", "created_at")
    op.drop_column("user_profiles", "is_active")

    # Subcategories
    op.drop_column("subcategories", "updated_at")
    op.drop_column("subcategories", "created_at")
    op.drop_column("subcategories", "is_active")

    # Clothing
    op.drop_column("clothing", "updated_at")
    op.drop_column("clothing", "created_at")
    op.drop_column("clothing", "is_active")

    # Categories
    op.drop_column("categories", "updated_at")
    op.drop_column("categories", "created_at")
    op.drop_column("categories", "is_active")