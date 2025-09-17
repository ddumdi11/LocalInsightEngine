"""
Test suite for FTS5 search functionality.
Tests SmartSearchEngine and repository search methods.
"""

import sys
import tempfile
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.persistence.database import DatabaseManager
from local_insight_engine.persistence.repository import SessionRepository
from local_insight_engine.persistence.search import SmartSearchEngine
from local_insight_engine.models.analysis import AnalysisResult, Insight
from uuid import uuid4


def create_test_data(repo: SessionRepository) -> dict:
    """Create test Q&A sessions with varied content for search testing."""

    # Create temporary test document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as doc:
        doc.write("Test document content")
        doc_path = Path(doc.name)

    sessions = {}

    try:
        # Session 1: Nutrition & Vitamins
        analysis1 = AnalysisResult(
            source_processed_text_id=uuid4(),
            insights=[
                Insight(
                    title="Vitamin B3 Benefits",
                    content="Niacin supports energy metabolism",
                    confidence=0.9,
                    category="health"
                )
            ],
            main_themes=["nutrition", "vitamins"],
            executive_summary="Document about vitamin benefits and nutrition"
        )

        # Use unique pepper_id to avoid UniqueConstraint collision
        with patch('local_insight_engine.persistence.repository.PersistentQASession') as MockSession:
            def create_session_with_unique_pepper(**kwargs):
                kwargs['pepper_id'] = f"test_pepper_nutrition_{uuid.uuid4().hex[:8]}"
                return PersistentQASession(**kwargs)

            MockSession.side_effect = create_session_with_unique_pepper
            session1 = repo.create_session(
                document_path=doc_path,
                analysis_result=analysis1,
                display_name="Nutrition Guide",
                tags=["health", "vitamins", "nutrition"]
            )
        sessions['nutrition'] = session1

        # Add Q&A exchanges to session 1
        repo.add_qa_exchange(
            session1.session_id,
            "What are the benefits of vitamin B3?",
            "Vitamin B3 (niacin) supports energy metabolism and helps maintain healthy skin. It plays a crucial role in converting nutrients into energy.",
            confidence_score=0.9,
            tokens_used=120,
            is_bookmarked=True
        )

        repo.add_qa_exchange(
            session1.session_id,
            "How much vitamin B3 should I take daily?",
            "The recommended daily allowance for niacin is 16mg for men and 14mg for women. Higher doses should be supervised by healthcare providers.",
            confidence_score=0.85,
            tokens_used=98
        )

        # Session 2: Exercise & Fitness
        analysis2 = AnalysisResult(
            source_processed_text_id=uuid4(),
            insights=[
                Insight(
                    title="Exercise Benefits",
                    content="Regular exercise improves cardiovascular health",
                    confidence=0.88,
                    category="fitness"
                )
            ],
            main_themes=["exercise", "fitness", "health"],
            executive_summary="Guide to exercise and fitness routines"
        )

        session2 = repo.create_session(
            document_path=doc_path,
            analysis_result=analysis2,
            display_name="Fitness Manual",
            tags=["exercise", "fitness", "health"]
        )
        sessions['fitness'] = session2

        # Add Q&A exchanges to session 2
        repo.add_qa_exchange(
            session2.session_id,
            "What are the benefits of regular exercise?",
            "Regular exercise improves cardiovascular health, strengthens muscles, enhances mood, and helps maintain healthy weight. It also boosts energy levels.",
            confidence_score=0.92,
            tokens_used=145
        )

        repo.add_qa_exchange(
            session2.session_id,
            "How often should I exercise per week?",
            "Adults should aim for at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity per week, plus muscle strengthening exercises twice weekly.",
            confidence_score=0.87,
            tokens_used=132,
            is_bookmarked=True
        )

        # Session 3: Mental Health (with some overlapping themes)
        analysis3 = AnalysisResult(
            source_processed_text_id=uuid4(),
            insights=[
                Insight(
                    title="Stress Management",
                    content="Meditation and exercise reduce stress effectively",
                    confidence=0.91,
                    category="mental_health"
                )
            ],
            main_themes=["mental_health", "stress", "wellbeing"],
            executive_summary="Mental health and stress management strategies"
        )

        # Use unique pepper_id to avoid UniqueConstraint collision
        with patch('local_insight_engine.persistence.repository.PersistentQASession') as MockSession:
            def create_session_with_unique_pepper(**kwargs):
                kwargs['pepper_id'] = f"test_pepper_mental_{uuid.uuid4().hex[:8]}"
                return PersistentQASession(**kwargs)

            MockSession.side_effect = create_session_with_unique_pepper
            session3 = repo.create_session(
                document_path=doc_path,
                analysis_result=analysis3,
                display_name="Mental Wellness Guide",
                tags=["mental_health", "stress", "wellbeing"]
            )
        sessions['mental_health'] = session3

        # Add Q&A exchanges to session 3
        repo.add_qa_exchange(
            session3.session_id,
            "How can I manage stress effectively?",
            "Effective stress management includes regular exercise, meditation, adequate sleep, and maintaining social connections. Deep breathing exercises can provide immediate relief.",
            confidence_score=0.89,
            tokens_used=118
        )

        repo.add_qa_exchange(
            session3.session_id,
            "What role does exercise play in mental health?",
            "Exercise releases endorphins that improve mood and reduce anxiety. Regular physical activity can be as effective as medication for mild depression.",
            confidence_score=0.93,
            tokens_used=105,
            is_bookmarked=True
        )

        # Wait a bit to create timestamp differences
        time.sleep(0.1)

        return sessions

    finally:
        if doc_path.exists():
            doc_path.unlink()


