"""Twilio Media Streams - WebSocket handler for call audio."""

import base64
import json
import tempfile
from pathlib import Path

from fastapi import WebSocket

from app.transcription.whisper_client import transcribe_file
from app.db.session import async_session
from app.db.repository import create_call, add_transcript_segments
from app.analysis.post_call import run_post_call_analysis


async def handle_twilio_media_stream(websocket: WebSocket) -> str | None:
    """
    Handle Twilio Media Stream WebSocket.
    Buffers mulaw audio, transcribes when stream closes, stores in DB.
    Returns call_id or None on error.
    """
    await websocket.accept()
    audio_chunks = []
    stream_sid = None
    call_sid = None

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("event") == "connected":
                pass
            elif msg.get("event") == "start":
                stream_sid = msg.get("streamSid")
                call_sid = msg.get("start", {}).get("callSid")
            elif msg.get("event") == "media":
                payload = msg.get("media", {}).get("payload")
                if payload:
                    chunk = base64.b64decode(payload)
                    audio_chunks.append(chunk)
            elif msg.get("event") == "closed":
                break
    except Exception:
        pass
    finally:
        await websocket.close()

    if not audio_chunks:
        return None

    raw_path = tempfile.mktemp(suffix=".ulaw")
    wav_path = tempfile.mktemp(suffix=".wav")
    try:
        with open(raw_path, "wb") as f:
            for chunk in audio_chunks:
                f.write(chunk)

        import subprocess
        result = subprocess.run(
            [
                "ffmpeg", "-y", "-f", "mulaw", "-ar", "8000", "-ac", "1",
                "-i", raw_path, "-ar", "16000", "-ac", "1", wav_path,
            ],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return None

        transcript = transcribe_file(wav_path)
    except Exception:
        return None
    finally:
        Path(raw_path).unlink(missing_ok=True)
        Path(wav_path).unlink(missing_ok=True)

    async with async_session() as db:
        call = await create_call(
            db=db,
            source="twilio",
            external_id=call_sid or stream_sid,
        )
        segments_data = [
            {"speaker": s.speaker, "text": s.text, "start_time_ms": s.start_time_ms, "end_time_ms": s.end_time_ms}
            for s in transcript.segments
        ]
        await add_transcript_segments(db, call.id, segments_data)
        await run_post_call_analysis(db, call.id, transcript.full_text)
        await db.commit()
        return str(call.id)
