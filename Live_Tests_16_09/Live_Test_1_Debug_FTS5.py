"""
Live Test 1 Debug: FTS5 Search Troubleshooting
Tests why FTS5 search returns 0 results.
"""

from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path.cwd().parent / "src"))

from local_insight_engine.persistence.database import DatabaseManager
from local_insight_engine.persistence.repository import SessionRepository
from local_insight_engine.models.analysis import AnalysisResult, Insight
from local_insight_engine.persistence.models import QAExchange
from uuid import uuid4
from sqlalchemy import text

# --- Use same test database ---
test_db_path = Path.cwd() / "live_test_db.db"

print("=== FTS5 DEBUG SESSION ===")
print(f"Using database: {test_db_path}")
print()

# Re-use existing database
db_manager = DatabaseManager(db_path=test_db_path)
db_manager.create_tables()  # This should be idempotent

db_session = db_manager.get_session()
repo = SessionRepository(db_session=db_session)

# Test 1: Check if qa_exchanges table has data
print("1. CHECKING qa_exchanges TABLE...")
try:
    result = db_session.execute(text("SELECT COUNT(*) FROM qa_exchanges"))
    count = result.scalar()
    print(f"qa_exchanges has {count} records")

    if count > 0:
        result = db_session.execute(text("SELECT exchange_id, question, answer FROM qa_exchanges LIMIT 3"))
        for row in result:
            print(f"  ID: {row[0]}")
            print(f"  Q: {row[1][:60]}...")
            print(f"  A: {row[2][:60]}...")
            print()
except Exception as e:
    print(f"ERROR checking qa_exchanges: {e}")

print()

# Test 2: Check if qa_search FTS5 table exists and has data
print("2. CHECKING qa_search FTS5 TABLE...")
try:
    result = db_session.execute(text("SELECT COUNT(*) FROM qa_search"))
    count = result.scalar()
    print(f"qa_search FTS5 table has {count} records")

    if count > 0:
        result = db_session.execute(text("SELECT rowid, question, answer FROM qa_search LIMIT 3"))
        for row in result:
            print(f"  ROWID: {row[0]}")
            print(f"  Q: {row[1][:60]}...")
            print(f"  A: {row[2][:60]}...")
            print()
    else:
        print("❌ qa_search table is EMPTY - triggers may not be working!")

        # Try to manually populate
        print("Attempting to manually sync FTS5 table...")
        db_session.execute(text("""
            INSERT INTO qa_search(rowid, question, answer, context_used, session_id, timestamp)
            SELECT rowid, question, answer, context_used, session_id, timestamp
            FROM qa_exchanges
        """))
        db_session.commit()

        result = db_session.execute(text("SELECT COUNT(*) FROM qa_search"))
        count = result.scalar()
        print(f"After manual sync: qa_search has {count} records")

except Exception as e:
    print(f"ERROR checking qa_search: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Test FTS5 search directly
print("3. TESTING FTS5 SEARCH DIRECTLY...")
try:
    # Simple FTS5 query
    result = db_session.execute(text("SELECT * FROM qa_search WHERE qa_search MATCH 'Vitamin'"))
    rows = result.fetchall()
    print(f"Direct FTS5 search for 'Vitamin': {len(rows)} results")

    for row in rows:
        print(f"  Found: {row}")

    # Try a broader search
    result = db_session.execute(text("SELECT * FROM qa_search WHERE qa_search MATCH 'Gesundheit'"))
    rows = result.fetchall()
    print(f"Direct FTS5 search for 'Gesundheit': {len(rows)} results")

except Exception as e:
    print(f"ERROR with direct FTS5 search: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Test full search query
print("4. TESTING FULL REPOSITORY SEARCH...")
try:
    search_results = repo.search_qa_content("Vitamin", min_score=0.0)
    print(f"Repository search for 'Vitamin': {len(search_results)} results")

    for result in search_results:
        print(f"  Q: {result.question[:50]}...")
        print(f"  A: {result.answer[:50]}...")
        print(f"  Score: {result.final_score}")

except Exception as e:
    print(f"ERROR with repository search: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Check table schemas
print("5. CHECKING TABLE SCHEMAS...")
try:
    result = db_session.execute(text("PRAGMA table_info(qa_exchanges)"))
    columns = result.fetchall()
    print("qa_exchanges columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    print()

    result = db_session.execute(text("PRAGMA table_info(qa_search)"))
    columns = result.fetchall()
    print("qa_search columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

except Exception as e:
    print(f"ERROR checking schemas: {e}")

print()

# Cleanup
try:
    db_session.close()
    print("Database session closed successfully.")
except Exception as e:
    print(f"Cleanup warning: {e}")

print()
print("=== FTS5 DEBUG COMPLETED ===")