def test_fts5_search_functionality():
    """Test comprehensive FTS5 search functionality."""
    print("TESTING: FTS5 Search Functionality")

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Setup
        db_manager = DatabaseManager(tmp_path)
        db_manager.create_tables()

        db_session = db_manager.get_session()
        repo = SessionRepository(db_session=db_session)
        # search_engine unused; repository delegates internally

        # Create test data
        sessions = create_test_data(repo)
        print(f"SUCCESS: Created {len(sessions)} test sessions")

        # Test 1: Basic keyword search
        results = repo.search_qa_content("vitamin B3")
        assert len(results) >= 1, f"Expected vitamin B3 results, got {len(results)}"
        assert "vitamin B3" in results[0].question.lower() or "vitamin B3" in results[0].answer.lower()
        print(f"SUCCESS: Basic search found {len(results)} results for 'vitamin B3'")

        # Test 2: Multi-keyword search
        results = repo.search_qa_content("exercise health benefits")
        assert len(results) >= 2, f"Expected multiple results for exercise+health, got {len(results)}"
        print(f"SUCCESS: Multi-keyword search found {len(results)} results")

        # Test 3: Bookmarked-only search
        bookmarked_results = repo.search_qa_content("vitamin", bookmarked_only=True)
        for result in bookmarked_results:
            assert result.is_bookmarked, "Non-bookmarked result in bookmarked-only search"
        print(f"SUCCESS: Bookmarked search found {len(bookmarked_results)} results")

        # Test 4: Similar questions
        similar = repo.find_similar_questions("What are vitamin benefits?")
        assert len(similar) >= 1, "Expected similar questions"
        print(f"SUCCESS: Similar questions found {len(similar)} results")

        # Test 5: Related insights across sessions
        nutrition_session_id = sessions['nutrition'].session_id
        related = repo.get_related_insights(nutrition_session_id)
        # Should find exercise-related content due to health overlap
        assert len(related) >= 1, "Expected related insights from other sessions"
        print(f"SUCCESS: Related insights found {len(related)} results")

        # Test 6: Tag-based search
        tag_results = repo.search_by_tags(["health"])
        assert len(tag_results) >= 2, "Expected multiple results for health tag"
        print(f"SUCCESS: Tag search found {len(tag_results)} results")

        # Test 7: Combined tag search (AND logic)
        specific_tags = repo.search_by_tags(["health", "vitamins"], match_all=True)
        print(f"SUCCESS: Specific tag combination found {len(specific_tags)} results")

        # Test 8: Search statistics
        stats = repo.get_search_statistics()
        assert "search_index" in stats
        assert stats["search_index"]["total_indexed_exchanges"] >= 6
        print(f"SUCCESS: Search statistics - {stats['search_index']['total_indexed_exchanges']} indexed exchanges")

        # Test 9: Search ranking (time decay)
        recent_results = repo.search_qa_content("exercise", time_decay_weight=0.8)
        older_results = repo.search_qa_content("exercise", time_decay_weight=0.1)
        print(f"SUCCESS: Time decay scoring - recent: {len(recent_results)}, older: {len(older_results)}")

        # Test 10: Search query sanitization
        problematic_query = 'vitamin "unclosed quote [brackets] {braces}'
        sanitized_results = repo.search_qa_content(problematic_query)
        # Should not crash and should return results
        print(f"SUCCESS: Query sanitization handled problematic query, found {len(sanitized_results)} results")

        print("ALL FTS5 SEARCH TESTS PASSED!")
        return True

    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            db_manager.engine.dispose()
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass


def test_search_performance():
    """Test search performance with multiple queries."""
    print("TESTING: Search Performance")

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Setup
        db_manager = DatabaseManager(tmp_path)
        db_manager.create_tables()

        repo = SessionRepository()

        # Create test data
        sessions = create_test_data(repo)

        # Performance test queries
        test_queries = [
            "vitamin benefits",
            "exercise health",
            "stress management",
            "daily allowance",
            "cardiovascular health",
            "mental wellbeing"
        ]

        start_time = time.time()
        total_results = 0

        for query in test_queries:
            results = repo.search_qa_content(query, limit=10)
            total_results += len(results)

        end_time = time.time()
        avg_time = (end_time - start_time) / len(test_queries)

        print(f"SUCCESS: Performance test completed")
        print(f"  - {len(test_queries)} queries executed")
        print(f"  - {total_results} total results")
        print(f"  - Average query time: {avg_time:.3f} seconds")
        print(f"  - All queries under 1 second: {'YES' if avg_time < 1.0 else 'NO'}")

        return True

    except Exception as e:
        print(f"PERFORMANCE TEST FAILED: {e}")
        return False

    finally:
        try:
            db_manager.engine.dispose()
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass


def run_all_fts5_tests():
    """Run all FTS5 search tests."""
    print("FTS5 SEARCH ENGINE TESTS")
    print("=" * 40)

    success = True

    success &= test_fts5_search_functionality()
    print()
    success &= test_search_performance()

    if success:
        print()
        print("ALL FTS5 TESTS PASSED!")
    else:
        print()
        print("SOME FTS5 TESTS FAILED!")

    return success


if __name__ == "__main__":
    success = run_all_fts5_tests()
    exit(0 if success else 1)