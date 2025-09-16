"""
Database configuration and setup for LocalInsightEngine persistence layer.
"""

import logging
from pathlib import Path
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional

logger = logging.getLogger(__name__)

# SQLAlchemy Base for all models
Base = declarative_base()

class DatabaseManager:
    """Manages SQLite database connection and setup."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path("data/qa_sessions.db")

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # SQLite connection string with optimizations
        db_url = f"sqlite:///{self.db_path}"

        self.engine = create_engine(
            db_url,
            echo=False,  # Set to True for SQL logging during development
            pool_pre_ping=True,
            connect_args={
                "check_same_thread": False,  # Allow multi-threading
                "timeout": 20
            }
        )

        # Configure SQLite optimizations
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            # Optimize for performance
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            # Test if FTS5 is available
            cursor.execute("PRAGMA compile_options")
            compile_options = cursor.fetchall()
            fts5_available = any("FTS5" in str(option[0]) for option in compile_options)
            if not fts5_available:
                logger.warning("FTS5 extension not available in this SQLite build")
            cursor.close()

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
        self._create_fts5_search_tables()
        logger.info(f"Database tables created/verified at {self.db_path}")

    def _create_fts5_search_tables(self):
        """Create FTS5 search tables and triggers."""
        with self.get_session() as session:
            try:
                # Create FTS5 virtual table for Q&A search
                session.execute(text("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS qa_search USING fts5(
                        question, answer, context_used,
                        session_id UNINDEXED,
                        timestamp UNINDEXED,
                        content='qa_exchanges',
                        content_rowid='rowid'
                    )
                """))

                # Create triggers to keep FTS5 in sync with qa_exchanges

                # INSERT trigger
                session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS qa_exchanges_ai AFTER INSERT ON qa_exchanges BEGIN
                        INSERT INTO qa_search(rowid, question, answer, context_used, session_id, timestamp)
                        VALUES (new.rowid, new.question, new.answer, new.context_used, new.session_id, new.timestamp);
                    END
                """))

                # DELETE trigger
                session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS qa_exchanges_ad AFTER DELETE ON qa_exchanges BEGIN
                        INSERT INTO qa_search(qa_search, rowid, question, answer, context_used, session_id, timestamp)
                        VALUES('delete', old.rowid, old.question, old.answer, old.context_used, old.session_id, old.timestamp);
                    END
                """))

                # UPDATE trigger
                session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS qa_exchanges_au AFTER UPDATE ON qa_exchanges BEGIN
                        INSERT INTO qa_search(qa_search, rowid, question, answer, context_used, session_id, timestamp)
                        VALUES('delete', old.rowid, old.question, old.answer, old.context_used, old.session_id, old.timestamp);
                        INSERT INTO qa_search(rowid, question, answer, context_used, session_id, timestamp)
                        VALUES (new.rowid, new.question, new.answer, new.context_used, new.session_id, new.timestamp);
                    END
                """))

                # Create ranking view for BM25 + time decay
                session.execute(text("""
                    CREATE VIEW IF NOT EXISTS qa_search_ranked AS
                    SELECT
                        qa_exchanges.rowid,
                        qa_exchanges.exchange_id,
                        qa_exchanges.session_id,
                        qa_exchanges.question,
                        qa_exchanges.answer,
                        qa_exchanges.context_used,
                        qa_exchanges.timestamp,
                        qa_exchanges.confidence_score,
                        qa_exchanges.is_bookmarked,
                        sessions.document_display_name,
                        sessions.session_tags_json,
                        -- Time decay factor (newer = higher score)
                        (julianday('now') - julianday(qa_exchanges.timestamp)) / 365.0 as days_old,
                        CASE
                            WHEN (julianday('now') - julianday(qa_exchanges.timestamp)) / 365.0 < 0.1 THEN 1.0  -- Last month
                            WHEN (julianday('now') - julianday(qa_exchanges.timestamp)) / 365.0 < 0.25 THEN 0.8  -- Last 3 months
                            WHEN (julianday('now') - julianday(qa_exchanges.timestamp)) / 365.0 < 1.0 THEN 0.6   -- Last year
                            ELSE 0.4  -- Older
                        END as time_decay_factor
                    FROM qa_exchanges
                    JOIN sessions ON qa_exchanges.session_id = sessions.session_id
                """))

                session.commit()
                logger.info("FTS5 search tables and triggers created successfully")

            except Exception as e:
                session.rollback()
                logger.error(f"Failed to create FTS5 search tables: {e}")
                raise

    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()

    def health_check(self) -> bool:
        """Check if database is accessible."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get or create the global database manager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.create_tables()
    return _db_manager

def get_db_session():
    """Get a database session (for dependency injection)."""
    return get_database_manager().get_session()