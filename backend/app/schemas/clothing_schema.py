
from datetime import date
from typing import Annotated, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)


# =====================================
# VALIDATED CLOTHING NAME
# =====================================

ClothingName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=120,
    ),
]


# =====================================
# BASE CLOTHING SCHEMA
# =====================================

class ClothingBase(BaseModel):

    # Clothing names cannot be empty.
    # Surrounding whitespace is removed.
    name: ClothingName

    # Catalog IDs must be positive when provided.
    subcategory_id: Optional[int] = Field(
        default=None,
        gt=0,
    )

    brand_id: Optional[int] = Field(
        default=None,
        gt=0,
    )

    material_id: Optional[int] = Field(
        default=None,
        gt=0,
    )

    color_id: Optional[int] = Field(
        default=None,
        gt=0,
    )

    # Clothing characteristics.
    season: Optional[str] = None
    style: Optional[str] = None
    fit: Optional[str] = None
    silhouette: Optional[str] = None
    layering_role: Optional[str] = None
    warmth_level: Optional[str] = None
    occasion: Optional[str] = None

    # Clothing image.
    image_url: Optional[str] = None

    # Additional metadata.
    condition: Optional[str] = None

    favorite: bool = False

    purchase_date: Optional[date] = None

    # Prices cannot be negative, infinite, or NaN.
    purchase_price: float = Field(
        default=0.0,
        ge=0,
        allow_inf_nan=False,
    )

    currency: Optional[str] = None

    last_worn: Optional[date] = None

    # Wear counts cannot be negative.
    times_worn: int = Field(
        default=0,
        ge=0,
    )

    notes: Optional[str] = None


# =====================================
# CREATE CLOTHING
# =====================================

class ClothingCreate(ClothingBase):
    pass


# =====================================
# UPDATE CLOTHING
# =====================================

class ClothingUpdate(ClothingBase):
    pass


# =====================================
# CLOTHING API RESPONSE
# =====================================

class ClothingResponse(ClothingBase):

    id: int
    user_id: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
