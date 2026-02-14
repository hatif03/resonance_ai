"""Real-time analysis - buffered segments."""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.llm_client import get_llm_client
from app.analysis.prompts import REALTIME_ANALYSIS_SYSTEM
from app.db.repository import create_analysis


async def run_realtime_analysis(
    db: AsyncSession,
    call_id: UUID,
    segment_text: str,
) -> dict:
    """
    Run quick analysis on a short transcript segment.
    Returns the analysis payload.
    """
    if not segment_text.strip():
        payload = {
            "sentiment_hint": "neutral",
            "has_unanswered_question": False,
            "escalation_signal": False,
            "notes": "",
        }
    else:
        client = get_llm_client()
        payload = await client.analyze_transcript(
            transcript=segment_text,
            system_prompt=REALTIME_ANALYSIS_SYSTEM,
        )
        payload = {
            "sentiment_hint": payload.get("sentiment_hint", "neutral"),
            "has_unanswered_question": payload.get("has_unanswered_question", False),
            "escalation_signal": payload.get("escalation_signal", False),
            "notes": payload.get("notes", ""),
        }

    await create_analysis(
        db=db,
        call_id=call_id,
        analysis_type="realtime",
        payload=payload,
    )
    await db.flush()
    return payload
