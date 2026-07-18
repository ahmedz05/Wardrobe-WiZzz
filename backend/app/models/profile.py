from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    height = Column(String)

    weight = Column(String)

    skin_tone = Column(String)

    body_type = Column(String)

    gender = Column(String)

    preferred_styles = Column(String)

    user = relationship(
        "User",
        back_populates="profile"
    )