from fastapi import FastAPI
from app.routes.user_routes import router as user_router
from app.database import engine, Base
from app.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"status": "backend working"}


app.include_router(user_router)