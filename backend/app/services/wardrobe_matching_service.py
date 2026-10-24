from sqlalchemy.orm import Session

from app.models.clothing import Clothing

from app.services.color_matching_service import (
    evaluate_color_pair,
)

from app.services.garment_matching_service import (
    evaluate_garment_pair,
)


def _build_item_info(
    item: Clothing,
) -> dict:
    category_name = None
    subcategory_name = None

    if item.subcategory is not None:
        subcategory_name = item.subcategory.name

        if item.subcategory.category is not None:
            category_name = (
                item.subcategory.category.name
            )

    color_info = None

    if item.color is not None:
        color_info = {
            "id": item.color.id,
            "name": item.color.name,
            "hex_code": item.color.hex_code,
        }

    return {
        "id": item.id,
        "name": item.name,
        "category": category_name,
        "subcategory": subcategory_name,
        "color": color_info,
    }


def calculate_outfit_score(
    color_score: int,
    garment_score: int,
) -> int:
    """
    Combine color compatibility and garment-role
    compatibility into one outfit score.

    V1 weighting:
        50% color compatibility
        50% garment compatibility
    """

    final_score = (
        (color_score * 0.50)
        + (garment_score * 0.50)
    )

    return round(final_score)


def rank_wardrobe_color_matches(
    db: Session,
    user_id: int,
    clothing_id: int,
    limit: int = 10,
):
    """
    Rank clothing items in the user's wardrobe
    against a selected base item.

    Ranking considers:

    1. Color compatibility
    2. Garment-role compatibility
    3. Combined outfit score
    """

    base_item = (
        db.query(Clothing)
        .filter(
            Clothing.id == clothing_id,
            Clothing.user_id == user_id,
            Clothing.is_active.is_(True),
        )
        .first()
    )

    if base_item is None:
        raise ValueError(
            "Clothing item not found."
        )

    if base_item.color is None:
        raise ValueError(
            "The selected clothing item does not "
            "have a color assigned."
        )

    wardrobe_items = (
        db.query(Clothing)
        .filter(
            Clothing.user_id == user_id,
            Clothing.id != clothing_id,
            Clothing.is_active.is_(True),
        )
        .all()
    )

    matches = []

    for item in wardrobe_items:

        if item.color is None:
            continue

        # -------------------------
        # COLOR COMPATIBILITY
        # -------------------------

        color_result = evaluate_color_pair(
            base_item.color,
            item.color,
        )

        # -------------------------
        # GARMENT COMPATIBILITY
        # -------------------------

        garment_result = evaluate_garment_pair(
            base_item,
            item,
        )

        # -------------------------
        # FINAL OUTFIT SCORE
        # -------------------------

        final_score = calculate_outfit_score(
            color_score=color_result["score"],
            garment_score=garment_result["score"],
        )

        # A high color score should never make two
        # incompatible garment roles a valid outfit.
        final_compatible = (
            color_result["compatible"]
            and garment_result["compatible"]
            and final_score >= 70
        )

        matches.append(
            {
                "clothing": _build_item_info(
                    item
                ),

                "final_score": final_score,

                "compatible": final_compatible,

                "color_match": {
                    "score": color_result[
                        "score"
                    ],
                    "compatible": color_result[
                        "compatible"
                    ],
                    "harmony": color_result[
                        "harmony"
                    ],
                    "reasons": color_result[
                        "reasons"
                    ],
                },

                "garment_match": {
                    "score": garment_result[
                        "score"
                    ],
                    "compatible": garment_result[
                        "compatible"
                    ],
                    "relation": garment_result[
                        "relation"
                    ],
                    "reasons": garment_result[
                        "reasons"
                    ],
                },
            }
        )

    # Compatible outfits first,
    # then highest overall score.
    matches.sort(
        key=lambda item: (
            item["compatible"],
            item["final_score"],
        ),
        reverse=True,
    )

    return {
        "base_item": _build_item_info(
            base_item
        ),
        "matches": matches[:limit],
    }