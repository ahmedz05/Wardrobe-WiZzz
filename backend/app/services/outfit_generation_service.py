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

from app.services.style_matching_service import (
    evaluate_style_and_occasion,
)

from app.services.season_matching_service import (
    evaluate_season_and_warmth,
)

from app.services.weather_matching_service import (
    evaluate_item_weather,
)


OUTFIT_COMPATIBILITY_THRESHOLD = 70


# -------------------------
# PAIR SCORING WEIGHTS
# -------------------------

COLOR_WEIGHT = 0.25
GARMENT_WEIGHT = 0.25
STYLE_WEIGHT = 0.20
OCCASION_WEIGHT = 0.10
SEASON_WEIGHT = 0.10
WARMTH_WEIGHT = 0.10


# -------------------------
# FINAL OUTFIT WEIGHTS
# -------------------------

FASHION_SCORE_WEIGHT = 0.80
WEATHER_SCORE_WEIGHT = 0.20


WEATHER_BODY_CATEGORIES = {
    "Tops",
    "Bottoms",
    "Dresses & One Pieces",
    "Outerwear",
}


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
        "silhouette": item.silhouette,
        "layering_role": item.layering_role,
        "season": item.season,
        "warmth_level": item.warmth_level,
    }


def _calculate_dynamic_score(
    color_score: int,
    garment_score: int,
    style_score: int | None,
    occasion_score: int | None,
    season_score: int | None,
    warmth_score: int | None,
) -> dict:
    """
    Calculate the pair compatibility score.

    Missing optional metadata does not reduce
    the score. Missing weight is redistributed
    over the dimensions that are available.
    """

    dimensions = [
        {
            "name": "color",
            "score": color_score,
            "weight": COLOR_WEIGHT,
        },
        {
            "name": "garment",
            "score": garment_score,
            "weight": GARMENT_WEIGHT,
        },
    ]

    if style_score is not None:
        dimensions.append(
            {
                "name": "style",
                "score": style_score,
                "weight": STYLE_WEIGHT,
            }
        )

    if occasion_score is not None:
        dimensions.append(
            {
                "name": "occasion",
                "score": occasion_score,
                "weight": OCCASION_WEIGHT,
            }
        )

    if season_score is not None:
        dimensions.append(
            {
                "name": "season",
                "score": season_score,
                "weight": SEASON_WEIGHT,
            }
        )

    if warmth_score is not None:
        dimensions.append(
            {
                "name": "warmth",
                "score": warmth_score,
                "weight": WARMTH_WEIGHT,
            }
        )

    total_weight = sum(
        dimension["weight"]
        for dimension in dimensions
    )

    weighted_total = sum(
        dimension["score"]
        * dimension["weight"]
        for dimension in dimensions
    )

    final_score = round(
        weighted_total
        / total_weight
    )

    normalized_weights = {
        dimension["name"]: round(
            dimension["weight"]
            / total_weight,
            3,
        )
        for dimension in dimensions
    }

    return {
        "score": final_score,
        "weights_used": normalized_weights,
    }


def _evaluate_item_pair(
    first_item: Clothing,
    second_item: Clothing,
) -> dict:
    color_result = evaluate_color_pair(
        first_item.color,
        second_item.color,
    )

    garment_result = evaluate_garment_pair(
        first_item,
        second_item,
    )

    style_context = (
        evaluate_style_and_occasion(
            first_item,
            second_item,
        )
    )

    style_result = style_context[
        "style"
    ]

    occasion_result = style_context[
        "occasion"
    ]

    seasonal_context = (
        evaluate_season_and_warmth(
            first_item,
            second_item,
        )
    )

    season_result = seasonal_context[
        "season"
    ]

    warmth_result = seasonal_context[
        "warmth"
    ]

    scoring = _calculate_dynamic_score(
        color_score=color_result[
            "score"
        ],
        garment_score=garment_result[
            "score"
        ],
        style_score=style_result[
            "score"
        ],
        occasion_score=occasion_result[
            "score"
        ],
        season_score=season_result[
            "score"
        ],
        warmth_score=warmth_result[
            "score"
        ],
    )

    combined_score = scoring[
        "score"
    ]

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

        "weights_used": scoring[
            "weights_used"
        ],

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

        "style_match": {
            "score": style_result[
                "score"
            ],
            "compatible": style_result[
                "compatible"
            ],
            "relation": style_result[
                "relation"
            ],
            "style_1": style_result[
                "style_1"
            ],
            "style_2": style_result[
                "style_2"
            ],
            "reasons": style_result[
                "reasons"
            ],
        },

        "occasion_match": {
            "score": occasion_result[
                "score"
            ],
            "compatible": occasion_result[
                "compatible"
            ],
            "relation": occasion_result[
                "relation"
            ],
            "occasion_1": occasion_result[
                "occasion_1"
            ],
            "occasion_2": occasion_result[
                "occasion_2"
            ],
            "reasons": occasion_result[
                "reasons"
            ],
        },

        "season_match": {
            "score": season_result[
                "score"
            ],
            "compatible": season_result[
                "compatible"
            ],
            "relation": season_result[
                "relation"
            ],
            "season_1": season_result[
                "season_1"
            ],
            "season_2": season_result[
                "season_2"
            ],
            "reasons": season_result[
                "reasons"
            ],
        },

        "warmth_match": {
            "score": warmth_result[
                "score"
            ],
            "compatible": warmth_result[
                "compatible"
            ],
            "relation": warmth_result[
                "relation"
            ],
            "warmth_1": warmth_result[
                "warmth_1"
            ],
            "warmth_2": warmth_result[
                "warmth_2"
            ],
            "reasons": warmth_result[
                "reasons"
            ],
        },
    }


