from fastapi import FastAPI

from app.database import Base, engine

# Import models so SQLAlchemy knows about them
from app.models.user import User
from app.models.clothing import Clothing

# Import routes
from app.routes.user_routes import router as user_router
from app.routes.clothing_routes import router as clothing_router

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wardrobe-WIZzz API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "status": "Backend working!",
        "message": "Welcome to Wardrobe-WIZzz API"
    }


app.include_router(user_router)
app.include_router(clothing_router)