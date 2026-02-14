"""Manual audio upload - save, transcribe, analyze."""

import tempfile
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.transcription.whisper_client import transcribe_file_async
from app.db.repository import create_call, add_transcript_segments
from app.analysis.post_call import run_post_call_analysis

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}


async def process_upload(
    db: AsyncSession,
    file: UploadFile,
) -> tuple[str, str]:
    """
    Process uploaded audio: transcribe with Whisper, store, run analysis.
    Returns (call_id, full_text).
    """
    suffix = Path(file.filename or "audio").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        suffix = ".mp3"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        transcript = await transcribe_file_async(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    call = await create_call(
        db=db,
        source="upload",
        external_id=file.filename,
    )
    segments_data = [
        {
            "speaker": s.speaker,
            "text": s.text,
            "start_time_ms": s.start_time_ms,
            "end_time_ms": s.end_time_ms,
        }
        for s in transcript.segments
    ]
    await add_transcript_segments(db, call.id, segments_data)
    await run_post_call_analysis(db, call.id, transcript.full_text)
    return str(call.id), transcript.full_text
