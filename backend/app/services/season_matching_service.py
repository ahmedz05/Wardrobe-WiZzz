from app.services.garment_matching_service import (
    LAYERING_TOPS,
)


SEASON_ALIASES = {
    "fall": "autumn",
    "autumn": "autumn",
    "spring": "spring",
    "summer": "summer",
    "winter": "winter",
    "all season": "all-season",
    "all seasons": "all-season",
    "all-season": "all-season",
    "year round": "all-season",
    "year-round": "all-season",
}


WARMTH_LEVELS = {
    "very light": 0,
    "light": 1,
    "medium": 2,
    "warm": 3,
    "heavy": 4,
}


SEASON_COMPATIBILITY = {
    frozenset(
        {"spring", "summer"}
    ): 90,

    frozenset(
        {"spring", "autumn"}
    ): 85,

    frozenset(
        {"autumn", "winter"}
    ): 92,

    frozenset(
        {"summer", "autumn"}
    ): 72,

    frozenset(
        {"spring", "winter"}
    ): 65,

    frozenset(
        {"summer", "winter"}
    ): 35,
}


NON_THERMAL_CATEGORIES = {
    "Shoes",
    "Accessories",
    "Bags",
}


OUTERWEAR_BASE_CATEGORIES = {
    "Tops",
    "Dresses & One Pieces",
}


