import colorsys

from app.models.color import Color


COMPATIBILITY_THRESHOLD = 75


def _hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    """
    Convert a HEX color such as #ADD8E6
    into an RGB tuple.
    """
    cleaned = hex_code.strip().lstrip("#")

    if len(cleaned) != 6:
        raise ValueError(
            f"Invalid HEX color: {hex_code}"
        )

    try:
        return (
            int(cleaned[0:2], 16),
            int(cleaned[2:4], 16),
            int(cleaned[4:6], 16),
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid HEX color: {hex_code}"
        ) from exc


def _get_hue(hex_code: str) -> float:
    """
    Return hue in degrees from 0 to 360.
    """
    red, green, blue = _hex_to_rgb(
        hex_code
    )

    red /= 255
    green /= 255
    blue /= 255

    hue, _, _ = colorsys.rgb_to_hsv(
        red,
        green,
        blue,
    )

    return hue * 360


def _hue_distance(
    first_hue: float,
    second_hue: float,
) -> float:
    """
    Return the shortest distance between
    two colors on the color wheel.
    """
    difference = abs(
        first_hue - second_hue
    )

    return min(
        difference,
        360 - difference,
    )


def _normalize(
    value: str | None,
) -> str:
    if value is None:
        return ""

    return value.strip().lower()


def _brightness_difference(
    first_color: Color,
    second_color: Color,
) -> int:
    levels = {
        "dark": 0,
        "medium": 1,
        "light": 2,
    }

    first = levels.get(
        _normalize(
            first_color.brightness
        )
    )

    second = levels.get(
        _normalize(
            second_color.brightness
        )
    )

    if first is None or second is None:
        return 0

    return abs(
        first - second
    )


def _build_color_info(
    color: Color,
) -> dict:
    return {
        "id": color.id,
        "name": color.name,
        "hex_code": color.hex_code,
        "color_family": color.color_family,
        "undertone": color.undertone,
        "brightness": color.brightness,
        "saturation": color.saturation,
        "is_neutral": color.is_neutral,
    }


def evaluate_color_pair(
    first_color: Color,
    second_color: Color,
) -> dict:
    """
    Evaluate how well two wardrobe colors
    work together.
    """

    if not first_color.is_active:
        raise ValueError(
            f"{first_color.name} is inactive."
        )

    if not second_color.is_active:
        raise ValueError(
            f"{second_color.name} is inactive."
        )

    reasons = []

    first_neutral = bool(
        first_color.is_neutral
    )

    second_neutral = bool(
        second_color.is_neutral
    )

    # -------------------------
    # SAME COLOR
    # -------------------------

    if first_color.id == second_color.id:
        score = 90
        harmony = "Monochromatic"

        reasons.append(
            "Both pieces use the same color, "
            "creating a monochromatic look."
        )

    # -------------------------
    # TWO NEUTRALS
    # -------------------------

    elif (
        first_neutral
        and second_neutral
    ):
        score = 92
        harmony = "Neutral Pairing"

        reasons.append(
            "Both colors are neutrals and can "
            "be combined easily."
        )

    # -------------------------
    # NEUTRAL + COLOR
    # -------------------------

    elif (
        first_neutral
        or second_neutral
    ):
        score = 94
        harmony = "Neutral Balance"

        neutral_color = (
            first_color
            if first_neutral
            else second_color
        )

        accent_color = (
            second_color
            if first_neutral
            else first_color
        )

        reasons.append(
            f"{neutral_color.name} acts as a "
            f"neutral base for "
            f"{accent_color.name}."
        )

        reasons.append(
            "Neutral colors give stronger colors "
            "space to stand out without competing."
        )

    # -------------------------
    # COLOR WHEEL
    # -------------------------

    else:
        first_hue = _get_hue(
            first_color.hex_code
        )

        second_hue = _get_hue(
            second_color.hex_code
        )

        distance = _hue_distance(
            first_hue,
            second_hue,
        )

        if distance <= 15:
            score = 88
            harmony = "Monochromatic"

            reasons.append(
                "The colors have very similar hues, "
                "creating a cohesive tonal look."
            )

        elif distance <= 45:
            score = 93
            harmony = "Analogous"

            reasons.append(
                "The colors sit close together on "
                "the color wheel and create "
                "a smooth harmony."
            )

        elif distance <= 75:
            score = 82
            harmony = "Soft Contrast"

            reasons.append(
                "The colors create gentle contrast "
                "while remaining balanced."
            )

        elif distance <= 135:
            score = 84
            harmony = "Balanced Contrast"

            reasons.append(
                "The colors create noticeable "
                "contrast without directly "
                "opposing each other."
            )

        elif distance <= 165:
            score = 88
            harmony = "Strong Contrast"

            reasons.append(
                "The colors create strong "
                "visual contrast."
            )

        else:
            score = 96
            harmony = "Complementary"

            reasons.append(
                "The colors sit close to opposite "
                "sides of the color wheel."
            )

    # -------------------------
    # UNDERTONE
    # -------------------------

    first_undertone = _normalize(
        first_color.undertone
    )

    second_undertone = _normalize(
        second_color.undertone
    )

    if (
        first_undertone
        and second_undertone
        and first_undertone
        == second_undertone
    ):
        score += 3

        reasons.append(
            "The colors share the same undertone."
        )

    elif (
        first_undertone == "neutral"
        or second_undertone == "neutral"
    ):
        score += 1

        reasons.append(
            "A neutral undertone helps the colors "
            "work together flexibly."
        )

    # -------------------------
    # BRIGHTNESS
    # -------------------------

    brightness_difference = (
        _brightness_difference(
            first_color,
            second_color,
        )
    )

    if brightness_difference == 2:
        score += 3

        reasons.append(
            "The light-dark contrast adds "
            "visual depth."
        )

    elif brightness_difference == 1:
        score += 1

        reasons.append(
            "The brightness difference gives "
            "the combination visual separation."
        )

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    return {
        "color_1": _build_color_info(
            first_color
        ),
        "color_2": _build_color_info(
            second_color
        ),
        "score": score,
        "compatible": (
            score
            >= COMPATIBILITY_THRESHOLD
        ),
        "harmony": harmony,
        "reasons": reasons,
    }


def rank_color_matches(
    base_color: Color,
    colors: list[Color],
    limit: int = 5,
) -> list[dict]:
    """
    Rank available colors from best to worst
    for a given base color.
    """

    matches = []

    for color in colors:
        if not color.is_active:
            continue

        if color.id == base_color.id:
            continue

        result = evaluate_color_pair(
            base_color,
            color,
        )

        matches.append(
            {
                "color": _build_color_info(
                    color
                ),
                "score": result["score"],
                "compatible": result[
                    "compatible"
                ],
                "harmony": result[
                    "harmony"
                ],
                "reasons": result[
                    "reasons"
                ],
            }
        )

    matches.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return matches[:limit]