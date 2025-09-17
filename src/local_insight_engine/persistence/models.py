"""
SQLAlchemy models for persistent Q&A sessions.
Based on CONCEPT_PersistentQA.md specification.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, ForeignKey, JSON, CheckConstraint,
    Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
# from sqlalchemy.ext.hybrid import hybrid_property  # Causing issues, use regular properties
# from dataclasses import asdict  # Not needed for Pydantic models

from .database import Base
from ..models.analysis import AnalysisResult


class PersistentQASession(Base):
    """
    Persistent storage for Q&A sessions with documents.
    Stores neutralized content only - never original document text.
    """
    __tablename__ = 'sessions'

    # Core Session Data
    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_path_hash = Column(String, nullable=False, index=True)
    pepper_id = Column(String, nullable=False, index=True)
    document_hash = Column(String, nullable=False)
    document_display_name = Column(String, nullable=True)
    source_id = Column(String, nullable=True)  # Opaque reference instead of path

    # Analysis Data
    neutralized_context = Column(Text, nullable=True)
    analysis_result_json = Column(Text, nullable=False)  # JSON-serialized AnalysisResult
    neutralization_version = Column(String, nullable=False, default="v0.1.1")
    policy_id = Column(String, nullable=False, default="default")
    retention_days = Column(Integer, nullable=False, default=365)
    consent_basis = Column(String, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_accessed = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    total_questions = Column(Integer, nullable=False, default=0)
    session_tags_json = Column(Text, nullable=False, default='[]')  # JSON array
    is_favorite = Column(Boolean, nullable=False, default=False)

    # Smart Features
    auto_generated_summary = Column(Text, nullable=True)
    key_insights_json = Column(Text, nullable=False, default='[]')  # JSON array

    # Relationships
    qa_exchanges = relationship("QAExchange", back_populates="session", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint('retention_days >= 0', name='positive_retention'),
        CheckConstraint('is_favorite IN (0, 1)', name='boolean_favorite'),
        CheckConstraint('total_questions >= 0', name='non_negative_questions'),
        CheckConstraint(
            "consent_basis IS NULL OR consent_basis IN "
            "('consent','contract','legal_obligation','vital_interests','public_task','legitimate_interests')",
            name='valid_consent_basis'
        ),
        UniqueConstraint('document_hash', 'pepper_id', name='unique_document_hash_per_pepper'),
        Index('idx_sessions_last_accessed', 'last_accessed'),
        Index('idx_sessions_created_at', 'created_at'),
        Index('idx_sessions_pepper_id', 'pepper_id'),
    )

    @property
    def session_tags(self) -> List[str]:
        """Get session tags as Python list."""
        try:
            return json.loads(self.session_tags_json or '[]')
        except json.JSONDecodeError:
            return []

    @session_tags.setter
    def session_tags(self, value: List[str]):
        """Set session tags from Python list."""
        self.session_tags_json = json.dumps(value or [])

    @property
    def key_insights(self) -> List[str]:
        """Get key insights as Python list."""
        try:
            return json.loads(self.key_insights_json or '[]')
        except json.JSONDecodeError:
            return []

    @key_insights.setter
    def key_insights(self, value: List[str]):
        """Set key insights from Python list."""
        self.key_insights_json = json.dumps(value or [])

    @property
    def analysis_result(self) -> Optional[AnalysisResult]:
        """Get analysis result as Python object."""
        try:
            if self.analysis_result_json:
                # Parse JSON and create Pydantic model
                return AnalysisResult.model_validate_json(self.analysis_result_json)
            return None
        except (json.JSONDecodeError, TypeError, Exception):
            return None

    @analysis_result.setter
    def analysis_result(self, value: Optional[AnalysisResult]):
        """Set analysis result from Python object."""
        if value is None:
            self.analysis_result_json = '{}'
        else:
            # Convert Pydantic model to dict for JSON serialization
            self.analysis_result_json = value.model_dump_json()

    @property
    def expires_at(self) -> datetime:
        """Calculate expiration date based on created_at and retention_days."""
        from datetime import timedelta
        return self.created_at + timedelta(days=self.retention_days)

    def update_last_accessed(self):
        """Update the last accessed timestamp to now."""
        self.last_accessed = datetime.now(timezone.utc)

    def add_qa_exchange(self, question: str, answer: str, **kwargs) -> 'QAExchange':
        """Add a new Q&A exchange to this session."""
        exchange = QAExchange(
            session_id=self.session_id,
            question=question,
            answer=answer,
            **kwargs
        )
        self.qa_exchanges.append(exchange)
        self.total_questions += 1
        self.update_last_accessed()
        return exchange


class QAExchange(Base):
    """
    Individual question-answer exchange within a session.
    """
    __tablename__ = 'qa_exchanges'

    # Core Data
    exchange_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Context & Intelligence
    context_used = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    answer_quality = Column(String, nullable=True)
    answer_origin = Column(String, nullable=True)

    # User Interaction
    user_rating = Column(Integer, nullable=True)
    user_notes = Column(Text, nullable=True)
    is_bookmarked = Column(Boolean, nullable=False, default=False)

    # Meta Information
    processing_time = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=False, default=0)
    claude_model = Column(String, nullable=True)
    safety_flags_json = Column(Text, nullable=False, default='[]')  # JSON array
    checksum = Column(String, nullable=True)

    # Relations
    document_references_json = Column(Text, nullable=False, default='[]')  # JSON array

    # Relationships
    session = relationship("PersistentQASession", back_populates="qa_exchanges")

    # Constraints
    __table_args__ = (
        CheckConstraint('user_rating IS NULL OR (user_rating >= 1 AND user_rating <= 5)', name='valid_rating'),
        CheckConstraint('confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)', name='valid_confidence'),
        CheckConstraint('tokens_used >= 0', name='non_negative_tokens'),
        CheckConstraint('is_bookmarked IN (0, 1)', name='boolean_bookmarked'),
        CheckConstraint(
            "answer_quality IS NULL OR answer_quality IN ('excellent','good','partial','low')",
            name='valid_answer_quality'
        ),
        CheckConstraint(
            "answer_origin IS NULL OR answer_origin IN ('neutralized','synthesized')",
            name='valid_answer_origin'
        ),
        Index('idx_exchanges_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_exchanges_timestamp', 'timestamp'),
        Index('idx_exchanges_bookmarked', 'is_bookmarked'),
    )

    @property
    def safety_flags(self) -> List[str]:
        """Get safety flags as Python list."""
        try:
            return json.loads(self.safety_flags_json or '[]')
        except json.JSONDecodeError:
            return []

    @safety_flags.setter
    def safety_flags(self, value: List[str]):
        """Set safety flags from Python list."""
        self.safety_flags_json = json.dumps(value or [])

    @property
    def document_references(self) -> List[str]:
        """Get document references as Python list."""
        try:
            return json.loads(self.document_references_json or '[]')
        except json.JSONDecodeError:
            return []

    @document_references.setter
    def document_references(self, value: List[str]):
        """Set document references from Python list."""
        self.document_references_json = json.dumps(value or [])