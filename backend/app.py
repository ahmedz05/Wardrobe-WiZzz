from fastapi import FastAPI

app = FastAPI(
    title="Wardrobe-WIZzz API"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to Wardrobe-WIZzz"
    }