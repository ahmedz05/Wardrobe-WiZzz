from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine

# Import models
import app.models

# Import routers
from app.routes.user_routes import router as user_router
from app.routes.clothing_routes import router as clothing_router
from app.routes.upload_routes import router as upload_router
from app.routes.category_routes import router as category_router
from app.routes.brand_routes import router as brand_router
from app.routes.material_routes import router as material_router
from app.routes.color_routes import router as color_router


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "uploads"

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Wardrobe-WIZzz API",
    version="1.0.0",
)


app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_FOLDER)),
    name="uploads",
)


app.include_router(user_router)
app.include_router(clothing_router)
app.include_router(upload_router)
app.include_router(category_router)
app.include_router(brand_router)
app.include_router(material_router)
app.include_router(color_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Wardrobe-WIZzz API"
    }