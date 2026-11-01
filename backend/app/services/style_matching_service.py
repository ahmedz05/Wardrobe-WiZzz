# app/services/style_matching_service.py


STYLE_ALIASES = {
    "smart-casual": "smart casual",
    "smart casual": "smart casual",
    "business casual": "business casual",
    "business-casual": "business casual",
    "street wear": "streetwear",
    "street-wear": "streetwear",
    "athletic": "sporty",
}


OCCASION_ALIASES = {
    "daily": "everyday",
    "casual": "everyday",
    "office": "work",
    "business": "work",
    "gym": "sport",
    "sports": "sport",
    "night out": "party",
}


STYLE_RULES = {
    frozenset(
        {"casual", "streetwear"}
    ): (
        92,
        "Casual Streetwear Blend",
    ),

    frozenset(
        {"casual", "smart casual"}
    ): (
        90,
        "Elevated Casual",
    ),

    frozenset(
        {"casual", "minimalist"}
    ): (
        94,
        "Clean Casual",
    ),

    frozenset(
        {"casual", "sporty"}
    ): (
        88,
        "Sport Casual",
    ),

    frozenset(
        {"casual", "athleisure"}
    ): (
        92,
        "Athleisure Casual",
    ),

    frozenset(
        {"streetwear", "sporty"}
    ): (
        90,
        "Sport Streetwear",
    ),

    frozenset(
        {"streetwear", "athleisure"}
    ): (
        92,
        "Athleisure Streetwear",
    ),

    frozenset(
        {"streetwear", "minimalist"}
    ): (
        82,
        "Minimal Streetwear",
    ),

    frozenset(
        {"smart casual", "business casual"}
    ): (
        95,
        "Refined Casual",
    ),

    frozenset(
        {"smart casual", "formal"}
    ): (
        80,
        "Dressy Contrast",
    ),

    frozenset(
        {"business casual", "formal"}
    ): (
        88,
        "Professional Blend",
    ),

    frozenset(
        {"minimalist", "smart casual"}
    ): (
        92,
        "Clean Smart Casual",
    ),

    frozenset(
        {"minimalist", "formal"}
    ): (
        88,
        "Minimal Formal",
    ),

    frozenset(
        {"vintage", "casual"}
    ): (
        86,
        "Vintage Casual",
    ),

    frozenset(
        {"vintage", "streetwear"}
    ): (
        85,
        "Vintage Streetwear",
    ),

    frozenset(
        {"preppy", "smart casual"}
    ): (
        94,
        "Preppy Smart Casual",
    ),

    frozenset(
        {"preppy", "business casual"}
    ): (
        91,
        "Preppy Professional",
    ),
}


OCCASION_RULES = {
    frozenset(
        {"everyday", "work"}
    ): 82,

    frozenset(
        {"everyday", "travel"}
    ): 92,

    frozenset(
        {"everyday", "date"}
    ): 86,

    frozenset(
        {"everyday", "party"}
    ): 76,

    frozenset(
        {"work", "business"}
    ): 96,

    frozenset(
        {"work", "formal"}
    ): 88,

    frozenset(
        {"business", "formal"}
    ): 94,

    frozenset(
        {"date", "party"}
    ): 91,

    frozenset(
        {"travel", "outdoor"}
    ): 88,

    frozenset(
        {"sport", "outdoor"}
    ): 90,

    frozenset(
        {"sport", "everyday"}
    ): 80,
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


def _normalize_style(
    value: str | None,
) -> str | None:
    style = _normalize(value)

    if style is None:
        return None

    return STYLE_ALIASES.get(
        style,
        style,
    )


def _normalize_occasion(
    value: str | None,
) -> str | None:
    occasion = _normalize(value)

    if occasion is None:
        return None

    return OCCASION_ALIASES.get(
        occasion,
        occasion,
    )


def evaluate_style_pair(
    first_item,
    second_item,
) -> dict:
    """
    Evaluate style compatibility between
    two clothing items.

    Missing style information is not treated
    as a failure because older wardrobe items
    may not have style metadata yet.
    """

    first_style = _normalize_style(
        first_item.style
    )

    second_style = _normalize_style(
        second_item.style
    )

    if (
        first_style is None
        or second_style is None
    ):
        return {
            "score": None,
            "compatible": None,
            "relation": "Style Data Missing",
            "style_1": first_style,
            "style_2": second_style,
            "reasons": [
                "One or both items do not have style "
                "metadata, so style compatibility was "
                "not included in scoring."
            ],
        }

    if first_style == second_style:
        return {
            "score": 100,
            "compatible": True,
            "relation": "Same Style Direction",
            "style_1": first_style,
            "style_2": second_style,
            "reasons": [
                "Both items share the same style direction."
            ],
        }

    style_pair = frozenset(
        {
            first_style,
            second_style,
        }
    )

    rule = STYLE_RULES.get(
        style_pair
    )

    if rule is not None:
        score, relation = rule

        return {
            "score": score,
            "compatible": score >= 70,
            "relation": relation,
            "style_1": first_style,
            "style_2": second_style,
            "reasons": [
                f"{first_style.title()} and "
                f"{second_style.title()} can work "
                "together within the same outfit."
            ],
        }

    return {
        "score": 65,
        "compatible": True,
        "relation": "Mixed Style Direction",
        "style_1": first_style,
        "style_2": second_style,
        "reasons": [
            "The styles are not a known strong match, "
            "but the combination is not automatically "
            "rejected."
        ],
    }


def evaluate_occasion_pair(
    first_item,
    second_item,
) -> dict:
    """
    Evaluate whether two pieces target compatible
    occasions.

    Missing occasion information does not penalize
    the outfit.
    """

    first_occasion = _normalize_occasion(
        first_item.occasion
    )

    second_occasion = _normalize_occasion(
        second_item.occasion
    )

    if (
        first_occasion is None
        or second_occasion is None
    ):
        return {
            "score": None,
            "compatible": None,
            "relation": "Occasion Data Missing",
            "occasion_1": first_occasion,
            "occasion_2": second_occasion,
            "reasons": [
                "One or both items do not have occasion "
                "metadata, so occasion compatibility was "
                "not included in scoring."
            ],
        }

    if first_occasion == second_occasion:
        return {
            "score": 100,
            "compatible": True,
            "relation": "Same Occasion",
            "occasion_1": first_occasion,
            "occasion_2": second_occasion,
            "reasons": [
                "Both items are intended for the same "
                "type of occasion."
            ],
        }

    occasion_pair = frozenset(
        {
            first_occasion,
            second_occasion,
        }
    )

    score = OCCASION_RULES.get(
        occasion_pair
    )

    if score is not None:
        return {
            "score": score,
            "compatible": score >= 70,
            "relation": "Compatible Occasions",
            "occasion_1": first_occasion,
            "occasion_2": second_occasion,
            "reasons": [
                f"{first_occasion.title()} and "
                f"{second_occasion.title()} have "
                "compatible dress expectations."
            ],
        }

    return {
        "score": 60,
        "compatible": True,
        "relation": "Different Occasion Focus",
        "occasion_1": first_occasion,
        "occasion_2": second_occasion,
        "reasons": [
            "The pieces target different occasions, "
            "so the combination may depend on how "
            "the outfit is styled."
        ],
    }


def evaluate_style_and_occasion(
    first_item,
    second_item,
) -> dict:
    """
    Evaluate both style and occasion compatibility.
    """

    return {
        "style": evaluate_style_pair(
            first_item,
            second_item,
        ),
        "occasion": evaluate_occasion_pair(
            first_item,
            second_item,
        ),
    }