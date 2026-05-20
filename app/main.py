from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.segmentation import router as segmentation_router

app = FastAPI()

app.include_router(health_router)
app.include_router(segmentation_router)

@app.get("/")
def home():
    return {"message": "Welcome to Customer Segmentation API" }