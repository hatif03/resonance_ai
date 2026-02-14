"""Analyses API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.db.repository import list_analyses as repo_list_analyses
from app.api.schemas import CallAnalysisListResponse, CallAnalysisResponse

router = APIRouter()


@router.get("", response_model=CallAnalysisListResponse)
async def list_analyses(
    db: AsyncSession = Depends(get_db),
    call_id: UUID | None = Query(None, description="Filter by call ID"),
    analysis_type: str | None = Query(None, description="Filter by type: realtime, post_call"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List call analyses with optional filters."""
    analyses, total = await repo_list_analyses(
        db, call_id=call_id, analysis_type=analysis_type, limit=limit, offset=offset
    )
    return CallAnalysisListResponse(
        analyses=[CallAnalysisResponse.model_validate(a) for a in analyses],
        total=total,
        limit=limit,
        offset=offset,
    )
