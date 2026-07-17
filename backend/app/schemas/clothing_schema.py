from pydantic import BaseModel


class ClothingCreate(BaseModel):
    name: str
    category: str
    color: str
    season: str
    style: str
    brand: str
    image_url: str


class ClothingUpdate(BaseModel):
    name: str
    category: str
    color: str
    season: str
    style: str
    brand: str
    image_url: str