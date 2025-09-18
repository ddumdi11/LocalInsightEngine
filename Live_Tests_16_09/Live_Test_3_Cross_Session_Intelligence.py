"""
Live Test 3: Cross-Session Intelligence
Tests advanced features like timeline, patterns, and cross-session analysis.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd().parent / "src"))

from local_insight_engine.persistence.repository import SessionRepository
from local_insight_engine.persistence.models import QAExchange
from local_insight_engine.models.analysis import AnalysisResult, Insight
from uuid import uuid4

print("=== LIVE TEST 3: CROSS-SESSION INTELLIGENCE ===")
print()

repo = SessionRepository()

# Test 1: Session Timeline View
print("1. TESTING SESSION TIMELINE...")
sessions = repo.list_sessions(limit=1, order_by="created_at", ascending=False)
if not sessions:
    print("ERROR: No sessions found! Run Live_Test_1.py first!")
    exit(1)

session = sessions[0]
timeline = repo.get_session_timeline(session.session_id, include_metadata=True)

print(f"SUCCESS: Timeline for '{timeline['document_display_name']}'")
print(f"  - Session ID: {timeline['session_id']}")
print(f"  - Total questions: {timeline['total_questions']}")
print(f"  - Is favorite: {timeline['is_favorite']}")
print(f"  - Created: {timeline['created_at']}")

if 'session_statistics' in timeline:
    stats = timeline['session_statistics']
    print("  Session Statistics:")
    print(f"    - Total tokens used: {stats['total_tokens_used']}")
    print(f"    - Average confidence: {stats['avg_confidence']:.2f}")
    print(f"    - Bookmarked exchanges: {stats['bookmarked_count']}")

print(f"  Timeline Events: {len(timeline['timeline_events'])}")
for i, event in enumerate(timeline['timeline_events'][:3]):  # Show first 3
    print(f"    Event {event['sequence_number']}: {event['question'][:40]}...")
    if event['time_since_previous']:
        print(f"      Time since previous: {event['time_since_previous']}")
    print(f"      Confidence: {event['confidence_score']}")
print()

# Test 2: Create a second session for cross-session testing
print("2. CREATING SECOND SESSION FOR CROSS-SESSION TESTING...")

analysis2 = AnalysisResult(
    source_processed_text_id=uuid4(),
    insights=[
        Insight(
            title="Exercise Benefits",
            content="Regular physical activity improves cardiovascular health",
            confidence=0.88,
            category="fitness"
        )
    ],
    main_themes=["exercise", "fitness", "health"],
    executive_summary="Exercise and fitness guide"
)

try:
    # Use different file to avoid unique constraint
    test_doc2 = Path("english_sample.txt")  # Different file
    session2 = repo.create_session(
        document_path=test_doc2,
        analysis_result=analysis2,
        display_name="Exercise & Fitness Guide",
        tags=["exercise", "fitness", "health"]
    )

    # Add related content
    with repo._get_session() as db_session:
        exercise_exchange = QAExchange(
            session_id=session2.session_id,
            question="What are the benefits of regular exercise?",
            answer="Regular exercise improves cardiovascular health, strengthens muscles, and enhances mental wellbeing through endorphin release.",
            confidence_score=0.89,
            tokens_used=140
        )
        db_session.add(exercise_exchange)
        db_session.commit()

    print(f"SUCCESS: Second session created: {session2.session_id}")
    print(f"Document: {session2.document_display_name}")

except Exception as e:
    print(f"NOTE: Could not create second session (probably duplicate): {e}")
    # Use existing session for cross-session tests
    all_sessions = repo.list_sessions(limit=2)
    session2 = all_sessions[1] if len(all_sessions) > 1 else all_sessions[0]

print()

# Test 3: Knowledge Patterns Discovery
print("3. TESTING KNOWLEDGE PATTERNS DISCOVERY...")
try:
    patterns = repo.discover_knowledge_patterns(min_session_count=1, limit=5)
    print(f"SUCCESS: Found {len(patterns)} knowledge patterns")

    for i, pattern in enumerate(patterns[:3]):  # Show first 3
        print(f"  Pattern {i+1}: '{pattern['pattern']}'")
        print(f"    - Appears in {pattern['session_count']} sessions")
        print(f"    - Total mentions: {pattern['total_mentions']}")
        print(f"    - Example sessions: {pattern['example_sessions']}")
        print(f"    - Relevance score: {pattern['relevance_score']:.1f}")
        print()

except Exception as e:
    print(f"PATTERN DISCOVERY ERROR: {e}")

# Test 4: Related Insights
print("4. TESTING RELATED INSIGHTS...")
try:
    related = repo.get_related_insights(session.session_id, limit=5)
    print(f"SUCCESS: Found {len(related)} related insights")

    for insight in related[:2]:  # Show first 2
        print(f"  - From: {insight.document_display_name}")
        print(f"    Question: {insight.question[:50]}...")
        print(f"    Similarity score: {insight.final_score:.3f}")
        print()

except Exception as e:
    print(f"RELATED INSIGHTS ERROR: {e}")

# Test 5: Follow-up Question Suggestions
print("5. TESTING FOLLOW-UP SUGGESTIONS...")
try:
    suggestions = repo.suggest_follow_up_questions(session.session_id, limit=3)
    print(f"SUCCESS: Generated {len(suggestions)} follow-up suggestions")

    for i, suggestion in enumerate(suggestions):
        print(f"  Suggestion {i+1}: {suggestion['suggested_question']}")
        print(f"    Reasoning: {suggestion['reasoning']}")
        print(f"    Confidence: {suggestion['confidence']}")
        print()

except Exception as e:
    print(f"SUGGESTIONS ERROR: {e}")

# Test 6: Session Evolution Analysis
print("6. TESTING SESSION EVOLUTION...")
try:
    evolution = repo.analyze_session_evolution(session.session_id)
    print(f"SUCCESS: Session evolution analysis")
    print(f"  - Total exchanges: {evolution['total_exchanges']}")
    print(f"  - Time span: {evolution['time_span']}")
    print(f"  - Progression events: {len(evolution['progression_analysis'])}")

    for event in evolution['progression_analysis'][:2]:  # Show first 2
        print(f"    Event {event['exchange_number']}: {event['evolution_type']}")
        print(f"      New topics: {event['new_topics']}")
        if event.get('time_since_previous'):
            print(f"      Time since previous: {event['time_since_previous']}")
        print()

except Exception as e:
    print(f"EVOLUTION ANALYSIS ERROR: {e}")

print("=== LIVE TEST 3 COMPLETED ===")