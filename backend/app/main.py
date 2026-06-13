from fastapi import FastAPI
from app.routes.user_routes import router as user_router

app = FastAPI(
    title="Wardrobe-WIZzz API"
)

app.include_router(user_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to Wardrobe-WIZzz"
    }