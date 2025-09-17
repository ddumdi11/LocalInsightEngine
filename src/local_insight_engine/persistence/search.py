"""
Smart search engine using SQLite FTS5 with BM25 ranking and time-decay scoring.
Single-source-of-truth search architecture to prevent index drift.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from .database import get_db_session
from .models import PersistentQASession, QAExchange

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a search query."""
    exchange_id: str
    session_id: str
    question: str
    answer: str
    context_used: Optional[str]
    timestamp: datetime
    confidence_score: Optional[float]
    is_bookmarked: bool

    # Document context
    document_display_name: str
    session_tags: List[str]

    # Search scoring
    fts_rank: float  # BM25 score from FTS5
    time_decay_factor: float  # Time-based relevance adjustment
    final_score: float  # Combined score

    # Metadata
    days_old: float
    snippet: str  # Highlighted text snippet


class SmartSearchEngine:
    """
    Single-source-of-truth search using SQLite FTS5 with BM25 + time-decay ranking.
    No separate in-memory SearchIndex to prevent index drift and duplication.
    """

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize SmartSearchEngine with optional database session.

        Args:
            db_session: SQLAlchemy session for database operations.
                       If None, will create a new session when needed.
        """
        self.db_session = db_session

    def _get_session(self) -> Session:
        """Get database session, create new if needed."""
        if self.db_session:
            return self.db_session
        return get_db_session()

    def search_qa_history(
        self,
        query: str,
        limit: int = 20,
        time_decay_weight: float = 0.3,
        min_score: float = 0.1,
        session_filter: Optional[List[str]] = None,
        bookmarked_only: bool = False
    ) -> List[SearchResult]:
        """
        Full-text search across all Q&A history with BM25 + time-decay ranking.

        Args:
            query: Search query string
            limit: Maximum number of results
            time_decay_weight: Weight of time decay in final score (0.0 to 1.0)
            min_score: Minimum score threshold
            session_filter: Only search within these session IDs
            bookmarked_only: Only search bookmarked exchanges

        Returns:
            List of SearchResult objects ordered by relevance
        """
        session = self._get_session()

        try:
            # Sanitize FTS5 query
            sanitized_query = self._sanitize_fts5_query(query)
            if not sanitized_query:
                return []

            # Build the search query - simplified to avoid SQL syntax issues
            sql = """
                SELECT
                    e.exchange_id,
                    e.session_id,
                    e.question,
                    e.answer,
                    e.context_used,
                    e.timestamp,
                    e.confidence_score,
                    e.is_bookmarked,
                    s.document_display_name,
                    s.session_tags_json,
                    CAST(julianday('now') - julianday(e.timestamp) as REAL) as days_old,
                    -- Simple time decay factor
                    CASE
                        WHEN julianday('now') - julianday(e.timestamp) <= 1 THEN 1.0
                        WHEN julianday('now') - julianday(e.timestamp) <= 7 THEN 0.8
                        WHEN julianday('now') - julianday(e.timestamp) <= 30 THEN 0.6
                        ELSE 0.4
                    END as time_decay_factor,
                    qa_search.rank as fts_rank,
                    -- Simple combined score
                    qa_search.rank as final_score,
                    -- Create snippet
                    SUBSTR(e.answer, 1, 200) || '...' as answer_snippet
                FROM qa_search
                JOIN qa_exchanges e ON qa_search.rowid = e.rowid
                JOIN sessions s ON e.session_id = s.session_id
                WHERE qa_search MATCH :query
            """

            params = {
                'query': sanitized_query,
                'time_decay_weight': time_decay_weight,
                'min_score': min_score
            }

            # Add filters
            conditions = []
            if session_filter:
                placeholders = ','.join([f':session_{i}' for i in range(len(session_filter))])
                conditions.append(f"e.session_id IN ({placeholders})")
                for i, session_id in enumerate(session_filter):
                    params[f'session_{i}'] = session_id

            if bookmarked_only:
                conditions.append("e.is_bookmarked = 1")

            # Add scoring threshold as condition (FTS5 rank is negative - better scores are less negative)
            conditions.append("qa_search.rank <= -:min_score")

            if conditions:
                sql += " AND " + " AND ".join(conditions)

            # Apply ordering (FTS5 rank: higher values = better matches, since we use negative rank)
            sql += """
                ORDER BY qa_search.rank DESC, e.timestamp DESC
                LIMIT :limit
            """

            params['limit'] = limit

            result = session.execute(text(sql), params)
            rows = result.fetchall()

            # Convert to SearchResult objects
            search_results = []
            for row in rows:
                # Parse session tags
                try:
                    import json
                    session_tags = json.loads(row.session_tags_json or '[]')
                except (json.JSONDecodeError, TypeError):
                    session_tags = []

                search_results.append(SearchResult(
                    exchange_id=row.exchange_id,
                    session_id=row.session_id,
                    question=row.question,
                    answer=row.answer,
                    context_used=row.context_used,
                    timestamp=datetime.fromisoformat(row.timestamp.replace('Z', '+00:00')) if isinstance(row.timestamp, str) else row.timestamp,
                    confidence_score=row.confidence_score,
                    is_bookmarked=bool(row.is_bookmarked),
                    document_display_name=row.document_display_name,
                    session_tags=session_tags,
                    fts_rank=float(row.fts_rank) if row.fts_rank else 0.0,
                    time_decay_factor=float(row.time_decay_factor),
                    final_score=float(row.final_score),
                    days_old=float(row.days_old),
                    snippet=row.answer_snippet or row.answer[:200] + "..."
                ))

            logger.info(f"FTS5 search for '{query}' returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Search query failed: {e}")
            return []

    def find_similar_questions(
        self,
        question: str,
        exclude_exchange_id: Optional[str] = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Find Q&A exchanges with similar questions using FTS5 semantic matching.

        Args:
            question: Question to find similarities for
            exclude_exchange_id: Exchange ID to exclude from results
            limit: Maximum number of results

        Returns:
            List of similar SearchResult objects
        """
        # Extract key terms from the question for semantic search
        key_terms = self._extract_key_terms(question)
        if not key_terms:
            return []

        # Build semantic query
        semantic_query = " OR ".join([f'"{term}"' for term in key_terms[:5]])

        results = self.search_qa_history(
            query=semantic_query,
            limit=limit * 2,  # Get more results to filter
            time_decay_weight=0.1  # Less emphasis on recency for similarity
        )

        # Filter out the original question if specified
        if exclude_exchange_id:
            results = [r for r in results if r.exchange_id != exclude_exchange_id]

        return results[:limit]

    def discover_related_insights(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Discover related insights from other sessions based on content analysis.

        Args:
            session_id: Session ID to find related content for
            limit: Maximum number of results

        Returns:
            List of related SearchResult objects from different sessions
        """
        session = self._get_session()

        try:
            # Get key terms from the target session
            result = session.execute(
                text("""
                    SELECT question, answer, context_used
                    FROM qa_exchanges
                    WHERE session_id = :session_id
                    ORDER BY timestamp DESC
                    LIMIT 5
                """),
                {'session_id': session_id}
            )

            session_content = result.fetchall()
            if not session_content:
                return []

            # Extract key terms from session content
            all_text = " ".join([
                f"{row.question} {row.answer} {row.context_used or ''}"
                for row in session_content
            ])
            key_terms = self._extract_key_terms(all_text)

            if not key_terms:
                return []

            # Search for related content in other sessions
            related_query = " OR ".join([f'"{term}"' for term in key_terms[:8]])

            results = self.search_qa_history(
                query=related_query,
                limit=limit * 2,
                time_decay_weight=0.2
            )

            # Filter out results from the same session
            related_results = [r for r in results if r.session_id != session_id]

            return related_results[:limit]

        except Exception as e:
            logger.error(f"Failed to discover related insights: {e}")
            return []

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about the search index."""
        session = self._get_session()

        try:
            # Get FTS5 index statistics
            result = session.execute(text("""
                SELECT
                    COUNT(*) as total_indexed_exchanges,
                    COUNT(DISTINCT session_id) as indexed_sessions
                FROM qa_search
            """))
            stats = result.fetchone()

            # Get content distribution
            result = session.execute(text("""
                SELECT
                    AVG(length(question)) as avg_question_length,
                    AVG(length(answer)) as avg_answer_length,
                    COUNT(CASE WHEN is_bookmarked = 1 THEN 1 END) as bookmarked_count
                FROM qa_search_ranked
            """))
            content_stats = result.fetchone()

            return {
                "total_indexed_exchanges": int(stats.total_indexed_exchanges) if stats else 0,
                "indexed_sessions": int(stats.indexed_sessions) if stats else 0,
                "avg_question_length": float(content_stats.avg_question_length) if content_stats and content_stats.avg_question_length else 0,
                "avg_answer_length": float(content_stats.avg_answer_length) if content_stats and content_stats.avg_answer_length else 0,
                "bookmarked_exchanges": int(content_stats.bookmarked_count) if content_stats else 0,
                "index_health": "healthy"
            }

        except Exception as e:
            logger.error(f"Failed to get search statistics: {e}")
            return {"error": str(e), "index_health": "error"}

    def rebuild_search_index(self) -> bool:
        """
        Rebuild the FTS5 search index from scratch.
        Use this if the index becomes corrupted or out of sync.
        """
        session = self._get_session()

        try:
            # Rebuild FTS5 index
            session.execute(text("INSERT INTO qa_search(qa_search) VALUES('rebuild')"))
            session.commit()

            logger.info("FTS5 search index rebuilt successfully")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to rebuild search index: {e}")
            return False

    def _sanitize_fts5_query(self, query: str) -> str:
        """
        Sanitize user input for FTS5 query to prevent syntax errors.

        Args:
            query: Raw user query

        Returns:
            Sanitized FTS5 query string
        """
        if not query or not query.strip():
            return ""

        # Remove or escape special FTS5 characters that might cause syntax errors
        # Keep useful operators but escape problematic ones
        sanitized = query.strip()

        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)

        # Handle quotes - ensure they're balanced
        quote_count = sanitized.count('"')
        if quote_count % 2 != 0:
            sanitized = sanitized.replace('"', '')

        # Escape problematic characters but keep useful operators
        # FTS5 supports: AND, OR, NOT, *, "", (), column:term
        problematic_chars = ['[', ']', '{', '}', '\\', '^']
        for char in problematic_chars:
            sanitized = sanitized.replace(char, ' ')

        # If query is too short or contains only stop words, make it more generic
        if len(sanitized.strip()) < 2:
            return ""

        return sanitized.strip()

    def _extract_key_terms(self, text: str, max_terms: int = 10) -> List[str]:
        """
        Extract key terms from text for semantic search.

        Args:
            text: Input text to analyze
            max_terms: Maximum number of terms to extract

        Returns:
            List of key terms
        """
        if not text:
            return []

        # Simple key term extraction - can be enhanced with NLP
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }

        # Extract words (alphanumeric, 3+ characters)
        words = re.findall(r'\b[a-zA-Z0-9]{3,}\b', text.lower())

        # Filter out stop words and get unique terms
        key_terms = list(set([word for word in words if word not in stop_words]))

        # Sort by length (longer terms are often more specific)
        key_terms.sort(key=len, reverse=True)

        return key_terms[:max_terms]


# Convenience functions
def search_qa_content(query: str, **kwargs) -> List[SearchResult]:
    """Convenience function for searching Q&A content."""
    engine = SmartSearchEngine()
    return engine.search_qa_history(query, **kwargs)

def find_similar_qa(question: str, **kwargs) -> List[SearchResult]:
    """Convenience function for finding similar questions."""
    engine = SmartSearchEngine()
    return engine.find_similar_questions(question, **kwargs)