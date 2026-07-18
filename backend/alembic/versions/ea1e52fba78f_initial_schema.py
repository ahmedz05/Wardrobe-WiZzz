"""Add clothing taxonomy

Revision ID: ea1e52fba78f
Revises:
Create Date: 2026-07-18 14:25:24.947340
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ea1e52fba78f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add new clothing taxonomy fields
    op.add_column(
        "clothing",
        sa.Column("subcategory_id", sa.Integer(), nullable=True)
    )

    op.add_column(
        "clothing",
        sa.Column("fit", sa.String(), nullable=True)
    )

    op.add_column(
        "clothing",
        sa.Column("material", sa.String(), nullable=True)
    )

    op.add_column(
        "clothing",
        sa.Column("silhouette", sa.String(), nullable=True)
    )

    op.add_column(
        "clothing",
        sa.Column("layering_role", sa.String(), nullable=True)
    )

    op.add_column(
        "clothing",
        sa.Column("warmth_level", sa.String(), nullable=True)
    )

    op.add_column(
        "clothing",
        sa.Column("occasion", sa.String(), nullable=True)
    )

    # Create foreign key
    op.create_foreign_key(
        "fk_clothing_subcategory",
        "clothing",
        "subcategories",
        ["subcategory_id"],
        ["id"],
    )

    # Remove old category column
    op.drop_column(
        "clothing",
        "category"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Restore old category column
    op.add_column(
        "clothing",
        sa.Column(
            "category",
            sa.String(),
            nullable=False
        )
    )

    # Remove foreign key
    op.drop_constraint(
        "fk_clothing_subcategory",
        "clothing",
        type_="foreignkey",
    )

    # Remove new columns
    op.drop_column("clothing", "occasion")
    op.drop_column("clothing", "warmth_level")
    op.drop_column("clothing", "layering_role")
    op.drop_column("clothing", "silhouette")
    op.drop_column("clothing", "material")
    op.drop_column("clothing", "fit")
    op.drop_column("clothing", "subcategory_id")