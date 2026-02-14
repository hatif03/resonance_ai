"""Transcription types."""

from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    """A single segment of transcribed speech."""

    speaker: str = "unknown"
    text: str
    start_time_ms: int | None = None
    end_time_ms: int | None = None


class Transcript(BaseModel):
    """Full transcript with segments."""

    segments: list[TranscriptSegment]
    full_text: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        if not self.full_text and self.segments:
            self.full_text = " ".join(s.text for s in self.segments)
