"""Calls API routes."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel

from app.db.session import get_db
from app.db.repository import list_calls as repo_list_calls, get_call as repo_get_call
from app.api.schemas import CallListResponse, CallDetailResponse, CallResponse, TranscriptSegmentResponse, CallAnalysisResponse
from app.analysis.realtime import run_realtime_analysis

router = APIRouter()


class RealtimeAnalysisRequest(BaseModel):
    segment_text: str


@router.get("", response_model=CallListResponse)
async def list_calls(
    db: AsyncSession = Depends(get_db),
    source: str | None = Query(None, description="Filter by source: google_meet, twilio, upload"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List calls with optional filters."""
    calls, total = await repo_list_calls(db, source=source, limit=limit, offset=offset)
    return CallListResponse(
        calls=[
            CallResponse(
                id=c.id,
                source=c.source,
                external_id=c.external_id,
                started_at=c.started_at,
                ended_at=c.ended_at,
                metadata=c.metadata_ or {},
                created_at=c.created_at,
            )
            for c in calls
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{call_id}", response_model=CallDetailResponse)
async def get_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single call with transcript and analyses."""
    call = await repo_get_call(db, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return CallDetailResponse(
        id=call.id,
        source=call.source,
        external_id=call.external_id,
        started_at=call.started_at,
        ended_at=call.ended_at,
        metadata=call.metadata_ or {},
        created_at=call.created_at,
        segments=[TranscriptSegmentResponse.model_validate(s) for s in call.segments],
        analyses=[CallAnalysisResponse.model_validate(a) for a in call.analyses],
    )


@router.post("/{call_id}/analyze-realtime")
async def analyze_realtime(
    call_id: UUID,
    body: RealtimeAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run real-time analysis on a transcript segment.
    Use when integrating with streaming transcript sources (Meet Media API, Recall.ai).
    """
    call = await repo_get_call(db, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    payload = await run_realtime_analysis(db, call_id, body.segment_text)
    return {"call_id": str(call_id), "analysis": payload}
