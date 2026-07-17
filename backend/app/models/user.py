from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

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