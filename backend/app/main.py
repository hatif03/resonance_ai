"""FastAPI application - standalone REST API for call monitoring."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import router as api_router
from app.db.session import init_db

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="AI Call Monitoring Agent - Transcribe and analyze customer support calls",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1", tags=["api"])


@app.on_event("startup")
async def startup():
    """Create database tables on startup if they don't exist."""
    try:
        await init_db()
        logger.info("Database tables ready")
    except Exception as e:
        logger.warning("Database init failed (run migrations?): %s", e)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name}
