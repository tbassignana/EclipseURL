from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.database import (
    close_mongo_connection,
    close_redis_connection,
    connect_to_mongo,
    connect_to_redis,
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup
    await connect_to_mongo()
    await connect_to_redis()
    yield
    # Shutdown
    await close_mongo_connection()
    await close_redis_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="A modern URL shortener service with analytics",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME}


# Import and include routers (must be after app creation to avoid circular imports)
from app.api import admin, analytics, auth, redirect, urls  # noqa: E402

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(urls.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
# Redirect router at root level for short URLs
app.include_router(redirect.router)
