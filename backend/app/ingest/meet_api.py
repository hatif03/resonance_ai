"""Google Meet REST API - fetch post-call transcripts."""

from datetime import datetime
from typing import Any

from app.config import settings


async def fetch_meet_transcript(
    conference_id: str,
    credentials_path: str | None = None,
) -> list[dict]:
    """
    Fetch transcript entries from a Google Meet conference.
    Requires Google Workspace with Meet API enabled and service account or OAuth.

    Returns list of segment dicts: [{speaker, text, start_time_ms, end_time_ms}, ...]
    """
    creds_path = credentials_path or settings.google_credentials_path
    if not creds_path:
        raise ValueError("Google credentials path not configured")

    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    credentials = service_account.Credentials.from_service_account_file(creds_path)
    service = build("meet", "v2", credentials=credentials)

    # List transcripts for the conference
    transcripts_response = (
        service.conferenceRecords()
        .transcripts()
        .list(parent=f"conferenceRecords/{conference_id}")
        .execute()
    )

    segments = []
    for transcript in transcripts_response.get("transcripts", []):
        transcript_id = transcript.get("name", "").split("/")[-1]
        entries_response = (
            service.conferenceRecords()
            .transcripts()
            .entries()
            .list(parent=f"conferenceRecords/{conference_id}/transcripts/{transcript_id}")
            .execute()
        )
        for entry in entries_response.get("transcriptEntries", []):
            participant = entry.get("participant", "")
            # participant is a resource name; speaker could be derived from participant
            speaker = "agent" if "agent" in participant.lower() else "customer"
            text = entry.get("text", "")
            start = entry.get("startTime")
            end = entry.get("endTime")
            start_ms = _parse_duration_to_ms(start) if start else None
            end_ms = _parse_duration_to_ms(end) if end else None
            segments.append({
                "speaker": speaker,
                "text": text,
                "start_time_ms": start_ms,
                "end_time_ms": end_ms,
            })

    return segments


def _parse_duration_to_ms(duration: str) -> int | None:
    """Parse Google duration string (e.g. '123.456s') to milliseconds."""
    if not duration or "s" not in duration:
        return None
    try:
        seconds = float(duration.replace("s", ""))
        return int(seconds * 1000)
    except (ValueError, TypeError):
        return None
