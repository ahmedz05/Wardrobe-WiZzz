from fastapi import FastAPI

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
from app.routes.outfit_routes import router as outfit_router


app = FastAPI(
    title="Wardrobe-WIZzz API",
    version="1.0.0",
)


# Legacy uploads have no trustworthy ownership metadata. Keep existing files on
# disk, but never expose the directory through a public static-files mount.


app.include_router(user_router)
app.include_router(clothing_router)
app.include_router(upload_router)
app.include_router(category_router)
app.include_router(brand_router)
app.include_router(material_router)
app.include_router(color_router)
app.include_router(outfit_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Wardrobe-WIZzz API"
    }
