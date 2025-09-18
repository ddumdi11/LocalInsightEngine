"""
Persistence layer for LocalInsightEngine.
Handles long-term storage of Q&A sessions and document analysis results.
"""

from .database import DatabaseManager

# Global database manager instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get or create global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

__all__ = ['get_database_manager', 'DatabaseManager']