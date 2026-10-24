# app/services/garment_matching_service.py


# Tops that commonly behave as an additional layer.
LAYERING_TOPS = {
    "Overshirt",
    "Hoodie",
    "Zip Hoodie",
    "Sweatshirt",
    "Crewneck",
    "Sweater",
    "Cardigan",
    "Vest",
}


# Tops that commonly behave as a base or primary top.
BASE_TOPS = {
    "T-Shirt",
    "Oversized T-Shirt",
    "Graphic T-Shirt",
    "Long Sleeve T-Shirt",
    "Shirt",
    "Oxford Shirt",
    "Flannel Shirt",
    "Linen Shirt",
    "Polo Shirt",
    "Turtleneck",
    "Tank Top",
    "Blouse",
    "Crop Top",
}


def _get_category_name(item):
    """
    Return the item's parent category name.

    Example:
        Clothing -> SubCategory -> Category -> "Tops"
    """

    if item.subcategory is None:
        return None

    if item.subcategory.category is None:
        return None

    return item.subcategory.category.name


def _get_subcategory_name(item):
    """
    Return the item's subcategory name.
    """

    if item.subcategory is None:
        return None

    return item.subcategory.name


def _evaluate_two_tops(
    first_subcategory: str | None,
    second_subcategory: str | None,
) -> dict:
    """
    Decide whether two tops make sense together
    as a layered outfit.
    """

    if (
        first_subcategory is None
        or second_subcategory is None
    ):
        return {
            "score": 40,
            "compatible": False,
            "relation": "Unknown Top Layering",
            "reasons": [
                "Both pieces are tops, but their subcategories "
                "are missing so layering compatibility cannot "
                "be determined."
            ],
        }

    first_is_layer = (
        first_subcategory in LAYERING_TOPS
    )

    second_is_layer = (
        second_subcategory in LAYERING_TOPS
    )

    first_is_base = (
        first_subcategory in BASE_TOPS
    )

    second_is_base = (
        second_subcategory in BASE_TOPS
    )

    if (
        first_is_layer
        and second_is_base
    ) or (
        second_is_layer
        and first_is_base
    ):
        return {
            "score": 88,
            "compatible": True,
            "relation": "Layered Tops",
            "reasons": [
                "One piece can function as a base top while "
                "the other can function as an additional layer."
            ],
        }

    if (
        first_is_layer
        and second_is_layer
    ):
        return {
            "score": 50,
            "compatible": False,
            "relation": "Competing Layers",
            "reasons": [
                "Both tops behave primarily as layering pieces, "
                "so they may compete for the same outfit role."
            ],
        }

    if (
        first_is_base
        and second_is_base
    ):
        return {
            "score": 35,
            "compatible": False,
            "relation": "Competing Base Tops",
            "reasons": [
                "Both pieces normally occupy the same base-top "
                "position in an outfit."
            ],
        }

    return {
        "score": 45,
        "compatible": False,
        "relation": "Same Garment Role",
        "reasons": [
            "Both pieces belong to the Tops category and do not "
            "have a recognized layering relationship."
        ],
    }


