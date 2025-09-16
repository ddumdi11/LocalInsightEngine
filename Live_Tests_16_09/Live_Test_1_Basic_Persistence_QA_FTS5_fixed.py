"""
Live Test 1: Basic Persistence + Q&A Exchanges + FTS5 Search - FIXED VERSION
Tests session creation, Q&A exchanges, and search functionality with correct database initialization.
"""

from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path.cwd().parent / "src"))

# Import database and repository classes
from local_insight_engine.persistence.database import DatabaseManager
from local_insight_engine.persistence.repository import SessionRepository
from local_insight_engine.models.analysis import AnalysisResult, Insight
from local_insight_engine.persistence.models import QAExchange
from uuid import uuid4

# --- Expliziter Pfad für die Testdatenbank ---
test_db_filename = "live_test_db.db"
test_db_path = Path.cwd() / test_db_filename

# Löschen der Testdatenbank vor dem Start
if test_db_path.exists():
    print(f"Lösche bestehende Testdatenbankdatei: {test_db_path}")
    os.remove(test_db_path)
    print("Testdatenbank gelöscht. Starte mit sauberem Zustand.")
else:
    print("Keine bestehende Testdatenbankdatei gefunden. Erstelle neue Testdatenbank.")
print()

# KORREKTE Initialisierung mit benutzerdefinierter Datenbank
# 1. Eigenen DatabaseManager erstellen
db_manager = DatabaseManager(db_path=test_db_path)
db_manager.create_tables()

# 2. Session Repository mit einer expliziten Database Session erstellen
db_session = db_manager.get_session()
repo = SessionRepository(db_session=db_session)

# Test 1: Session erstellen
print("1. TESTING SESSION CREATION...")

test_doc = Path("german_sample.txt")

# Sicherstellen, dass german_sample.txt existiert
if not test_doc.exists():
    print(f"Erstelle temporäre Dummy-Datei: {test_doc}")
    with open(test_doc, "w", encoding="utf-8") as f:
        f.write("Dies ist ein Beispieltext für den Test der LocalInsightEngine. Es behandelt verschiedene Themen rund um Gesundheit und Ernährung, mit besonderem Fokus auf Vitamine wie B3, B12, Vitamin C und Vitamin D.")

# Test-Analysis Result
analysis = AnalysisResult(
    source_processed_text_id=uuid4(),
    insights=[
        Insight(
            title="Test Insight",
            content="This is a test insight about the document",
            confidence=0.9,
            category="test"
        )
    ],
    executive_summary="Test document analysis"
)

# Session erstellen
session = repo.create_session(
    document_path=test_doc,
    analysis_result=analysis,
    display_name="Live Test Document",
    tags=["test", "live", "demo"]
)

print(f"SUCCESS: Session created: {session.session_id}")
print(f"Document: {session.document_display_name}")
print(f"Tags: {session.session_tags}")
print()

# Test 2: Q&A Exchanges hinzufügen
print("2. TESTING Q&A EXCHANGES...")

# Exchange 1 über Repository hinzufügen
exchange1 = repo.add_qa_exchange(
    session_id=session.session_id,
    question="Was ist der Hauptinhalt dieses Dokuments?",
    answer="Das Dokument behandelt verschiedene Themen rund um Gesundheit und Ernährung, mit besonderem Fokus auf Vitamine.",
    confidence_score=0.85,
    tokens_used=150,
    claude_model="claude-sonnet-4-20250514"
)

# Exchange 2 über Repository hinzufügen (mit Bookmark)
exchange2 = repo.add_qa_exchange(
    session_id=session.session_id,
    question="Welche Vitamine werden erwähnt?",
    answer="Hauptsächlich werden B-Vitamine wie B3 (Niacin) und B12 erwähnt, sowie Vitamin C und D.",
    confidence_score=0.92,
    tokens_used=120,
    is_bookmarked=True,
    claude_model="claude-sonnet-4-20250514"
)

print(f"SUCCESS: Exchange 1: {exchange1.exchange_id}")
print(f"SUCCESS: Exchange 2: {exchange2.exchange_id}")
print(f"Bookmarked: {exchange2.is_bookmarked}")
print()

# Test 3: FTS5 Search
print("3. TESTING FTS5 SEARCH...")

try:
    # Einfache Suche
    search_results = repo.search_qa_content("Vitamin", min_score=0.0)
    print(f"SUCCESS: Search 'Vitamin': {len(search_results)} results")

    for i, result in enumerate(search_results):
        print(f"  Result {i+1}:")
        print(f"    Question: {result.question[:60]}...")
        print(f"    Answer: {result.answer[:60]}...")
        print(f"    Score: {result.final_score:.3f}")
        print(f"    Document: {result.document_display_name}")
        print()

    # Komplexere Suche
    search_results2 = repo.search_qa_content("Gesundheit Ernährung", min_score=0.0)
    print(f"SUCCESS: Search 'Gesundheit Ernährung': {len(search_results2)} results")

    # Bookmark-only Suche
    bookmark_results = repo.search_qa_content("Vitamin", bookmarked_only=True, min_score=0.0)
    print(f"SUCCESS: Bookmarked 'Vitamin': {len(bookmark_results)} results")

    # Ähnliche Fragen finden
    similar_questions = repo.find_similar_questions("Was sind die wichtigsten Vitamine?", limit=3)
    print(f"SUCCESS: Similar questions found: {len(similar_questions)} results")
    for result in similar_questions:
        print(f"  Similar: {result.question[:60]}...")

except Exception as e:
    print(f"SEARCH ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Repository Statistiken
print("4. TESTING REPOSITORY STATISTICS...")
try:
    stats = repo.get_session_statistics()
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Total Q&A Exchanges: {stats['total_qa_exchanges']}")
    print(f"Favorite Sessions: {stats['favorite_sessions']}")
    print(f"Latest Activity: {stats['latest_activity']}")

    # Collection Stats
    collection_stats = repo.get_user_collection_stats()
    print(f"Bookmarked Exchanges: {collection_stats['bookmarked_exchanges']}")

except Exception as e:
    print(f"STATS ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# Cleanup
try:
    db_session.close()
    print("Database session closed successfully.")
except Exception as e:
    print(f"Cleanup warning: {e}")

print()
print("=== LIVE TEST 1 FIXED COMPLETED ===")