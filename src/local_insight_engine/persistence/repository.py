"""
Repository pattern for managing persistent Q&A sessions.
Provides high-level CRUD operations and business logic.
"""

import logging
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, asc, func, or_, and_

from .database import get_db_session
from .models import PersistentQASession, QAExchange
from .search import SmartSearchEngine, SearchResult
from ..models.analysis import AnalysisResult

logger = logging.getLogger(__name__)


class SessionRepository:
    """
    Repository for managing persistent Q&A sessions.
    Handles CRUD operations and business logic.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.search_engine = SmartSearchEngine(db_session)

    def _get_session(self) -> Session:
        """Get database session, create new if needed."""
        if self.db_session:
            return self.db_session
        return get_db_session()

    def create_session(
        self,
        document_path: Path,
        analysis_result: AnalysisResult,
        neutralized_context: Optional[str] = None,
        display_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> PersistentQASession:
        """
        Create a new persistent Q&A session.

        Args:
            document_path: Path to the source document
            analysis_result: Analysis result from the engine
            neutralized_context: Copyright-safe neutralized content
            display_name: Optional display name for the document
            tags: Optional list of tags
            **kwargs: Additional session parameters

        Returns:
            Created PersistentQASession instance

        Raises:
            IntegrityError: If session with same document hash already exists
        """
        session = self._get_session()

        try:
            # Generate document hashes
            canonical_path = str(document_path.resolve())
            document_hash = self._generate_document_hash(document_path)
            path_hash = self._generate_path_hash(canonical_path)

            # Create session
            qa_session = PersistentQASession(
                document_path_hash=path_hash,
                pepper_id="default_pepper_v1",  # TODO: Implement proper pepper management
                document_hash=document_hash,
                document_display_name=display_name or document_path.name,
                neutralized_context=neutralized_context,
                analysis_result=analysis_result,
                session_tags=tags or [],
                **kwargs
            )

            session.add(qa_session)
            session.commit()
            session.refresh(qa_session)

            logger.info(f"Created new session {qa_session.session_id} for document {display_name or document_path.name}")
            return qa_session

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Failed to create session - document already exists: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create session: {e}")
            raise

    def get_session_by_id(self, session_id: str) -> Optional[PersistentQASession]:
        """Get session by ID."""
        session = self._get_session()
        qa_session = session.query(PersistentQASession).filter(
            PersistentQASession.session_id == session_id
        ).first()

        if qa_session:
            qa_session.update_last_accessed()
            session.commit()

        return qa_session

    def get_session_by_document_hash(self, document_hash: str) -> Optional[PersistentQASession]:
        """Get session by document hash."""
        session = self._get_session()
        return session.query(PersistentQASession).filter(
            PersistentQASession.document_hash == document_hash
        ).first()

    def list_sessions(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "last_accessed",
        ascending: bool = False,
        favorites_only: bool = False,
        tags_filter: Optional[List[str]] = None
    ) -> List[PersistentQASession]:
        """
        List sessions with filtering and pagination.

        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            order_by: Field to order by ('last_accessed', 'created_at', 'total_questions')
            ascending: Sort order (False = descending)
            favorites_only: Only return favorite sessions
            tags_filter: Only return sessions with any of these tags

        Returns:
            List of PersistentQASession instances
        """
        session = self._get_session()
        query = session.query(PersistentQASession)

        # Apply filters
        if favorites_only:
            query = query.filter(PersistentQASession.is_favorite == True)

        if tags_filter:
            # SQLite JSON filtering - check if any tag matches
            tag_conditions = []
            for tag in tags_filter:
                tag_conditions.append(
                    PersistentQASession.session_tags_json.contains(f'"{tag}"')
                )
            query = query.filter(or_(*tag_conditions))

        # Apply ordering
        order_field = getattr(PersistentQASession, order_by, PersistentQASession.last_accessed)
        if ascending:
            query = query.order_by(asc(order_field))
        else:
            query = query.order_by(desc(order_field))

        # Apply pagination
        if offset > 0:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        return query.all()

    def update_session(self, session_id: str, **updates) -> Optional[PersistentQASession]:
        """Update session with given parameters."""
        session = self._get_session()
        qa_session = self.get_session_by_id(session_id)

        if not qa_session:
            return None

        try:
            for key, value in updates.items():
                if hasattr(qa_session, key):
                    setattr(qa_session, key, value)

            qa_session.update_last_accessed()
            session.commit()
            session.refresh(qa_session)

            logger.info(f"Updated session {session_id}")
            return qa_session

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update session {session_id}: {e}")
            raise

    def delete_session(self, session_id: str) -> bool:
        """Delete session and all associated Q&A exchanges."""
        session = self._get_session()
        qa_session = self.get_session_by_id(session_id)

        if not qa_session:
            return False

        try:
            session.delete(qa_session)
            session.commit()
            logger.info(f"Deleted session {session_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    def add_qa_exchange(
        self,
        session_id: str,
        question: str,
        answer: str,
        **kwargs
    ) -> Optional[QAExchange]:
        """Add a Q&A exchange to an existing session."""
        session = self._get_session()
        qa_session = self.get_session_by_id(session_id)

        if not qa_session:
            logger.error(f"Session {session_id} not found")
            return None

        try:
            exchange = qa_session.add_qa_exchange(question, answer, **kwargs)
            session.commit()
            session.refresh(exchange)

            logger.info(f"Added Q&A exchange to session {session_id}")
            return exchange

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add Q&A exchange to session {session_id}: {e}")
            raise

    def get_qa_exchanges(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[QAExchange]:
        """Get Q&A exchanges for a session, ordered by timestamp."""
        session = self._get_session()
        query = session.query(QAExchange).filter(
            QAExchange.session_id == session_id
        ).order_by(asc(QAExchange.timestamp))

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_session_timeline(
        self,
        session_id: str,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Get complete timeline view of a session with chronological Q&A exchanges.

        Args:
            session_id: Session ID to get timeline for
            include_metadata: Include session metadata and statistics

        Returns:
            Dictionary with session info and chronological timeline
        """
        session = self._get_session()

        # Get session
        qa_session = self.get_session_by_id(session_id)
        if not qa_session:
            return {}

        # Get all Q&A exchanges chronologically
        exchanges = session.query(QAExchange).filter(
            QAExchange.session_id == session_id
        ).order_by(asc(QAExchange.timestamp)).all()

        timeline = {
            "session_id": session_id,
            "document_display_name": qa_session.document_display_name,
            "session_tags": qa_session.session_tags,
            "created_at": qa_session.created_at,
            "last_accessed": qa_session.last_accessed,
            "total_questions": len(exchanges),
            "is_favorite": qa_session.is_favorite,
            "timeline_events": []
        }

        if include_metadata:
            timeline.update({
                "auto_generated_summary": qa_session.auto_generated_summary,
                "key_insights": qa_session.key_insights,
                "analysis_summary": qa_session.analysis_result.executive_summary if qa_session.analysis_result else None,
                "session_statistics": {
                    "total_tokens_used": sum(e.tokens_used for e in exchanges),
                    "avg_confidence": sum(e.confidence_score for e in exchanges if e.confidence_score) / len([e for e in exchanges if e.confidence_score]) if exchanges else 0,
                    "bookmarked_count": sum(1 for e in exchanges if e.is_bookmarked),
                    "avg_processing_time": sum(e.processing_time for e in exchanges if e.processing_time) / len([e for e in exchanges if e.processing_time]) if exchanges else 0
                }
            })

        # Build chronological timeline events
        for i, exchange in enumerate(exchanges):
            event = {
                "event_type": "qa_exchange",
                "sequence_number": i + 1,
                "exchange_id": exchange.exchange_id,
                "timestamp": exchange.timestamp,
                "question": exchange.question,
                "answer": exchange.answer,
                "confidence_score": exchange.confidence_score,
                "tokens_used": exchange.tokens_used,
                "processing_time": exchange.processing_time,
                "user_rating": exchange.user_rating,
                "is_bookmarked": exchange.is_bookmarked,
                "user_notes": exchange.user_notes,
                "claude_model": exchange.claude_model,
                "safety_flags": exchange.safety_flags,
                "answer_quality": exchange.answer_quality
            }

            # Add relative timing information
            if i == 0:
                event["time_since_session_start"] = "Session started"
                event["time_since_previous"] = None
            else:
                prev_exchange = exchanges[i-1]
                time_diff = exchange.timestamp - prev_exchange.timestamp
                event["time_since_previous"] = str(time_diff)

                session_diff = exchange.timestamp - qa_session.created_at
                event["time_since_session_start"] = str(session_diff)

            timeline["timeline_events"].append(event)

        return timeline

    def get_session_activity_summary(
        self,
        session_id: str,
        group_by_period: str = "day"  # "hour", "day", "week"
    ) -> Dict[str, Any]:
        """
        Get activity summary for a session grouped by time periods.

        Args:
            session_id: Session ID to analyze
            group_by_period: Time period for grouping ("hour", "day", "week")

        Returns:
            Activity summary with time-based statistics
        """
        session = self._get_session()

        # Get all exchanges for the session
        exchanges = session.query(QAExchange).filter(
            QAExchange.session_id == session_id
        ).order_by(asc(QAExchange.timestamp)).all()

        if not exchanges:
            return {"session_id": session_id, "activity_periods": [], "total_periods": 0}

        # Group exchanges by time period
        from collections import defaultdict
        periods = defaultdict(list)

        for exchange in exchanges:
            if group_by_period == "hour":
                period_key = exchange.timestamp.strftime("%Y-%m-%d %H:00")
            elif group_by_period == "day":
                period_key = exchange.timestamp.strftime("%Y-%m-%d")
            elif group_by_period == "week":
                # Get start of week (Monday)
                week_start = exchange.timestamp - timedelta(days=exchange.timestamp.weekday())
                period_key = week_start.strftime("%Y-%m-%d") + " (Week)"
            else:
                period_key = exchange.timestamp.strftime("%Y-%m-%d")

            periods[period_key].append(exchange)

        # Build activity summary
        activity_periods = []
        for period_key, period_exchanges in sorted(periods.items()):
            period_stats = {
                "period": period_key,
                "exchange_count": len(period_exchanges),
                "total_tokens": sum(e.tokens_used for e in period_exchanges),
                "avg_confidence": sum(e.confidence_score for e in period_exchanges if e.confidence_score) / len([e for e in period_exchanges if e.confidence_score]) if period_exchanges else 0,
                "bookmarked_count": sum(1 for e in period_exchanges if e.is_bookmarked),
                "questions": [e.question[:100] + "..." if len(e.question) > 100 else e.question for e in period_exchanges]
            }
            activity_periods.append(period_stats)

        return {
            "session_id": session_id,
            "group_by_period": group_by_period,
            "activity_periods": activity_periods,
            "total_periods": len(activity_periods),
            "total_exchanges": len(exchanges),
            "date_range": {
                "start": exchanges[0].timestamp.isoformat(),
                "end": exchanges[-1].timestamp.isoformat()
            }
        }

    def search_sessions(self, search_term: str, limit: int = 20) -> List[PersistentQASession]:
        """
        Search sessions by display name, tags, or summary.
        Basic implementation for session metadata search.
        """
        session = self._get_session()
        search_pattern = f"%{search_term}%"

        return session.query(PersistentQASession).filter(
            or_(
                PersistentQASession.document_display_name.ilike(search_pattern),
                PersistentQASession.session_tags_json.ilike(search_pattern),
                PersistentQASession.auto_generated_summary.ilike(search_pattern)
            )
        ).order_by(desc(PersistentQASession.last_accessed)).limit(limit).all()

    # New FTS5-powered search methods

    def search_qa_content(
        self,
        query: str,
        limit: int = 20,
        time_decay_weight: float = 0.3,
        min_score: float = 0.1,
        session_filter: Optional[List[str]] = None,
        bookmarked_only: bool = False
    ) -> List[SearchResult]:
        """
        Full-text search across all Q&A content using FTS5.

        Args:
            query: Search query string
            limit: Maximum number of results
            time_decay_weight: Weight of time decay in scoring (0.0-1.0)
            min_score: Minimum score threshold for results
            session_filter: Only search within these session IDs
            bookmarked_only: Only search bookmarked exchanges

        Returns:
            List of SearchResult objects ordered by relevance
        """
        return self.search_engine.search_qa_history(
            query=query,
            limit=limit,
            time_decay_weight=time_decay_weight,
            min_score=min_score,
            session_filter=session_filter,
            bookmarked_only=bookmarked_only
        )

    def find_similar_questions(
        self,
        question: str,
        exclude_exchange_id: Optional[str] = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Find Q&A exchanges with similar questions.

        Args:
            question: Question to find similarities for
            exclude_exchange_id: Exchange ID to exclude from results
            limit: Maximum number of results

        Returns:
            List of similar SearchResult objects
        """
        return self.search_engine.find_similar_questions(
            question=question,
            exclude_exchange_id=exclude_exchange_id,
            limit=limit
        )

    def get_related_insights(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Get insights from other sessions related to the given session.

        Args:
            session_id: Session ID to find related content for
            limit: Maximum number of results

        Returns:
            List of related SearchResult objects from different sessions
        """
        return self.search_engine.discover_related_insights(
            session_id=session_id,
            limit=limit
        )

    def search_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        limit: int = 20
    ) -> List[SearchResult]:
        """
        Search Q&A content by session tags.

        Args:
            tags: List of tags to search for
            match_all: If True, match all tags; if False, match any tag
            limit: Maximum number of results

        Returns:
            List of SearchResult objects from sessions with matching tags
        """
        # Convert tags to search query
        if match_all:
            # Use AND logic: all tags must be present
            query = " AND ".join([f'"{tag}"' for tag in tags])
        else:
            # Use OR logic: any tag matches
            query = " OR ".join([f'"{tag}"' for tag in tags])

        return self.search_engine.search_qa_history(
            query=query,
            limit=limit,
            time_decay_weight=0.1  # Less emphasis on recency for tag searches
        )

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about the FTS5 search index."""
        base_stats = super().get_session_statistics()
        search_stats = self.search_engine.get_search_statistics()

        return {
            **base_stats,
            "search_index": search_stats
        }

    def rebuild_search_index(self) -> bool:
        """
        Rebuild the FTS5 search index from scratch.
        Use this if the index becomes corrupted or out of sync.
        """
        return self.search_engine.rebuild_search_index()

    # Enhanced Bookmarks & Favorites System

    def toggle_session_favorite(self, session_id: str) -> bool:
        """Toggle favorite status of a session."""
        qa_session = self.get_session_by_id(session_id)
        if not qa_session:
            return False

        qa_session.is_favorite = not qa_session.is_favorite
        qa_session.update_last_accessed()

        session = self._get_session()
        session.commit()
        logger.info(f"Session {session_id} favorite status: {qa_session.is_favorite}")
        return qa_session.is_favorite

    def toggle_exchange_bookmark(self, exchange_id: str) -> bool:
        """Toggle bookmark status of a Q&A exchange."""
        session = self._get_session()
        exchange = session.query(QAExchange).filter(
            QAExchange.exchange_id == exchange_id
        ).first()

        if not exchange:
            return False

        exchange.is_bookmarked = not exchange.is_bookmarked
        session.commit()
        logger.info(f"Exchange {exchange_id} bookmark status: {exchange.is_bookmarked}")
        return exchange.is_bookmarked

    def rate_qa_exchange(self, exchange_id: str, rating: int) -> bool:
        """
        Rate a Q&A exchange (1-5 stars).

        Args:
            exchange_id: Exchange ID to rate
            rating: Rating from 1 to 5

        Returns:
            True if rating was successful
        """
        if not (1 <= rating <= 5):
            logger.error(f"Invalid rating {rating}. Must be 1-5")
            return False

        session = self._get_session()
        exchange = session.query(QAExchange).filter(
            QAExchange.exchange_id == exchange_id
        ).first()

        if not exchange:
            return False

        exchange.user_rating = rating
        session.commit()
        logger.info(f"Exchange {exchange_id} rated: {rating}/5")
        return True

    def add_exchange_notes(self, exchange_id: str, notes: str) -> bool:
        """Add or update user notes for a Q&A exchange."""
        session = self._get_session()
        exchange = session.query(QAExchange).filter(
            QAExchange.exchange_id == exchange_id
        ).first()

        if not exchange:
            return False

        exchange.user_notes = notes.strip() if notes else None
        session.commit()
        logger.info(f"Notes updated for exchange {exchange_id}")
        return True

    def get_favorite_sessions(
        self,
        limit: Optional[int] = None,
        order_by: str = "last_accessed"
    ) -> List[PersistentQASession]:
        """Get all favorite sessions."""
        return self.list_sessions(
            limit=limit,
            order_by=order_by,
            favorites_only=True
        )

    def get_bookmarked_exchanges(
        self,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[QAExchange]:
        """
        Get bookmarked Q&A exchanges, optionally filtered by session.

        Args:
            session_id: Optional session ID to filter by
            limit: Maximum number of results

        Returns:
            List of bookmarked QAExchange objects
        """
        session = self._get_session()
        query = session.query(QAExchange).filter(
            QAExchange.is_bookmarked == True
        )

        if session_id:
            query = query.filter(QAExchange.session_id == session_id)

        return query.order_by(desc(QAExchange.timestamp)).limit(limit).all()

    def get_highly_rated_exchanges(
        self,
        min_rating: int = 4,
        limit: int = 50
    ) -> List[QAExchange]:
        """Get highly rated Q&A exchanges."""
        session = self._get_session()
        return session.query(QAExchange).filter(
            QAExchange.user_rating >= min_rating
        ).order_by(desc(QAExchange.user_rating), desc(QAExchange.timestamp)).limit(limit).all()

    def get_user_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about user's bookmarks and favorites."""
        session = self._get_session()

        # Favorite sessions
        favorite_sessions = session.query(func.count(PersistentQASession.session_id)).filter(
            PersistentQASession.is_favorite == True
        ).scalar()

        # Bookmarked exchanges
        bookmarked_exchanges = session.query(func.count(QAExchange.exchange_id)).filter(
            QAExchange.is_bookmarked == True
        ).scalar()

        # Rated exchanges
        rated_exchanges = session.query(func.count(QAExchange.exchange_id)).filter(
            QAExchange.user_rating.is_not(None)
        ).scalar()

        # Average rating
        avg_rating = session.query(func.avg(QAExchange.user_rating)).filter(
            QAExchange.user_rating.is_not(None)
        ).scalar()

        # Exchanges with notes
        exchanges_with_notes = session.query(func.count(QAExchange.exchange_id)).filter(
            QAExchange.user_notes.is_not(None),
            QAExchange.user_notes != ""
        ).scalar()

        return {
            "favorite_sessions": int(favorite_sessions) if favorite_sessions else 0,
            "bookmarked_exchanges": int(bookmarked_exchanges) if bookmarked_exchanges else 0,
            "rated_exchanges": int(rated_exchanges) if rated_exchanges else 0,
            "avg_rating": float(avg_rating) if avg_rating else 0.0,
            "exchanges_with_notes": int(exchanges_with_notes) if exchanges_with_notes else 0
        }

    def export_user_collection(
        self,
        include_favorites: bool = True,
        include_bookmarks: bool = True,
        include_ratings: bool = True,
        include_notes: bool = True
    ) -> Dict[str, Any]:
        """
        Export user's personal collection (favorites, bookmarks, ratings, notes).

        Args:
            include_favorites: Include favorite sessions
            include_bookmarks: Include bookmarked exchanges
            include_ratings: Include ratings
            include_notes: Include user notes

        Returns:
            Dictionary with user's personal collection data
        """
        collection = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "collection_stats": self.get_user_collection_stats()
        }

        if include_favorites:
            favorite_sessions = self.get_favorite_sessions()
            collection["favorite_sessions"] = [
                {
                    "session_id": s.session_id,
                    "document_display_name": s.document_display_name,
                    "session_tags": s.session_tags,
                    "created_at": s.created_at.isoformat(),
                    "last_accessed": s.last_accessed.isoformat(),
                    "total_questions": s.total_questions,
                    "auto_generated_summary": s.auto_generated_summary
                }
                for s in favorite_sessions
            ]

        if include_bookmarks:
            bookmarked = self.get_bookmarked_exchanges()
            collection["bookmarked_exchanges"] = [
                {
                    "exchange_id": e.exchange_id,
                    "session_id": e.session_id,
                    "question": e.question,
                    "answer": e.answer,
                    "timestamp": e.timestamp.isoformat(),
                    "confidence_score": e.confidence_score,
                    "user_rating": e.user_rating if include_ratings else None,
                    "user_notes": e.user_notes if include_notes else None
                }
                for e in bookmarked
            ]

        if include_ratings:
            highly_rated = self.get_highly_rated_exchanges(min_rating=1)  # Get all rated
            collection["rated_exchanges"] = [
                {
                    "exchange_id": e.exchange_id,
                    "session_id": e.session_id,
                    "question": e.question[:200] + "..." if len(e.question) > 200 else e.question,
                    "rating": e.user_rating,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in highly_rated
            ]

        return collection

    # Advanced Cross-Session Intelligence

    def discover_knowledge_patterns(
        self,
        min_session_count: int = 2,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Discover patterns and themes that appear across multiple sessions.

        Args:
            min_session_count: Minimum number of sessions a pattern must appear in
            limit: Maximum number of patterns to return

        Returns:
            List of knowledge patterns with cross-session statistics
        """
        # Use FTS5 to find common terms across sessions
        search_engine = self.search_engine
        session = self._get_session()

        # Get all unique words from questions and answers
        result = session.execute(text("""
            SELECT question, answer, session_id
            FROM qa_exchanges
            ORDER BY timestamp DESC
        """))

        # Build word frequency analysis across sessions
        from collections import defaultdict
        word_sessions = defaultdict(set)  # word -> set of session_ids
        word_frequency = defaultdict(int)  # word -> total count

        for row in result:
            text_content = f"{row.question} {row.answer}".lower()
            # Simple word extraction
            words = search_engine._extract_key_terms(text_content)

            for word in words:
                if len(word) > 3:  # Filter short words
                    word_sessions[word].add(row.session_id)
                    word_frequency[word] += 1

        # Find patterns that appear in multiple sessions
        patterns = []
        for word, session_set in word_sessions.items():
            if len(session_set) >= min_session_count:
                # Get sessions for this pattern
                session_names = []
                for session_id in list(session_set)[:5]:  # Limit to 5 sessions
                    qa_session = self.get_session_by_id(session_id)
                    if qa_session:
                        session_names.append(qa_session.document_display_name)

                patterns.append({
                    "pattern": word,
                    "session_count": len(session_set),
                    "total_mentions": word_frequency[word],
                    "avg_mentions_per_session": word_frequency[word] / len(session_set),
                    "example_sessions": session_names[:3],
                    "relevance_score": len(session_set) * word_frequency[word]
                })

        # Sort by relevance and return top results
        patterns.sort(key=lambda p: p["relevance_score"], reverse=True)
        return patterns[:limit]

    def suggest_follow_up_questions(
        self,
        session_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Suggest follow-up questions based on current session and related sessions.

        Args:
            session_id: Current session ID
            limit: Maximum number of suggestions

        Returns:
            List of suggested questions with reasoning
        """
        # Get related sessions
        related_results = self.get_related_insights(session_id, limit=10)

        if not related_results:
            return []

        # Analyze questions from related sessions
        suggestions = []
        seen_questions = set()

        for result in related_results:
            # Skip if we've seen a very similar question
            question_key = result.question.lower()[:50]
            if question_key in seen_questions:
                continue
            seen_questions.add(question_key)

            # Create suggestion with context
            suggestion = {
                "suggested_question": result.question,
                "reasoning": f"Users with similar interests asked this in '{result.document_display_name}'",
                "source_session_id": result.session_id,
                "source_document": result.document_display_name,
                "confidence": result.confidence_score,
                "is_bookmarked_elsewhere": result.is_bookmarked,
                "similarity_score": result.final_score
            }
            suggestions.append(suggestion)

            if len(suggestions) >= limit:
                break

        return suggestions

    def analyze_session_evolution(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Analyze how a session evolved over time - topic progression, complexity changes, etc.

        Args:
            session_id: Session to analyze

        Returns:
            Analysis of session evolution patterns
        """
        exchanges = self.get_qa_exchanges(session_id)
        if len(exchanges) < 2:
            return {"error": "Not enough exchanges to analyze evolution"}

        # Analyze progression
        evolution = {
            "session_id": session_id,
            "total_exchanges": len(exchanges),
            "time_span": str(exchanges[-1].timestamp - exchanges[0].timestamp),
            "progression_analysis": []
        }

        # Analyze changes over time
        prev_topics = set()
        for i, exchange in enumerate(exchanges):
            # Extract key topics from this exchange
            topics = set(self.search_engine._extract_key_terms(
                f"{exchange.question} {exchange.answer}"
            )[:10])

            if i == 0:
                progression = {
                    "exchange_number": i + 1,
                    "timestamp": exchange.timestamp.isoformat(),
                    "evolution_type": "session_start",
                    "new_topics": list(topics),
                    "continued_topics": [],
                    "complexity_indicator": len(exchange.question.split()) + len(exchange.answer.split())
                }
            else:
                new_topics = topics - prev_topics
                continued_topics = topics & prev_topics

                # Determine evolution type
                if len(new_topics) > len(continued_topics):
                    evolution_type = "topic_expansion"
                elif len(continued_topics) > len(new_topics):
                    evolution_type = "topic_deepening"
                else:
                    evolution_type = "balanced_progression"

                progression = {
                    "exchange_number": i + 1,
                    "timestamp": exchange.timestamp.isoformat(),
                    "evolution_type": evolution_type,
                    "new_topics": list(new_topics)[:5],
                    "continued_topics": list(continued_topics)[:5],
                    "complexity_indicator": len(exchange.question.split()) + len(exchange.answer.split()),
                    "time_since_previous": str(exchange.timestamp - exchanges[i-1].timestamp)
                }

            evolution["progression_analysis"].append(progression)
            prev_topics = topics

        return evolution

    def find_complementary_sessions(
        self,
        session_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find sessions that complement the current session (cover related but different topics).

        Args:
            session_id: Session to find complements for
            limit: Maximum number of results

        Returns:
            List of complementary sessions with explanations
        """
        current_session = self.get_session_by_id(session_id)
        if not current_session:
            return []

        # Get current session topics
        current_exchanges = self.get_qa_exchanges(session_id)
        current_topics = set()
        for exchange in current_exchanges:
            topics = self.search_engine._extract_key_terms(
                f"{exchange.question} {exchange.answer}"
            )
            current_topics.update(topics[:10])

        # Find sessions with overlapping but different topic focus
        all_sessions = self.list_sessions(limit=100)  # Get more sessions to analyze
        complementary = []

        for other_session in all_sessions:
            if other_session.session_id == session_id:
                continue

            # Get topics from other session
            other_exchanges = self.get_qa_exchanges(other_session.session_id)
            other_topics = set()
            for exchange in other_exchanges:
                topics = self.search_engine._extract_key_terms(
                    f"{exchange.question} {exchange.answer}"
                )
                other_topics.update(topics[:10])

            # Calculate complementarity
            overlap = current_topics & other_topics
            unique_to_other = other_topics - current_topics

            if overlap and unique_to_other:
                overlap_ratio = len(overlap) / (len(current_topics) + len(other_topics) - len(overlap))
                complement_ratio = len(unique_to_other) / len(other_topics) if other_topics else 0

                # Good complement: some overlap but substantial unique content
                if 0.1 <= overlap_ratio <= 0.4 and complement_ratio >= 0.3:
                    complementary.append({
                        "session_id": other_session.session_id,
                        "document_display_name": other_session.document_display_name,
                        "session_tags": other_session.session_tags,
                        "overlap_topics": list(overlap)[:5],
                        "unique_topics": list(unique_to_other)[:5],
                        "overlap_ratio": overlap_ratio,
                        "complement_ratio": complement_ratio,
                        "complementarity_score": complement_ratio * (1 + len(overlap)),
                        "explanation": f"Shares {len(overlap)} topics but adds {len(unique_to_other)} new perspectives"
                    })

        # Sort by complementarity score
        complementary.sort(key=lambda c: c["complementarity_score"], reverse=True)
        return complementary[:limit]

    def generate_knowledge_graph_data(
        self,
        focus_session_id: Optional[str] = None,
        max_sessions: int = 20
    ) -> Dict[str, Any]:
        """
        Generate data for knowledge graph visualization showing connections between sessions.

        Args:
            focus_session_id: Optional session to focus the graph around
            max_sessions: Maximum number of sessions to include

        Returns:
            Graph data with nodes (sessions) and edges (relationships)
        """
        if focus_session_id:
            # Start with focus session and find related ones
            focus_session = self.get_session_by_id(focus_session_id)
            if not focus_session:
                return {"error": "Focus session not found"}

            related = self.get_related_insights(focus_session_id, limit=max_sessions-1)
            session_ids = {focus_session_id} | {r.session_id for r in related}
        else:
            # Use most recent sessions
            sessions = self.list_sessions(limit=max_sessions)
            session_ids = {s.session_id for s in sessions}

        # Build nodes
        nodes = []
        for session_id in session_ids:
            session_obj = self.get_session_by_id(session_id)
            if not session_obj:
                continue

            exchanges = self.get_qa_exchanges(session_id)
            node = {
                "id": session_id,
                "label": session_obj.document_display_name,
                "tags": session_obj.session_tags,
                "question_count": len(exchanges),
                "is_favorite": session_obj.is_favorite,
                "is_focus": session_id == focus_session_id,
                "node_size": min(len(exchanges) * 2 + 10, 50),  # Size based on activity
                "created_at": session_obj.created_at.isoformat()
            }
            nodes.append(node)

        # Build edges (relationships)
        edges = []
        session_list = list(session_ids)

        for i, session_a in enumerate(session_list):
            for session_b in session_list[i+1:]:
                # Find relationship strength using search
                related_results = self.get_related_insights(session_a, limit=50)
                relationship_strength = 0

                for result in related_results:
                    if result.session_id == session_b:
                        relationship_strength = result.final_score
                        break

                if relationship_strength > 0.1:  # Threshold for showing connection
                    edges.append({
                        "source": session_a,
                        "target": session_b,
                        "weight": relationship_strength,
                        "relationship_type": "content_similarity"
                    })

        return {
            "nodes": nodes,
            "edges": edges,
            "focus_session": focus_session_id,
            "graph_stats": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "avg_connections": len(edges) * 2 / len(nodes) if nodes else 0
            }
        }

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about stored sessions."""
        session = self._get_session()

        total_sessions = session.query(func.count(PersistentQASession.session_id)).scalar()
        total_exchanges = session.query(func.count(QAExchange.exchange_id)).scalar()
        favorite_sessions = session.query(func.count(PersistentQASession.session_id)).filter(
            PersistentQASession.is_favorite == True
        ).scalar()

        # Get most recent activity
        latest_session = session.query(PersistentQASession).order_by(
            desc(PersistentQASession.last_accessed)
        ).first()

        return {
            "total_sessions": total_sessions,
            "total_qa_exchanges": total_exchanges,
            "favorite_sessions": favorite_sessions,
            "latest_activity": latest_session.last_accessed if latest_session else None
        }

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions based on retention policy."""
        session = self._get_session()
        current_time = datetime.now(timezone.utc)

        expired_sessions = session.query(PersistentQASession).filter(
            PersistentQASession.created_at + func.julianday(PersistentQASession.retention_days) < current_time
        ).all()

        count = len(expired_sessions)
        if count > 0:
            for expired in expired_sessions:
                session.delete(expired)
            session.commit()
            logger.info(f"Cleaned up {count} expired sessions")

        return count

    def _generate_document_hash(self, document_path: Path) -> str:
        """Generate hash of document content."""
        try:
            with open(document_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Failed to generate document hash: {e}")
            # Fallback to path-based hash
            return hashlib.sha256(str(document_path).encode()).hexdigest()

    def _generate_path_hash(self, canonical_path: str, pepper: str = "default_pepper") -> str:
        """Generate HMAC hash of document path with pepper for security."""
        # TODO: Implement proper pepper management with KMS
        pepper_bytes = pepper.encode('utf-8')
        path_bytes = canonical_path.encode('utf-8')
        return hmac.new(pepper_bytes, path_bytes, hashlib.sha256).hexdigest()


# Convenience functions for common operations
def create_session_for_document(
    document_path: Path,
    analysis_result: AnalysisResult,
    **kwargs
) -> PersistentQASession:
    """Convenience function to create a session for a document."""
    repo = SessionRepository()
    return repo.create_session(document_path, analysis_result, **kwargs)

def get_session_by_id(session_id: str) -> Optional[PersistentQASession]:
    """Convenience function to get session by ID."""
    repo = SessionRepository()
    return repo.get_session_by_id(session_id)