def evaluate_garment_pair(
    first_item,
    second_item,
) -> dict:
    """
    Evaluate whether two clothing items make sense
    together based on garment roles.

    This does not evaluate color.
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

    # -------------------------
    # MISSING CATEGORY DATA
    # -------------------------

    if (
        first_category is None
        or second_category is None
    ):
        return {
            "score": 50,
            "compatible": False,
            "relation": "Unknown Garment Roles",
            "category_1": first_category,
            "subcategory_1": first_subcategory,
            "category_2": second_category,
            "subcategory_2": second_subcategory,
            "reasons": [
                "One or both clothing items do not have enough "
                "category information to evaluate outfit roles."
            ],
        }

    # -------------------------
    # SAME CATEGORY
    # -------------------------

    if first_category == second_category:

        if first_category == "Tops":
            result = _evaluate_two_tops(
                first_subcategory,
                second_subcategory,
            )

        elif first_category == "Accessories":
            result = {
                "score": 75,
                "compatible": True,
                "relation": "Multiple Accessories",
                "reasons": [
                    "Multiple accessories can usually coexist "
                    "when they serve different styling purposes."
                ],
            }

        elif first_category == "Bottoms":
            result = {
                "score": 20,
                "compatible": False,
                "relation": "Competing Bottoms",
                "reasons": [
                    "Both pieces occupy the bottom garment role."
                ],
            }

        elif first_category == "Shoes":
            result = {
                "score": 10,
                "compatible": False,
                "relation": "Competing Footwear",
                "reasons": [
                    "An outfit normally uses one pair of shoes."
                ],
            }

        elif first_category == "Outerwear":
            result = {
                "score": 30,
                "compatible": False,
                "relation": "Competing Outerwear",
                "reasons": [
                    "Both pieces primarily occupy the outerwear "
                    "role."
                ],
            }

        elif first_category == "Dresses & One Pieces":
            result = {
                "score": 10,
                "compatible": False,
                "relation": "Competing One Pieces",
                "reasons": [
                    "Both garments are designed to function as "
                    "the primary one-piece garment."
                ],
            }

        elif first_category == "Bags":
            result = {
                "score": 20,
                "compatible": False,
                "relation": "Competing Bags",
                "reasons": [
                    "Most outfits normally use one primary bag."
                ],
            }

        else:
            result = {
                "score": 40,
                "compatible": False,
                "relation": "Same Garment Role",
                "reasons": [
                    "Both pieces occupy the same general "
                    "garment role."
                ],
            }

    # -------------------------
    # DIFFERENT CATEGORIES
    # -------------------------

    else:
        category_pair = frozenset(
            {
                first_category,
                second_category,
            }
        )

        compatibility_rules = {
            frozenset(
                {"Tops", "Bottoms"}
            ): (
                100,
                "Core Outfit Pair",
                "A top and a bottom form the core structure "
                "of a standard outfit.",
            ),

            frozenset(
                {"Tops", "Outerwear"}
            ): (
                95,
                "Layering Pair",
                "Outerwear can naturally layer over a top.",
            ),

            frozenset(
                {"Tops", "Shoes"}
            ): (
                85,
                "Outfit Support Pair",
                "Shoes can coordinate with the upper half "
                "of an outfit.",
            ),

            frozenset(
                {"Tops", "Accessories"}
            ): (
                80,
                "Styling Pair",
                "Accessories can support and refine a top.",
            ),

            frozenset(
                {"Tops", "Bags"}
            ): (
                78,
                "Styling Pair",
                "A bag can coordinate with the outfit's "
                "upper-body styling.",
            ),

            frozenset(
                {"Bottoms", "Outerwear"}
            ): (
                88,
                "Outfit Structure Pair",
                "Bottoms and outerwear can work together "
                "as part of a complete outfit.",
            ),

            frozenset(
                {"Bottoms", "Shoes"}
            ): (
                97,
                "Core Outfit Pair",
                "Footwear and bottoms have a strong visual "
                "and silhouette relationship.",
            ),

            frozenset(
                {"Bottoms", "Accessories"}
            ): (
                80,
                "Styling Pair",
                "Accessories such as belts can directly "
                "support the bottom half of an outfit.",
            ),

            frozenset(
                {"Bottoms", "Bags"}
            ): (
                78,
                "Styling Pair",
                "Bags can coordinate with the overall outfit "
                "built around the bottoms.",
            ),

            frozenset(
                {
                    "Dresses & One Pieces",
                    "Outerwear",
                }
            ): (
                97,
                "Layering Pair",
                "Outerwear layers naturally over dresses "
                "and one-piece garments.",
            ),

            frozenset(
                {
                    "Dresses & One Pieces",
                    "Shoes",
                }
            ): (
                98,
                "Core Outfit Pair",
                "Footwear is a major styling component for "
                "dresses and one-piece garments.",
            ),

            frozenset(
                {
                    "Dresses & One Pieces",
                    "Accessories",
                }
            ): (
                92,
                "Styling Pair",
                "Accessories can strongly shape the styling "
                "of a dress or one-piece garment.",
            ),

            frozenset(
                {
                    "Dresses & One Pieces",
                    "Bags",
                }
            ): (
                88,
                "Styling Pair",
                "A bag can complement a dress or one-piece "
                "outfit.",
            ),

            frozenset(
                {
                    "Dresses & One Pieces",
                    "Tops",
                }
            ): (
                35,
                "Uncommon Layering Pair",
                "A top and a one-piece garment can sometimes "
                "be layered, but this depends heavily on the "
                "specific pieces.",
            ),

            frozenset(
                {
                    "Dresses & One Pieces",
                    "Bottoms",
                }
            ): (
                20,
                "Competing Main Garments",
                "A dress or one-piece garment normally "
                "replaces the need for separate bottoms.",
            ),

            frozenset(
                {"Outerwear", "Shoes"}
            ): (
                88,
                "Outfit Support Pair",
                "Outerwear and footwear can coordinate to "
                "define the outfit's overall style.",
            ),

            frozenset(
                {"Outerwear", "Accessories"}
            ): (
                85,
                "Styling Pair",
                "Accessories can complement outerwear and "
                "complete the look.",
            ),

            frozenset(
                {"Outerwear", "Bags"}
            ): (
                85,
                "Styling Pair",
                "Bags and outerwear can strongly influence "
                "the overall outfit aesthetic.",
            ),

            frozenset(
                {"Shoes", "Accessories"}
            ): (
                82,
                "Styling Pair",
                "Footwear and accessories can reinforce the "
                "same style direction.",
            ),

            frozenset(
                {"Shoes", "Bags"}
            ): (
                82,
                "Styling Pair",
                "Shoes and bags are common coordination "
                "points in an outfit.",
            ),

            frozenset(
                {"Accessories", "Bags"}
            ): (
                88,
                "Styling Pair",
                "Accessories and bags can work together to "
                "finish an outfit.",
            ),
        }

        rule = compatibility_rules.get(
            category_pair
        )

        if rule is None:
            result = {
                "score": 50,
                "compatible": False,
                "relation": "Unclassified Garment Pair",
                "reasons": [
                    "No garment compatibility rule exists "
                    "for this combination yet."
                ],
            }

        else:
            score, relation, reason = rule

            result = {
                "score": score,
                "compatible": score >= 60,
                "relation": relation,
                "reasons": [
                    reason
                ],
            }

    return {
        "score": result["score"],
        "compatible": result["compatible"],
        "relation": result["relation"],
        "category_1": first_category,
        "subcategory_1": first_subcategory,
        "category_2": second_category,
        "subcategory_2": second_subcategory,
        "reasons": result["reasons"],
    }