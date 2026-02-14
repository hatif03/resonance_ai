"""Webhook endpoints for external integrations."""

from fastapi import APIRouter, Request, Depends, WebSocket
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.db.repository import create_call, add_transcript_segments
from app.api.schemas import MeetWebhookPayload
from app.analysis.post_call import run_post_call_analysis
from app.ingest.meet_api import fetch_meet_transcript
from app.ingest.twilio import handle_twilio_media_stream

router = APIRouter()


@router.post("/meet")
async def meet_webhook(
    payload: MeetWebhookPayload,
    db: AsyncSession = Depends(get_db),
):
    """
    Google Meet transcript webhook.
    Accepts inline segments or conference_id to fetch from Meet API.
    """
    segments_data = payload.segments

    if not segments_data and payload.conference_id:
        try:
            raw_segments = await fetch_meet_transcript(payload.conference_id)
            segments_data = [
                {"speaker": s.get("speaker", "unknown"), "text": s.get("text", ""), "start_time_ms": s.get("start_time_ms"), "end_time_ms": s.get("end_time_ms")}
                for s in raw_segments
            ]
        except Exception as e:
            return {"error": str(e), "received": False}

    if not segments_data:
        return {"error": "No segments provided and no conference_id", "received": False}

    call = await create_call(
        db=db,
        source=payload.source,
        external_id=payload.external_id or payload.conference_id,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
    )
    await add_transcript_segments(db, call.id, segments_data)
    full_text = " ".join(s.get("text", "") for s in segments_data)
    await run_post_call_analysis(db, call.id, full_text)
    return {"received": True, "call_id": str(call.id)}


@router.post("/twilio/voice")
async def twilio_voice_webhook(request: Request):
    """
    Twilio voice webhook - returns TwiML to stream call audio to our WebSocket.
    Configure this URL as the webhook for your Twilio number.
    """
    ws_url = f"{settings.twilio_ws_base_url.rstrip('/')}/api/v1/webhooks/twilio/media"
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{ws_url}"/>
    </Connect>
    <Say>Please hold while we connect your call.</Say>
    <Pause length="3600"/>
</Response>'''
    return Response(content=twiml, media_type="application/xml")


@router.websocket("/twilio/media")
async def twilio_media_websocket(websocket: WebSocket):
    """WebSocket endpoint for Twilio Media Streams."""
    await handle_twilio_media_stream(websocket)


@router.post("/twilio")
async def twilio_webhook(request: Request):
    """Twilio status callback webhook (e.g. call completed)."""
    body = await request.json()
    return {"received": True}
