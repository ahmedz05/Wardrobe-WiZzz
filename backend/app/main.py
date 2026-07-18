from fastapi import FastAPI

from app.routes.user_routes import router as user_router
from app.routes.clothing_routes import router as clothing_router
from app.routes.upload_routes import router as upload_router
from app.routes.category_routes import router as category_router
from app.routes.brand_routes import router as brand_router


app = FastAPI(
    title="Wardrobe-WIZzz API",
    version="1.0.0"
)

# ----------------------------------------
# ROUTES
# ----------------------------------------

app.include_router(
    user_router
)

app.include_router(
    clothing_router
)

app.include_router(
    upload_router
)

app.include_router(
    category_router
)

app.include_router(
    brand_router
)

# ----------------------------------------
# ROOT
# ----------------------------------------

@app.get("/")
def root():
    return {
        "message": "Wardrobe-WIZzz API is running!"
    }