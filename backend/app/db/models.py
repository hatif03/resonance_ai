"""SQLAlchemy models – works with both PostgreSQL and SQLite."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey, Index, JSON,
    TypeDecorator, CHAR,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Declarative base for all models."""
    pass


# ---------------------------------------------------------------------------
# Portable UUID type – uses native PG UUID when available, CHAR(36) on SQLite
# ---------------------------------------------------------------------------
class PortableUUID(TypeDecorator):
    """Platform-agnostic UUID column."""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value) if not isinstance(value, uuid.UUID) else value
        return value

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))


class Call(Base):
    """Call record from any source."""

    __tablename__ = "calls"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    source = Column(String(20), nullable=False)  # google_meet | twilio | upload
    external_id = Column(String(255), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    segments = relationship("TranscriptSegment", back_populates="call", cascade="all, delete-orphan")
    analyses = relationship("CallAnalysis", back_populates="call", cascade="all, delete-orphan")


class TranscriptSegment(Base):
    """Transcript segment with speaker and timestamps."""

    __tablename__ = "transcript_segments"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    call_id = Column(PortableUUID(), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False)
    speaker = Column(String(20), nullable=False)  # agent | customer
    text = Column(Text, nullable=False)
    start_time_ms = Column(Integer, nullable=True)
    end_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    call = relationship("Call", back_populates="segments")


class CallAnalysis(Base):
    """Analysis result for a call (realtime or post_call)."""

    __tablename__ = "call_analyses"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    call_id = Column(PortableUUID(), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False)
    analysis_type = Column(String(20), nullable=False)  # realtime | post_call
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    call = relationship("Call", back_populates="analyses")


Index("idx_calls_source", Call.source)
Index("idx_calls_started", Call.started_at)
Index("idx_analyses_call", CallAnalysis.call_id)
