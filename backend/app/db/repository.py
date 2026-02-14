"""Database repository - CRUD operations."""

from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Call, TranscriptSegment, CallAnalysis


async def create_call(
    db: AsyncSession,
    source: str,
    external_id: str | None = None,
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    metadata_: dict | None = None,
) -> Call:
    """Create a new call record."""
    call = Call(
        source=source,
        external_id=external_id,
        started_at=started_at,
        ended_at=ended_at,
        metadata_=metadata_ or {},
    )
    db.add(call)
    await db.flush()
    return call


async def get_call(db: AsyncSession, call_id: UUID) -> Call | None:
    """Get a call by ID with segments and analyses."""
    result = await db.execute(
        select(Call)
        .where(Call.id == call_id)
        .options(selectinload(Call.segments), selectinload(Call.analyses))
    )
    return result.scalar_one_or_none()


async def list_calls(
    db: AsyncSession,
    source: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Call], int]:
    """List calls with optional filter and pagination."""
    query = select(Call)
    count_query = select(func.count()).select_from(Call)

    if source:
        query = query.where(Call.source == source)
        count_query = count_query.where(Call.source == source)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(Call.started_at.desc().nullslast()).limit(limit).offset(offset)
    result = await db.execute(query)
    calls = list(result.scalars().all())
    return calls, total


async def add_transcript_segments(
    db: AsyncSession,
    call_id: UUID,
    segments: list[dict],
) -> list[TranscriptSegment]:
    """Add transcript segments to a call."""
    created = []
    for seg in segments:
        segment = TranscriptSegment(
            call_id=call_id,
            speaker=seg.get("speaker", "unknown"),
            text=seg.get("text", ""),
            start_time_ms=seg.get("start_time_ms"),
            end_time_ms=seg.get("end_time_ms"),
        )
        db.add(segment)
        created.append(segment)
    await db.flush()
    return created


async def create_analysis(
    db: AsyncSession,
    call_id: UUID,
    analysis_type: str,
    payload: dict,
) -> CallAnalysis:
    """Create a call analysis record."""
    analysis = CallAnalysis(
        call_id=call_id,
        analysis_type=analysis_type,
        payload=payload,
    )
    db.add(analysis)
    await db.flush()
    return analysis


async def list_analyses(
    db: AsyncSession,
    call_id: UUID | None = None,
    analysis_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[CallAnalysis], int]:
    """List analyses with optional filters."""
    query = select(CallAnalysis)
    count_query = select(func.count()).select_from(CallAnalysis)

    if call_id:
        query = query.where(CallAnalysis.call_id == call_id)
        count_query = count_query.where(CallAnalysis.call_id == call_id)
    if analysis_type:
        query = query.where(CallAnalysis.analysis_type == analysis_type)
        count_query = count_query.where(CallAnalysis.analysis_type == analysis_type)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(CallAnalysis.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    analyses = list(result.scalars().all())
    return analyses, total
