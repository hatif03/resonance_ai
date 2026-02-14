"""API router - aggregates all route modules."""

from fastapi import APIRouter

from app.api.routes import calls, analyses, upload

router = APIRouter()

router.include_router(calls.router, prefix="/calls", tags=["calls"])
router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
router.include_router(upload.router, prefix="/upload", tags=["upload"])
