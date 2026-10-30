# app/services/weather_matching_service.py


WARMTH_LEVELS = {
    "very light": 0,
    "light": 1,
    "medium": 2,
    "warm": 3,
    "heavy": 4,
}


RAIN_CONDITIONS = {
    "rain",
    "drizzle",
    "showers",
    "thunderstorm",
    "storm",
}


HOT_CONDITIONS = {
    "hot",
    "heat",
}


COLD_CONDITIONS = {
    "cold",
    "snow",
    "sleet",
    "freezing",
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


def get_target_warmth(
    temperature_c: float,
) -> dict:
    """
    Convert outside temperature into a target
    clothing warmth level.
    """

    if temperature_c >= 30:
        return {
            "level": "very light",
            "value": 0,
            "description": "Hot weather",
        }

    if temperature_c >= 24:
        return {
            "level": "light",
            "value": 1,
            "description": "Warm weather",
        }

    if temperature_c >= 17:
        return {
            "level": "medium",
            "value": 2,
            "description": "Mild weather",
        }

    if temperature_c >= 10:
        return {
            "level": "warm",
            "value": 3,
            "description": "Cool weather",
        }

    return {
        "level": "heavy",
        "value": 4,
        "description": "Cold weather",
    }


def evaluate_item_temperature(
    item,
    temperature_c: float,
) -> dict:
    """
    Evaluate whether an item's warmth level
    suits the outside temperature.
    """

    warmth = _normalize(
        item.warmth_level
    )

    if warmth is None:
        return {
            "score": None,
            "compatible": None,
            "relation": "Warmth Data Missing",
            "item_warmth": None,
            "target_warmth": None,
            "temperature_c": temperature_c,
            "reasons": [
                "The item does not have warmth metadata."
            ],
        }

    item_value = WARMTH_LEVELS.get(
        warmth
    )

    if item_value is None:
        return {
            "score": None,
            "compatible": None,
            "relation": "Unknown Warmth Level",
            "item_warmth": warmth,
            "target_warmth": None,
            "temperature_c": temperature_c,
            "reasons": [
                "The item's warmth level is not "
                "recognized by the weather engine."
            ],
        }

    target = get_target_warmth(
        temperature_c
    )

    difference = abs(
        item_value
        - target["value"]
    )

    if difference == 0:
        score = 100
        relation = "Ideal Temperature Match"

    elif difference == 1:
        score = 88
        relation = "Good Temperature Match"

    elif difference == 2:
        score = 68
        relation = "Temperature Compromise"

    elif difference == 3:
        score = 45
        relation = "Poor Temperature Match"

    else:
        score = 25
        relation = "Temperature Conflict"

    return {
        "score": score,
        "compatible": score >= 65,
        "relation": relation,
        "item_warmth": warmth,
        "target_warmth": target[
            "level"
        ],
        "temperature_c": temperature_c,
        "reasons": [
            f"{temperature_c}°C is classified as "
            f"{target['description'].lower()}, "
            f"with a target warmth level of "
            f"{target['level']}."
        ],
    }


def evaluate_weather_condition(
    item,
    condition: str | None,
) -> dict:
    """
    Interpret the weather condition without
    modifying the outfit score until the
    wardrobe contains enough metadata to make
    a reliable decision.

    Future versions can use:

        waterproof
        water_resistant
        material
        footwear type
        wind resistance
    """

    normalized_condition = _normalize(
        condition
    )

    if normalized_condition is None:
        return {
            "score": None,
            "compatible": None,
            "relation": "Weather Condition Missing",
            "condition": None,
            "reasons": [
                "No weather condition was provided."
            ],
        }

    words = set(
        normalized_condition.split()
    )

    is_rainy = bool(
        words & RAIN_CONDITIONS
    )

    if is_rainy:
        return {
            "score": None,
            "compatible": None,
            "relation": "Rain Detected",
            "condition": normalized_condition,
            "reasons": [
                "Rain was detected, but garment "
                "water-resistance metadata is not "
                "available yet, so rain does not "
                "change the score."
            ],
        }

    return {
        "score": None,
        "compatible": None,
        "relation": "Normal Conditions",
        "condition": normalized_condition,
        "reasons": [
            "No condition-specific clothing "
            "adjustment is currently required."
        ],
    }


def evaluate_item_weather(
    item,
    temperature_c: float,
    condition: str | None = None,
) -> dict:
    """
    Evaluate one wardrobe item against
    the supplied weather context.

    Temperature currently affects scoring.

    Weather conditions are retained as context
    but remain score-neutral until richer
    garment metadata is available.
    """

    temperature_result = (
        evaluate_item_temperature(
            item,
            temperature_c,
        )
    )

    condition_result = (
        evaluate_weather_condition(
            item,
            condition,
        )
    )

    available_scores = [
        score
        for score in [
            temperature_result[
                "score"
            ],
            condition_result[
                "score"
            ],
        ]
        if score is not None
    ]

    if not available_scores:
        final_score = None
        compatible = None

    else:
        final_score = round(
            sum(available_scores)
            / len(available_scores)
        )

        compatible = (
            final_score >= 65
        )

    return {
        "score": final_score,
        "compatible": compatible,
        "temperature": (
            temperature_result
        ),
        "condition": (
            condition_result
        ),
    }