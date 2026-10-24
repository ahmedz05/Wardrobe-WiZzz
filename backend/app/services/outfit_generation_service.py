from itertools import combinations

from sqlalchemy.orm import Session, joinedload

from app.models.category import SubCategory
from app.models.clothing import Clothing

from app.services.color_matching_service import (
    evaluate_color_pair,
)

from app.services.garment_matching_service import (
    LAYERING_TOPS,
    evaluate_garment_pair,
)


OUTFIT_COMPATIBILITY_THRESHOLD = 70


def _get_category_name(
    item: Clothing,
) -> str | None:
    if item.subcategory is None:
        return None

    if item.subcategory.category is None:
        return None

    return item.subcategory.category.name


def _get_subcategory_name(
    item: Clothing,
) -> str | None:
    if item.subcategory is None:
        return None

    return item.subcategory.name


def _build_item_info(
    item: Clothing,
) -> dict:
    color = None

    if item.color is not None:
        color = {
            "id": item.color.id,
            "name": item.color.name,
            "hex_code": item.color.hex_code,
        }

    return {
        "id": item.id,
        "name": item.name,
        "category": _get_category_name(
            item
        ),
        "subcategory": _get_subcategory_name(
            item
        ),
        "color": color,
        "style": item.style,
        "occasion": item.occasion,
        "fit": item.fit,
    }


def _evaluate_item_pair(
    first_item: Clothing,
    second_item: Clothing,
) -> dict:
    """
    Combine color compatibility and garment-role
    compatibility for two clothing items.
    """

    color_result = evaluate_color_pair(
        first_item.color,
        second_item.color,
    )

    garment_result = evaluate_garment_pair(
        first_item,
        second_item,
    )

    combined_score = round(
        (
            color_result["score"]
            + garment_result["score"]
        )
        / 2
    )

    compatible = (
        garment_result["compatible"]
        and combined_score
        >= OUTFIT_COMPATIBILITY_THRESHOLD
    )

    return {
        "item_1": {
            "id": first_item.id,
            "name": first_item.name,
        },
        "item_2": {
            "id": second_item.id,
            "name": second_item.name,
        },
        "score": combined_score,
        "compatible": compatible,
        "color_score": color_result[
            "score"
        ],
        "color_harmony": color_result[
            "harmony"
        ],
        "garment_score": garment_result[
            "score"
        ],
        "garment_relation": garment_result[
            "relation"
        ],
    }


def _score_outfit(
    items: list[Clothing],
) -> dict:
    """
    Score a complete outfit by evaluating
    every pair of pieces inside it.
    """

    pair_results = []

    for first_item, second_item in combinations(
        items,
        2,
    ):
        pair_result = _evaluate_item_pair(
            first_item,
            second_item,
        )

        pair_results.append(
            pair_result
        )

    if not pair_results:
        return {
            "score": 0,
            "compatible": False,
            "pair_analysis": [],
        }

    total_score = sum(
        result["score"]
        for result in pair_results
    )

    outfit_score = round(
        total_score
        / len(pair_results)
    )

    # Garment-role conflicts should stop an
    # outfit from being recommended even when
    # its colors happen to work well.
    garment_roles_valid = all(
        result["compatible"]
        for result in pair_results
    )

    compatible = (
        garment_roles_valid
        and outfit_score
        >= OUTFIT_COMPATIBILITY_THRESHOLD
    )

    return {
        "score": outfit_score,
        "compatible": compatible,
        "pair_analysis": pair_results,
    }


def _is_layer_candidate(
    item: Clothing,
) -> bool:
    """
    Return True when an item can reasonably
    function as an additional layer.
    """

    category = _get_category_name(
        item
    )

    subcategory = _get_subcategory_name(
        item
    )

    if category == "Outerwear":
        return True

    if (
        category == "Tops"
        and subcategory in LAYERING_TOPS
    ):
        return True

    return False


def generate_outfits(
    db: Session,
    user_id: int,
    limit: int = 5,
    include_layers: bool = True,
) -> dict:
    """
    Generate ranked outfits from a user's wardrobe.

    V1 outfit structure:

        Top
        Bottom
        Shoes
        Optional Layer

    Future versions can add:
        dresses
        accessories
        bags
        weather
        occasion
        personal style
        fit
        silhouette
        history
        user feedback
    """

    wardrobe = (
        db.query(Clothing)
        .options(
            joinedload(
                Clothing.color
            ),
            joinedload(
                Clothing.subcategory
            ).joinedload(
                SubCategory.category
            ),
        )
        .filter(
            Clothing.user_id == user_id,
            Clothing.is_active.is_(True),
        )
        .all()
    )

    usable_items = [
        item
        for item in wardrobe
        if (
            item.color is not None
            and item.subcategory is not None
            and item.subcategory.category
            is not None
        )
    ]

    tops = [
        item
        for item in usable_items
        if _get_category_name(item)
        == "Tops"
    ]

    bottoms = [
        item
        for item in usable_items
        if _get_category_name(item)
        == "Bottoms"
    ]

    shoes = [
        item
        for item in usable_items
        if _get_category_name(item)
        == "Shoes"
    ]

    layers = [
        item
        for item in usable_items
        if _is_layer_candidate(item)
    ]

    if not tops:
        raise ValueError(
            "No usable tops found in the wardrobe."
        )

    if not bottoms:
        raise ValueError(
            "No usable bottoms found in the wardrobe."
        )

    if not shoes:
        raise ValueError(
            "No usable shoes found in the wardrobe."
        )

    generated_outfits = []

    for top in tops:
        for bottom in bottoms:
            for shoe in shoes:

                core_items = [
                    top,
                    bottom,
                    shoe,
                ]

                core_result = _score_outfit(
                    core_items
                )

                if core_result["compatible"]:
                    generated_outfits.append(
                        {
                            "score": core_result[
                                "score"
                            ],
                            "has_layer": False,
                            "items": {
                                "top": _build_item_info(
                                    top
                                ),
                                "bottom": _build_item_info(
                                    bottom
                                ),
                                "shoes": _build_item_info(
                                    shoe
                                ),
                                "layer": None,
                            },
                            "pair_analysis": (
                                core_result[
                                    "pair_analysis"
                                ]
                            ),
                        }
                    )

                if not include_layers:
                    continue

                for layer in layers:

                    if layer.id == top.id:
                        continue

                    layered_items = [
                        top,
                        bottom,
                        shoe,
                        layer,
                    ]

                    layered_result = (
                        _score_outfit(
                            layered_items
                        )
                    )

                    if not layered_result[
                        "compatible"
                    ]:
                        continue

                    generated_outfits.append(
                        {
                            "score": layered_result[
                                "score"
                            ],
                            "has_layer": True,
                            "items": {
                                "top": _build_item_info(
                                    top
                                ),
                                "bottom": _build_item_info(
                                    bottom
                                ),
                                "shoes": _build_item_info(
                                    shoe
                                ),
                                "layer": _build_item_info(
                                    layer
                                ),
                            },
                            "pair_analysis": (
                                layered_result[
                                    "pair_analysis"
                                ]
                            ),
                        }
                    )

    generated_outfits.sort(
        key=lambda outfit: outfit[
            "score"
        ],
        reverse=True,
    )

    return {
        "wardrobe_items_considered": len(
            usable_items
        ),
        "outfits_generated": len(
            generated_outfits
        ),
        "outfits": generated_outfits[
            :limit
        ],
    }