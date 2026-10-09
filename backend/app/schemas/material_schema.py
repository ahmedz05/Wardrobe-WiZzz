from typing import Optional

from pydantic import BaseModel, ConfigDict


class MaterialBase(BaseModel):
    name: str
    slug: str
    material_type: str
    description: Optional[str] = None
    care_instructions: Optional[str] = None
    is_natural: bool = False


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)