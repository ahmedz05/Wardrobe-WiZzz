from typing import Optional

from pydantic import BaseModel, ConfigDict


class ColorBase(BaseModel):
    name: str
    slug: str
    hex_code: str

    rgb_value: Optional[str] = None

    color_family: str

    undertone: Optional[str] = None
    brightness: Optional[str] = None
    saturation: Optional[str] = None

    description: Optional[str] = None

    is_neutral: bool = False


class ColorCreate(ColorBase):
    pass


class ColorUpdate(ColorBase):
    pass


class ColorResponse(ColorBase):
    id: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )