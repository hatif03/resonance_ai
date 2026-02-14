"""SQLAlchemy models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Declarative base for all models."""
    pass


def generate_uuid():
    return str(uuid.uuid4())


class Call(Base):
    """Call record from any source."""

    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(20), nullable=False)  # google_meet | twilio | upload
    external_id = Column(String(255), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    segments = relationship("TranscriptSegment", back_populates="call", cascade="all, delete-orphan")
    analyses = relationship("CallAnalysis", back_populates="call", cascade="all, delete-orphan")


class TranscriptSegment(Base):
    """Transcript segment with speaker and timestamps."""

    __tablename__ = "transcript_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False)
    speaker = Column(String(20), nullable=False)  # agent | customer
    text = Column(Text, nullable=False)
    start_time_ms = Column(Integer, nullable=True)
    end_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    call = relationship("Call", back_populates="segments")


class CallAnalysis(Base):
    """Analysis result for a call (realtime or post_call)."""

    __tablename__ = "call_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False)
    analysis_type = Column(String(20), nullable=False)  # realtime | post_call
    payload = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    call = relationship("Call", back_populates="analyses")


Index("idx_calls_source", Call.source)
Index("idx_calls_started", Call.started_at)
Index("idx_analyses_call", CallAnalysis.call_id)
