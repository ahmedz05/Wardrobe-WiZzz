from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ClothingBase(BaseModel):
    name: str

    subcategory_id: Optional[int] = None
    brand_id: Optional[int] = None
    material_id: Optional[int] = None
    color_id: Optional[int] = None

    season: Optional[str] = None
    style: Optional[str] = None
    fit: Optional[str] = None
    silhouette: Optional[str] = None
    layering_role: Optional[str] = None
    warmth_level: Optional[str] = None
    occasion: Optional[str] = None

    image_url: Optional[str] = None

    # Metadata
    condition: Optional[str] = None
    favorite: bool = False

    purchase_date: Optional[date] = None
    purchase_price: float = 0.0
    currency: Optional[str] = None

    last_worn: Optional[date] = None
    times_worn: int = 0

    notes: Optional[str] = None


class ClothingCreate(ClothingBase):
    pass


class ClothingUpdate(ClothingBase):
    pass


class ClothingResponse(ClothingBase):
    id: int
    user_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)