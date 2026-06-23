from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.middleware.logging_middleware import LoggingMiddleware
from app.logger import logger

from app.routes.health_routes import router as health_router
from app.routes.segmentation_routes import router as segmentation_router
from app.routes.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up", extra={"version": "1.0.0"})
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Customer Segmentation API",
    description="Your customer data has been trying to tell you something. This is what it's been saying.",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware must be added before routers
app.add_middleware(LoggingMiddleware)

app.include_router(health_router)
app.include_router(segmentation_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "Welcome to Customer Segmentation API"}