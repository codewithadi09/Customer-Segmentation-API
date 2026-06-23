from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.security_middleware import SecurityHeadersMiddleware
from app.middleware.rate_limit import limiter
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

# Attach the rate limiter to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — only allow your intended clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # add your frontend URL here when you have one
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Order matters — security headers wrap everything
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)

app.include_router(health_router)
app.include_router(segmentation_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "Welcome to Customer Segmentation API"}