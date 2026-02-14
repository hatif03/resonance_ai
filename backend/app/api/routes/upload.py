"""Manual audio upload API."""

import logging

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.ingest.upload import process_upload, ALLOWED_EXTENSIONS

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("")
async def upload_audio(
    file: UploadFile = File(..., description="Audio file (mp3, wav, m4a, ogg, flac, webm, mp4)"),
    db: AsyncSession = Depends(get_db),
):
    """Upload an audio file for transcription and analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    parts = (file.filename or "").lower().rsplit(".", 1)
    suffix = ("." + parts[-1]) if len(parts) > 1 else ""
    if not suffix or suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    try:
        call_id, _ = await process_upload(db, file)
        return {"message": "Upload processed", "call_id": call_id, "filename": file.filename}
    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=str(e))
