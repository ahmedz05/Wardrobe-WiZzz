from sqlalchemy import Column, Integer, String, Text

from app.core.base_model import BaseModel


class Brand(BaseModel):
    __tablename__ = "brands"

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    slug = Column(
        String,
        unique=True,
        nullable=False
    )

    brand_type = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    founded_year = Column(
        Integer,
        nullable=True
    )

    website = Column(
        String,
        nullable=True
    )

    logo_url = Column(
        String,
        nullable=True
    )