from pydantic import BaseModel


class ClothingCreate(BaseModel):

    name: str

    subcategory_id: int | None = None

    color: str | None = None

    fit: str | None = None

    material: str | None = None

    season: str | None = None

    style: str | None = None

    brand: str | None = None

    silhouette: str | None = None

    layering_role: str | None = None

    warmth_level: str | None = None

    occasion: str | None = None

    image_url: str | None = None



class ClothingUpdate(BaseModel):

    name: str

    subcategory_id: int | None = None

    color: str | None = None

    fit: str | None = None

    material: str | None = None

    season: str | None = None

    style: str | None = None

    brand: str | None = None

    silhouette: str | None = None

    layering_role: str | None = None

    warmth_level: str | None = None

    occasion: str | None = None

    image_url: str | None = None