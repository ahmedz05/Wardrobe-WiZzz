from typing import Optional

from pydantic import BaseModel, ConfigDict


class BrandBase(BaseModel):
    name: str
    slug: str
    brand_type: str

    description: Optional[str] = None
    founded_year: Optional[int] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    brand_type: Optional[str] = None

    description: Optional[str] = None
    founded_year: Optional[int] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None


class BrandResponse(BrandBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )