"""Manual audio upload API."""

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.ingest.upload import process_upload, ALLOWED_EXTENSIONS

router = APIRouter()


@router.post("")
async def upload_audio(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an audio file for transcription and analysis."""
    suffix = (file.filename or "").lower().split(".")[-1]
    if suffix and f".{suffix}" not in ALLOWED_EXTENSIONS:
        return {
            "error": f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            "call_id": None,
        }
    call_id, _ = await process_upload(db, file)
    return {"message": "Upload processed", "call_id": call_id, "filename": file.filename}
