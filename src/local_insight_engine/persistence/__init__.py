"""
Persistence layer for LocalInsightEngine.
Handles long-term storage of Q&A sessions and document analysis results.
"""

from .database import DatabaseManager, get_database_manager

__all__ = ["DatabaseManager", "get_database_manager"]

__all__ = ['get_database_manager', 'DatabaseManager']
