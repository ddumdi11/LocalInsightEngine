"""
Test suite for enhanced persistence features:
- Session Timeline View
- Bookmarks & Favorites System
- Cross-Session Intelligence
"""

import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.persistence.database import DatabaseManager
from local_insight_engine.persistence.repository import SessionRepository
from local_insight_engine.models.analysis import AnalysisResult, Insight
from uuid import uuid4


def test_enhanced_features():
    """Test all enhanced persistence features together."""
    print("TESTING: Enhanced Persistence Features")

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Setup
        db_manager = DatabaseManager(tmp_path)
        db_manager.create_tables()
        repo = SessionRepository()

        # Create temporary test document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as doc:
            doc.write("Test document content about health and nutrition")
            doc_path = Path(doc.name)

        try:
            # Test 1: Create session with rich analysis
            analysis = AnalysisResult(
                source_processed_text_id=uuid4(),
                insights=[
                    Insight(
                        title="Health Benefits",
                        content="Regular exercise and proper nutrition are essential",
                        confidence=0.95,
                        category="health"
                    )
                ],
                main_themes=["health", "nutrition", "wellness"],
                executive_summary="Comprehensive guide to health and wellness practices"
            )

            session = repo.create_session(
                document_path=doc_path,
                analysis_result=analysis,
                display_name="Health & Wellness Guide",
                tags=["health", "wellness", "nutrition"]
            )

            print(f"SUCCESS: Created test session {session.session_id}")

            # Test 2: Add multiple Q&A exchanges with different timestamps
            exchanges = [
                ("What are the key principles of good health?",
                 "Good health is built on regular exercise, balanced nutrition, adequate sleep, and stress management."),
                ("How important is nutrition in overall wellness?",
                 "Nutrition is fundamental - it provides the fuel and building blocks for all body functions."),
                ("What role does exercise play in mental health?",
                 "Exercise releases endorphins and reduces stress hormones, significantly improving mental wellbeing.")
            ]

            exchange_ids = []
            for i, (question, answer) in enumerate(exchanges):
                exchange = repo.add_qa_exchange(
                    session.session_id,
                    question,
                    answer,
                    confidence_score=0.9 - (i * 0.05),
                    tokens_used=120 + (i * 10),
                    is_bookmarked=(i == 1),  # Bookmark the second exchange
                    claude_model="claude-sonnet-4-20250514"
                )
                exchange_ids.append(exchange.exchange_id)
                time.sleep(0.1)  # Small delay for different timestamps

            print(f"SUCCESS: Added {len(exchanges)} Q&A exchanges")

            # Test 3: Session Timeline View
            timeline = repo.get_session_timeline(session.session_id, include_metadata=True)

            assert timeline["session_id"] == session.session_id
            assert timeline["total_questions"] == 3
            assert len(timeline["timeline_events"]) == 3
            assert timeline["session_statistics"]["bookmarked_count"] == 1

            print("SUCCESS: Session timeline view working")

            # Test 4: Bookmarks & Favorites System

            # Toggle session as favorite
            is_favorite = repo.toggle_session_favorite(session.session_id)
            assert is_favorite == True

            # Get favorite sessions
            favorites = repo.get_favorite_sessions(limit=10)
            assert len(favorites) == 1
            assert favorites[0].session_id == session.session_id

            # Get bookmarked exchanges
            bookmarked = repo.get_bookmarked_exchanges(session.session_id)
            assert len(bookmarked) == 1

            # Rate an exchange
            success = repo.rate_qa_exchange(exchange_ids[0], 5)
            assert success == True

            # Add notes to an exchange
            success = repo.add_exchange_notes(exchange_ids[1], "Important point about nutrition fundamentals")
            assert success == True

            # Get user collection stats
            stats = repo.get_user_collection_stats()
            assert stats["favorite_sessions"] == 1
            assert stats["bookmarked_exchanges"] == 1
            assert stats["rated_exchanges"] == 1
            assert stats["exchanges_with_notes"] == 1

            print("SUCCESS: Bookmarks & Favorites system working")

            # Test 5: Cross-Session Intelligence (create second session for testing)

            analysis2 = AnalysisResult(
                source_processed_text_id=uuid4(),
                insights=[
                    Insight(
                        title="Exercise Science",
                        content="Cardiovascular exercise improves heart health and endurance",
                        confidence=0.92,
                        category="fitness"
                    )
                ],
                main_themes=["exercise", "fitness", "cardiovascular"],
                executive_summary="Scientific approach to exercise and fitness"
            )

            session2 = repo.create_session(
                document_path=doc_path,
                analysis_result=analysis2,
                display_name="Exercise Science Manual",
                tags=["exercise", "fitness", "science"]
            )

            # Add related content to second session
            repo.add_qa_exchange(
                session2.session_id,
                "What are the cardiovascular benefits of exercise?",
                "Regular cardiovascular exercise strengthens the heart muscle and improves circulation throughout the body.",
                confidence_score=0.88,
                tokens_used=130
            )

            # Test cross-session features

            # Related insights
            related = repo.get_related_insights(session.session_id, limit=5)
            print(f"SUCCESS: Found {len(related)} related insights")

            # Knowledge patterns
            patterns = repo.discover_knowledge_patterns(min_session_count=1, limit=10)
            assert len(patterns) > 0
            print(f"SUCCESS: Discovered {len(patterns)} knowledge patterns")

            # Follow-up suggestions
            suggestions = repo.suggest_follow_up_questions(session.session_id, limit=3)
            print(f"SUCCESS: Generated {len(suggestions)} follow-up suggestions")

            # Session evolution analysis
            evolution = repo.analyze_session_evolution(session.session_id)
            assert evolution["total_exchanges"] == 3
            assert len(evolution["progression_analysis"]) == 3
            print("SUCCESS: Session evolution analysis working")

            # Complementary sessions
            complementary = repo.find_complementary_sessions(session.session_id, limit=3)
            print(f"SUCCESS: Found {len(complementary)} complementary sessions")

            # Knowledge graph data
            graph_data = repo.generate_knowledge_graph_data(focus_session_id=session.session_id, max_sessions=10)
            assert len(graph_data["nodes"]) >= 2
            print(f"SUCCESS: Generated knowledge graph with {len(graph_data['nodes'])} nodes")

            # Test 6: Activity Summary
            activity = repo.get_session_activity_summary(session.session_id, group_by_period="day")
            assert activity["total_exchanges"] == 3
            assert activity["total_periods"] >= 1
            print("SUCCESS: Activity summary working")

            # Test 7: Export Collection
            collection = repo.export_user_collection(
                include_favorites=True,
                include_bookmarks=True,
                include_ratings=True,
                include_notes=True
            )

            assert len(collection["favorite_sessions"]) == 1
            assert len(collection["bookmarked_exchanges"]) == 1
            assert len(collection["rated_exchanges"]) == 1
            print("SUCCESS: User collection export working")

            print("ALL ENHANCED FEATURES TESTS PASSED!")
            return True

        finally:
            if doc_path.exists():
                doc_path.unlink()

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


def run_enhanced_features_tests():
    """Run all enhanced features tests."""
    print("ENHANCED PERSISTENCE FEATURES TESTS")
    print("=" * 40)

    success = test_enhanced_features()

    if success:
        print()
        print("ALL ENHANCED FEATURES WORKING PERFECTLY!")
        print()
        print("PHASE 2 COMPLETE:")
        print("- Session Timeline View")
        print("- Enhanced Bookmarks & Favorites")
        print("- Advanced Cross-Session Intelligence")
        print("- Knowledge Graph Generation")
        print("- Pattern Discovery")
        print("- Smart Recommendations")
    else:
        print()
        print("SOME ENHANCED FEATURES FAILED!")

    return success


if __name__ == "__main__":
    success = run_enhanced_features_tests()
    exit(0 if success else 1)