def _score_outfit(
    items: list[Clothing],
) -> dict:
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

    garment_roles_valid = all(
        result["garment_match"][
            "compatible"
        ]
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


def _evaluate_outfit_weather(
    items: list[Clothing],
    temperature_c: float | None,
    condition: str | None,
) -> dict:
    """
    Evaluate the complete outfit against
    external weather conditions.

    Shoes, accessories and bags are excluded
    from thermal scoring for now because their
    warmth metadata should not determine the
    body's overall temperature suitability.
    """

    if temperature_c is None:
        return {
            "score": None,
            "items_evaluated": 0,
            "analysis": [],
        }

    weather_items = [
        item
        for item in items
        if _get_category_name(item)
        in WEATHER_BODY_CATEGORIES
    ]

    analysis = []

    valid_scores = []

    for item in weather_items:
        result = evaluate_item_weather(
            item=item,
            temperature_c=temperature_c,
            condition=condition,
        )

        analysis.append(
            {
                "item": {
                    "id": item.id,
                    "name": item.name,
                },
                "weather_match": result,
            }
        )

        if result["score"] is not None:
            valid_scores.append(
                result["score"]
            )

    if not valid_scores:
        weather_score = None

    else:
        weather_score = round(
            sum(valid_scores)
            / len(valid_scores)
        )

    return {
        "score": weather_score,
        "items_evaluated": len(
            weather_items
        ),
        "analysis": analysis,
    }


def _combine_fashion_and_weather(
    fashion_score: int,
    weather_score: int | None,
) -> int:
    """
    Weather adjusts ranking but does not replace
    the core fashion intelligence score.
    """

    if weather_score is None:
        return fashion_score

    return round(
        fashion_score
        * FASHION_SCORE_WEIGHT
        +
        weather_score
        * WEATHER_SCORE_WEIGHT
    )


def _is_layer_candidate(
    item: Clothing,
) -> bool:
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


def _build_outfit_result(
    top: Clothing,
    bottom: Clothing,
    shoe: Clothing,
    layer: Clothing | None,
    outfit_result: dict,
    temperature_c: float | None,
    condition: str | None,
) -> dict:
    items = [
        top,
        bottom,
        shoe,
    ]

    if layer is not None:
        items.append(
            layer
        )

    weather_result = (
        _evaluate_outfit_weather(
            items=items,
            temperature_c=temperature_c,
            condition=condition,
        )
    )

    final_score = (
        _combine_fashion_and_weather(
            fashion_score=outfit_result[
                "score"
            ],
            weather_score=weather_result[
                "score"
            ],
        )
    )

    return {
        "score": final_score,

        "compatibility_score": outfit_result[
            "score"
        ],

        "weather_score": weather_result[
            "score"
        ],

        "has_layer": layer is not None,

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

            "layer": (
                _build_item_info(
                    layer
                )
                if layer is not None
                else None
            ),
        },

        "pair_analysis": outfit_result[
            "pair_analysis"
        ],

        "weather_analysis": weather_result[
            "analysis"
        ],
    }


def generate_outfits(
    db: Session,
    user_id: int,
    limit: int = 5,
    include_layers: bool = True,
    temperature_c: float | None = None,
    condition: str | None = None,
) -> dict:
    """
    Generate ranked outfits from a user's wardrobe.

    V2.2 considers:

        Color
        Garment roles
        Style
        Occasion
        Season
        Garment warmth
        External weather context

    Weather is optional.

    If weather is supplied, the final ranking is:

        80% fashion compatibility
        20% weather suitability
    """

    if (
        condition is not None
        and temperature_c is None
    ):
        raise ValueError(
            "temperature_c is required when "
            "a weather condition is provided."
        )

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

                if core_result[
                    "compatible"
                ]:
                    generated_outfits.append(
                        _build_outfit_result(
                            top=top,
                            bottom=bottom,
                            shoe=shoe,
                            layer=None,
                            outfit_result=core_result,
                            temperature_c=temperature_c,
                            condition=condition,
                        )
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
                        _build_outfit_result(
                            top=top,
                            bottom=bottom,
                            shoe=shoe,
                            layer=layer,
                            outfit_result=layered_result,
                            temperature_c=temperature_c,
                            condition=condition,
                        )
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

        "scoring_version": "2.2",

        "pair_scoring_dimensions": {
            "color": COLOR_WEIGHT,
            "garment_role": GARMENT_WEIGHT,
            "style": STYLE_WEIGHT,
            "occasion": OCCASION_WEIGHT,
            "season": SEASON_WEIGHT,
            "warmth": WARMTH_WEIGHT,
        },

        "final_ranking_dimensions": {
            "fashion_compatibility": (
                FASHION_SCORE_WEIGHT
            ),
            "weather_suitability": (
                WEATHER_SCORE_WEIGHT
            ),
        },

        "weather_context": {
            "enabled": (
                temperature_c is not None
            ),
            "temperature_c": temperature_c,
            "condition": condition,
        },

        "outfits": generated_outfits[
            :limit
        ],
    }