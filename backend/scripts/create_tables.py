from app.database import Base, engine

from app.models.user import User
from app.models.clothing import Clothing


Base.metadata.create_all(bind=engine)

print("Tables created successfully!")