"""Whisper-based transcription service."""

import asyncio
from pathlib import Path

from app.config import settings
from app.transcription.types import Transcript, TranscriptSegment

# Lazy-load model to avoid startup cost
_whisper_model = None


def _get_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(
            settings.whisper_model_size,
            device="cpu",
            compute_type="int8",
        )
    return _whisper_model


def transcribe_file(audio_path: str | Path) -> Transcript:
    """Transcribe an audio file synchronously."""
    model = _get_model()
    segments_iter, info = model.transcribe(str(audio_path), language=None)
    segments = []
    for seg in segments_iter:
        segments.append(
            TranscriptSegment(
                speaker="unknown",
                text=seg.text.strip(),
                start_time_ms=int(seg.start * 1000) if seg.start else None,
                end_time_ms=int(seg.end * 1000) if seg.end else None,
            )
        )
    full_text = " ".join(s.text for s in segments)
    return Transcript(segments=segments, full_text=full_text)


async def transcribe_file_async(audio_path: str | Path) -> Transcript:
    """Transcribe an audio file asynchronously (runs in executor)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, transcribe_file, audio_path)
