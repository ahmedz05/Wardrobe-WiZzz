from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.user_routes import router as user_router
from app.routes.clothing_routes import router as clothing_router
from app.routes.upload_routes import router as upload_router
from app.routes.category_routes import router as category_router

app = FastAPI(
    title="Wardrobe-WIZzz API",
    description="AI-Powered Smart Wardrobe & Fashion Intelligence Platform",
    version="1.0.0",
)

# Serve uploaded images
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

# -------------------------
# ROUTERS
# -------------------------

app.include_router(user_router)
app.include_router(clothing_router)
app.include_router(upload_router)
app.include_router(category_router)

# -------------------------
# ROOT
# -------------------------

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Wardrobe-WIZzz API is running!",
        "version": "1.0.0",
        "status": "online",
    }