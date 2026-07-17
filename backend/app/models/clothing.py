from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Clothing(Base):
    __tablename__ = "clothing"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        nullable=False
    )

    subcategory = Column(
        String
    )

    color = Column(
        String
    )

    fit = Column(
        String
    )

    material = Column(
        String
    )

    season = Column(
        String
    )

    style = Column(
        String
    )

    brand = Column(
        String
    )

    image_url = Column(
        String
    )

    owner = relationship(
        "User",
        back_populates="clothes"
    )