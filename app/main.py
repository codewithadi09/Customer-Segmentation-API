from fastapi import FastAPI

from app import models

from app.database import engine, Base

from app.routes.health import router as health_router
from app.routes.segmentation import router as segmentation_router
from app.routes.auth_routes import router as auth_router
from app.models.user_model import User


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(health_router)
app.include_router(segmentation_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "Welcome to Customer Segmentation API"}