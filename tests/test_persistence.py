"""
Test suite for persistence layer.
Tests SQLAlchemy models and repository operations.
"""

import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.persistence.database import DatabaseManager, get_database_manager
from local_insight_engine.persistence.models import PersistentQASession, QAExchange
from local_insight_engine.persistence.repository import SessionRepository
from local_insight_engine.models.analysis import AnalysisResult


def test_database_setup():
    """Test database initialization and table creation."""
    print("TESTING: Database setup...")

    # Use temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Create database manager
        db_manager = DatabaseManager(tmp_path)
        db_manager.create_tables()

        # Test health check
        assert db_manager.health_check(), "Database health check failed"

        print("SUCCESS: Database setup successful")

    finally:
        # Cleanup - close engine first
        try:
            if 'db_manager' in locals():
                db_manager.engine.dispose()
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors


def test_model_creation():
    """Test creating and storing models."""
    print("TESTING: Model creation...")

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Setup
        db_manager = DatabaseManager(tmp_path)
        db_manager.create_tables()

        # Create test analysis result with correct structure
        from local_insight_engine.models.analysis import Insight
        from uuid import uuid4

        test_insights = [
            Insight(
                title="Test Insight 1",
                content="This is a test insight about vitamins",
                confidence=0.85,
                category="pattern"
            ),
            Insight(
                title="Test Insight 2",
                content="Another test insight",
                confidence=0.92,
                category="synthesis"
            )
        ]

        analysis_result = AnalysisResult(
            source_processed_text_id=uuid4(),
            insights=test_insights,
            main_themes=["nutrition", "health"],
            executive_summary="Test document about vitamins and health"
        )

        # Create session using raw SQLAlchemy
        with db_manager.get_session() as session:
            qa_session = PersistentQASession(
                document_path_hash="test_path_hash_123",
                pepper_id="test_pepper",
                document_hash="test_doc_hash_456",
                document_display_name="test_document.pdf",
                neutralized_context="This is neutralized content about vitamins",
                analysis_result=analysis_result,
                session_tags=["health", "nutrition", "test"]
            )

            session.add(qa_session)
            session.commit()
            session.refresh(qa_session)

            # Verify session was created
            assert qa_session.session_id is not None
            assert qa_session.total_questions == 0
            assert qa_session.session_tags == ["health", "nutrition", "test"]
            assert qa_session.analysis_result.executive_summary == "Test document about vitamins and health"
            assert len(qa_session.analysis_result.insights) == 2

            print(f"SUCCESS: Session created with ID: {qa_session.session_id}")

            # Add Q&A exchange
            exchange = qa_session.add_qa_exchange(
                question="What vitamins are mentioned?",
                answer="The document mentions B3, B12, C, and D vitamins",
                confidence_score=0.9,
                tokens_used=150,
                claude_model="claude-sonnet-4-20250514"
            )

            session.commit()
            session.refresh(exchange)

            # Verify exchange
            assert exchange.exchange_id is not None
            assert exchange.question == "What vitamins are mentioned?"
            assert exchange.confidence_score == 0.9
            assert qa_session.total_questions == 1

            print(f"SUCCESS: Q&A exchange created with ID: {exchange.exchange_id}")

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_repository_operations():
    """Test repository CRUD operations."""
    print("TESTING: Repository operations...")

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Setup
        db_manager = DatabaseManager(tmp_path)
        db_manager.create_tables()

        # Create test document (temporary file)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as doc:
            doc.write("This is a test document about vitamins and nutrition.")
            doc_path = Path(doc.name)

        try:
            # Create repository bound to the temporary DB session
            with db_manager.get_session() as db_sess:
                repo = SessionRepository(db_session=db_sess)

                # Test analysis result with correct structure
                test_insights = [
                    Insight(
                        title="Vitamin Analysis",
                        content="Vitamin analysis complete - B vitamins are important",
                        confidence=0.92,
                        category="analysis"
                    )
                ]

                analysis_result = AnalysisResult(
                    source_processed_text_id=uuid4(),
                    insights=test_insights,
                    main_themes=["vitamins", "nutrition"],
                    executive_summary="Document about vitamin benefits"
                )

                # Test create session (inside with-block to keep session open)
                session = repo.create_session(
                    document_path=doc_path,
                    analysis_result=analysis_result,
                    neutralized_context="Safe neutralized content",
                    display_name="Test Nutrition Document",
                    tags=["nutrition", "vitamins", "health"]
                )

                assert session is not None
                assert session.document_display_name == "Test Nutrition Document"
                assert len(session.session_tags) == 3
                print(f"SUCCESS: Repository created session: {session.session_id}")

                # Test get by ID (inside with-block to keep session open)
                retrieved_session = repo.get_session_by_id(session.session_id)
                assert retrieved_session is not None
                assert retrieved_session.session_id == session.session_id
                print("SUCCESS: Session retrieved by ID")

                # Test add Q&A exchange (inside with-block to keep session open)
                exchange = repo.add_qa_exchange(
                    session_id=session.session_id,
                question="What are the health benefits?",
                answer="Vitamins support various bodily functions...",
                confidence_score=0.88,
                tokens_used=200,
                is_bookmarked=True
                )

                assert exchange is not None
                assert exchange.is_bookmarked == True
                print(f"SUCCESS: Q&A exchange added: {exchange.exchange_id}")

                # Test list sessions (inside with-block to keep session open)
                sessions = repo.list_sessions(limit=10)
                assert len(sessions) >= 1
                assert sessions[0].session_id == session.session_id
                print(f"SUCCESS: Listed sessions: {len(sessions)} found")

                # Test update session (inside with-block to keep session open)
                updated = repo.update_session(
                    session.session_id,
                    is_favorite=True,
                    auto_generated_summary="Updated summary"
                )
                assert updated.is_favorite == True
                assert updated.auto_generated_summary == "Updated summary"
                print("SUCCESS: Session updated successfully")

                # Test search (inside with-block to keep session open)
                found = repo.search_sessions("nutrition")
                assert len(found) >= 1
                print(f"SUCCESS: Search found {len(found)} sessions")

                # Test statistics (inside with-block to keep session open)
                stats = repo.get_session_statistics()
                assert stats["total_sessions"] >= 1
                assert stats["total_qa_exchanges"] >= 1
                print(f"SUCCESS: Statistics: {stats}")

        finally:
            if doc_path.exists():
                doc_path.unlink()

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def run_all_tests():
    """Run all persistence tests."""
    print("PERSISTENCE LAYER TESTS")
    print("=" * 40)

    try:
        test_database_setup()
        print()
        test_model_creation()
        print()
        test_repository_operations()
        print()
        print("ALL PERSISTENCE TESTS PASSED!")
        return True

    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)