def _normalize(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = value.strip().lower()

    if not cleaned:
        return None

    return cleaned


def _normalize_season(
    value: str | None,
) -> str | None:
    season = _normalize(value)

    if season is None:
        return None

    return SEASON_ALIASES.get(
        season,
        season,
    )


def _normalize_warmth(
    value: str | None,
) -> str | None:
    return _normalize(value)


def _get_category_name(
    item,
) -> str | None:
    if item.subcategory is None:
        return None

    if item.subcategory.category is None:
        return None

    return item.subcategory.category.name


def _get_subcategory_name(
    item,
) -> str | None:
    if item.subcategory is None:
        return None

    return item.subcategory.name


def _get_layering_relationship(
    first_item,
    second_item,
):
    """
    Determine whether one garment is functioning
    as a layer over the other.

    Returns:

        layer_item, base_item

    or:

        None, None
    """

    first_category = _get_category_name(
        first_item
    )

    second_category = _get_category_name(
        second_item
    )

    first_subcategory = _get_subcategory_name(
        first_item
    )

    second_subcategory = _get_subcategory_name(
        second_item
    )

    # Outerwear only forms a true layering
    # relationship with upper-body garments
    # or one-piece garments.
    #
    # Example:
    # T-shirt + Jacket -> layering
    # Hoodie + Jacket -> layering
    # Dress + Jacket -> layering
    # Jeans + Jacket -> NOT layering

    if (
        first_category == "Outerwear"
        and second_category
        in OUTERWEAR_BASE_CATEGORIES
    ):
        return (
            first_item,
            second_item,
        )

    if (
        second_category == "Outerwear"
        and first_category
        in OUTERWEAR_BASE_CATEGORIES
    ):
        return (
            second_item,
            first_item,
        )

    # Two tops can form a layering relationship
    # when one is a known layering garment.
    if (
        first_category == "Tops"
        and second_category == "Tops"
    ):
        first_is_layer = (
            first_subcategory
            in LAYERING_TOPS
        )

        second_is_layer = (
            second_subcategory
            in LAYERING_TOPS
        )

        if (
            first_is_layer
            and not second_is_layer
        ):
            return (
                first_item,
                second_item,
            )

        if (
            second_is_layer
            and not first_is_layer
        ):
            return (
                second_item,
                first_item,
            )

    return (
        None,
        None,
    )


def evaluate_season_pair(
    first_item,
    second_item,
) -> dict:
    """
    Evaluate whether two clothing items
    belong to compatible seasons.
    """

    first_season = _normalize_season(
        first_item.season
    )

    second_season = _normalize_season(
        second_item.season
    )

    if (
        first_season is None
        or second_season is None
    ):
        return {
            "score": None,
            "compatible": None,
            "relation": "Season Data Missing",
            "season_1": first_season,
            "season_2": second_season,
            "reasons": [
                "One or both items do not have season "
                "metadata, so season compatibility was "
                "not included in scoring."
            ],
        }

    if first_season == second_season:
        return {
            "score": 100,
            "compatible": True,
            "relation": "Same Season",
            "season_1": first_season,
            "season_2": second_season,
            "reasons": [
                "Both items are intended for the same "
                "season."
            ],
        }

    if (
        first_season == "all-season"
        or second_season == "all-season"
    ):
        return {
            "score": 96,
            "compatible": True,
            "relation": "All-Season Compatible",
            "season_1": first_season,
            "season_2": second_season,
            "reasons": [
                "At least one item is suitable for "
                "year-round use."
            ],
        }

    season_pair = frozenset(
        {
            first_season,
            second_season,
        }
    )

    score = SEASON_COMPATIBILITY.get(
        season_pair,
        65,
    )

    if score >= 80:
        relation = "Compatible Seasons"

    elif score >= 65:
        relation = "Seasonal Compromise"

    else:
        relation = "Season Conflict"

    return {
        "score": score,
        "compatible": score >= 65,
        "relation": relation,
        "season_1": first_season,
        "season_2": second_season,
        "reasons": [
            f"{first_season.title()} and "
            f"{second_season.title()} have a "
            f"season compatibility score of {score}."
        ],
    }


def _evaluate_layering_warmth(
    first_item,
    second_item,
    layer_item,
    base_item,
) -> dict:
    """
    Evaluate warmth specifically for layering.

    A layer being warmer than its base garment
    is expected and should usually be rewarded.
    """

    layer_warmth = _normalize_warmth(
        layer_item.warmth_level
    )

    base_warmth = _normalize_warmth(
        base_item.warmth_level
    )

    layer_value = WARMTH_LEVELS[
        layer_warmth
    ]

    base_value = WARMTH_LEVELS[
        base_warmth
    ]

    warmth_difference = (
        layer_value
        - base_value
    )

    if warmth_difference == 0:
        score = 88
        relation = "Equal Layer Warmth"

        reason = (
            "The layer and base garment have "
            "similar warmth."
        )

    elif warmth_difference == 1:
        score = 100
        relation = "Ideal Layering Warmth"

        reason = (
            "The outer layer is slightly warmer "
            "than the base garment."
        )

    elif warmth_difference == 2:
        score = 96
        relation = "Strong Layering Warmth"

        reason = (
            "The outer layer provides meaningful "
            "extra warmth over the base garment."
        )

    elif warmth_difference == 3:
        score = 90
        relation = "High Layering Contrast"

        reason = (
            "The layer is much warmer than the "
            "base garment, which can work well "
            "in colder conditions."
        )

    elif warmth_difference >= 4:
        score = 82
        relation = "Heavy Layering Contrast"

        reason = (
            "The layer is substantially warmer "
            "than the base garment."
        )

    elif warmth_difference == -1:
        score = 72
        relation = "Reverse Warmth Balance"

        reason = (
            "The identified layer is slightly "
            "lighter than the base garment."
        )

    else:
        score = 55
        relation = "Poor Layering Warmth"

        reason = (
            "The identified outer layer is "
            "significantly lighter than the base."
        )

    return {
        "score": score,
        "compatible": score >= 65,
        "relation": relation,

        # These always correspond to the
        # original pair order.
        "warmth_1": _normalize_warmth(
            first_item.warmth_level
        ),

        "warmth_2": _normalize_warmth(
            second_item.warmth_level
        ),

        "reasons": [
            reason
        ],
    }


def evaluate_warmth_pair(
    first_item,
    second_item,
) -> dict:
    """
    Evaluate thermal compatibility.

    Warmth is interpreted differently for:

    - layering relationships
    - normal garment relationships
    - categories where thermal comparison
      does not provide useful information
    """

    first_warmth = _normalize_warmth(
        first_item.warmth_level
    )

    second_warmth = _normalize_warmth(
        second_item.warmth_level
    )

    if (
        first_warmth is None
        or second_warmth is None
    ):
        return {
            "score": None,
            "compatible": None,
            "relation": "Warmth Data Missing",
            "warmth_1": first_warmth,
            "warmth_2": second_warmth,
            "reasons": [
                "One or both items do not have warmth "
                "metadata, so warmth compatibility was "
                "not included in scoring."
            ],
        }

    if (
        first_warmth not in WARMTH_LEVELS
        or second_warmth not in WARMTH_LEVELS
    ):
        return {
            "score": None,
            "compatible": None,
            "relation": "Unknown Warmth Level",
            "warmth_1": first_warmth,
            "warmth_2": second_warmth,
            "reasons": [
                "One or both warmth levels are not "
                "recognized by the current engine."
            ],
        }

    first_category = _get_category_name(
        first_item
    )

    second_category = _get_category_name(
        second_item
    )

    # Shoes, bags and accessories do not
    # meaningfully contribute to this
    # garment warmth comparison.
    if (
        first_category
        in NON_THERMAL_CATEGORIES
        or second_category
        in NON_THERMAL_CATEGORIES
    ):
        return {
            "score": None,
            "compatible": None,
            "relation": "Warmth Not Relevant",
            "warmth_1": first_warmth,
            "warmth_2": second_warmth,
            "reasons": [
                "Warmth comparison is not meaningful "
                "for this garment-category pairing."
            ],
        }

    layer_item, base_item = (
        _get_layering_relationship(
            first_item,
            second_item,
        )
    )

    if (
        layer_item is not None
        and base_item is not None
    ):
        return _evaluate_layering_warmth(
            first_item=first_item,
            second_item=second_item,
            layer_item=layer_item,
            base_item=base_item,
        )

    first_value = WARMTH_LEVELS[
        first_warmth
    ]

    second_value = WARMTH_LEVELS[
        second_warmth
    ]

    difference = abs(
        first_value
        - second_value
    )

    if difference == 0:
        score = 100
        relation = "Same Warmth Level"

    elif difference == 1:
        score = 92
        relation = "Balanced Warmth"

    elif difference == 2:
        score = 78
        relation = "Moderate Warmth Contrast"

    elif difference == 3:
        score = 65
        relation = "High Warmth Contrast"

    else:
        score = 55
        relation = "Warmth Conflict"

    return {
        "score": score,
        "compatible": score >= 65,
        "relation": relation,
        "warmth_1": first_warmth,
        "warmth_2": second_warmth,
        "reasons": [
            f"The garments differ by {difference} "
            "warmth level(s)."
        ],
    }


def evaluate_season_and_warmth(
    first_item,
    second_item,
) -> dict:
    """
    Evaluate seasonal and thermal compatibility.
    """

    return {
        "season": evaluate_season_pair(
            first_item,
            second_item,
        ),

        "warmth": evaluate_warmth_pair(
            first_item,
            second_item,
        ),
    }