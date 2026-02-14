"""Pydantic schemas for API request/response."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# --- Call ---
class CallBase(BaseModel):
    source: str
    external_id: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: dict | None = None


class CallCreate(CallBase):
    pass


class CallResponse(CallBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CallListResponse(BaseModel):
    calls: list[CallResponse]
    total: int
    limit: int
    offset: int


# --- Transcript Segment ---
class TranscriptSegmentBase(BaseModel):
    speaker: str
    text: str
    start_time_ms: int | None = None
    end_time_ms: int | None = None


class TranscriptSegmentResponse(TranscriptSegmentBase):
    id: UUID
    call_id: UUID

    model_config = {"from_attributes": True}


# --- Call Analysis ---
class CallAnalysisPayload(BaseModel):
    customer_satisfaction_score: int | None = None
    questions_answered_correctly: bool | None = None
    unanswered_questions: list[str] | None = None
    resolution_status: str | None = None
    key_topics: list[str] | None = None
    agent_performance_notes: str | None = None
    summary: str | None = None


class CallAnalysisResponse(BaseModel):
    id: UUID
    call_id: UUID
    analysis_type: str
    payload: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class CallAnalysisListResponse(BaseModel):
    analyses: list[CallAnalysisResponse]
    total: int
    limit: int
    offset: int


# --- Call detail (with transcript and analyses) ---
class CallDetailResponse(CallResponse):
    segments: list[TranscriptSegmentResponse] = []
    analyses: list[CallAnalysisResponse] = []


# --- Webhook payloads ---
class MeetWebhookSegment(BaseModel):
    speaker: str = "unknown"
    text: str
    start_time_ms: int | None = None
    end_time_ms: int | None = None


class MeetWebhookPayload(BaseModel):
    """Payload for Google Meet transcript webhook."""

    source: str = "google_meet"
    external_id: str | None = None
    conference_id: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    segments: list[MeetWebhookSegment]
