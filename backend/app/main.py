from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine

from app.routes.user_routes import router as user_router
from app.routes.clothing_routes import router as clothing_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wardrobe-WIZzz API",
    description="AI Powered Smart Wardrobe Assistant",
    version="1.0.0"
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.include_router(user_router)
app.include_router(clothing_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Wardrobe-WIZzz API",
        "status": "Running 🚀",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }