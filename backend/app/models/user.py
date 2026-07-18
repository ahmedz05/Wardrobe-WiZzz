from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    clothes = relationship(
        "Clothing",
        back_populates="owner"
    )

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False
    )