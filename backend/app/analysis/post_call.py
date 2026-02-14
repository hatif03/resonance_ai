"""Post-call analysis - full transcript to structured output."""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.llm_client import get_llm_client
from app.analysis.prompts import POST_CALL_ANALYSIS_SYSTEM
from app.db.repository import create_analysis, get_call


async def run_post_call_analysis(
    db: AsyncSession,
    call_id: UUID,
    transcript_text: str,
) -> dict:
    """
    Run full analysis on a transcript and store in DB.
    Returns the analysis payload.
    """
    if not transcript_text.strip():
        payload = {
            "customer_satisfaction_score": None,
            "questions_answered_correctly": None,
            "unanswered_questions": [],
            "resolution_status": "unknown",
            "key_topics": [],
            "agent_performance_notes": "No transcript content to analyze.",
            "summary": "Empty transcript.",
        }
    else:
        client = get_llm_client()
        payload = await client.analyze_transcript(
            transcript=transcript_text,
            system_prompt=POST_CALL_ANALYSIS_SYSTEM,
        )
        # Normalize keys to match schema
        payload = {
            "customer_satisfaction_score": payload.get("customer_satisfaction_score"),
            "questions_answered_correctly": payload.get("questions_answered_correctly"),
            "unanswered_questions": payload.get("unanswered_questions") or [],
            "resolution_status": payload.get("resolution_status") or "unknown",
            "key_topics": payload.get("key_topics") or [],
            "agent_performance_notes": payload.get("agent_performance_notes") or "",
            "summary": payload.get("summary") or "",
        }

    analysis = await create_analysis(
        db=db,
        call_id=call_id,
        analysis_type="post_call",
        payload=payload,
    )
    await db.flush()
    return payload
