"""
Normalize clothing colors

Revision ID: c0e75e5e8daa
Revises: 15af7d5fd05e
Create Date: 2026-10-02 20:43:30.142857
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c0e75e5e8daa"
down_revision: Union[str, Sequence[str], None] = "15af7d5fd05e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Normalize clothing colors.

    Existing clothing.color values are converted into
    foreign keys pointing to the colors table.
    """

    # --------------------------------------------------
    # 1. Add the new color_id column
    # --------------------------------------------------

    op.add_column(
        "clothing",
        sa.Column(
            "color_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # --------------------------------------------------
    # 2. Seed the colors currently used by clothing items
    # --------------------------------------------------

    colors_table = sa.table(
        "colors",
        sa.column("name", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("hex_code", sa.String()),
        sa.column("rgb_value", sa.String()),
        sa.column("color_family", sa.String()),
        sa.column("undertone", sa.String()),
        sa.column("brightness", sa.String()),
        sa.column("saturation", sa.String()),
        sa.column("description", sa.String()),
        sa.column("is_neutral", sa.Boolean()),
        sa.column("is_active", sa.Boolean()),
    )

    op.bulk_insert(
        colors_table,
        [
            {
                "name": "Black",
                "slug": "black",
                "hex_code": "#000000",
                "rgb_value": "0, 0, 0",
                "color_family": "Black",
                "undertone": "Neutral",
                "brightness": "Dark",
                "saturation": "Low",
                "description": "A deep neutral black.",
                "is_neutral": True,
                "is_active": True,
            },
            {
                "name": "White",
                "slug": "white",
                "hex_code": "#FFFFFF",
                "rgb_value": "255, 255, 255",
                "color_family": "White",
                "undertone": "Neutral",
                "brightness": "Light",
                "saturation": "Low",
                "description": "A clean neutral white.",
                "is_neutral": True,
                "is_active": True,
            },
            {
                "name": "Blue",
                "slug": "blue",
                "hex_code": "#0000FF",
                "rgb_value": "0, 0, 255",
                "color_family": "Blue",
                "undertone": "Cool",
                "brightness": "Medium",
                "saturation": "High",
                "description": "A primary blue.",
                "is_neutral": False,
                "is_active": True,
            },
            {
                "name": "Light Blue",
                "slug": "light-blue",
                "hex_code": "#ADD8E6",
                "rgb_value": "173, 216, 230",
                "color_family": "Blue",
                "undertone": "Cool",
                "brightness": "Light",
                "saturation": "Medium",
                "description": "A lighter blue with a soft appearance.",
                "is_neutral": False,
                "is_active": True,
            },
            {
                "name": "Navy Blue",
                "slug": "navy-blue",
                "hex_code": "#000080",
                "rgb_value": "0, 0, 128",
                "color_family": "Blue",
                "undertone": "Cool",
                "brightness": "Dark",
                "saturation": "High",
                "description": "A deep dark blue.",
                "is_neutral": False,
                "is_active": True,
            },
        ],
    )

    # --------------------------------------------------
    # 3. Connect existing clothing rows to the new colors
    # --------------------------------------------------

    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE clothing
            SET color_id = colors.id
            FROM colors
            WHERE clothing.color = colors.name
            """
        )
    )

    # --------------------------------------------------
    # 4. Add the foreign key
    # --------------------------------------------------

    op.create_foreign_key(
        "fk_clothing_color_id_colors",
        "clothing",
        "colors",
        ["color_id"],
        ["id"],
    )

    # --------------------------------------------------
    # 5. Remove the old color string column
    # --------------------------------------------------

    op.drop_column(
        "clothing",
        "color",
    )


def downgrade() -> None:
    """
    Restore the original clothing.color string column.
    """

    # --------------------------------------------------
    # 1. Recreate the old color column
    # --------------------------------------------------

    op.add_column(
        "clothing",
        sa.Column(
            "color",
            sa.String(),
            nullable=True,
        ),
    )

    # --------------------------------------------------
    # 2. Restore color names from the colors table
    # --------------------------------------------------

    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE clothing
            SET color = colors.name
            FROM colors
            WHERE clothing.color_id = colors.id
            """
        )
    )

    # --------------------------------------------------
    # 3. Remove the foreign key
    # --------------------------------------------------

    op.drop_constraint(
        "fk_clothing_color_id_colors",
        "clothing",
        type_="foreignkey",
    )

    # --------------------------------------------------
    # 4. Remove color_id
    # --------------------------------------------------

    op.drop_column(
        "clothing",
        "color_id",
    )