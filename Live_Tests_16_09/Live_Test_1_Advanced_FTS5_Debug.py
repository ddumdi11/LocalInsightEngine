"""
Advanced FTS5 Debug: Test FTS5 ranking system
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd().parent / "src"))

from local_insight_engine.persistence.database import DatabaseManager
from sqlalchemy import text

test_db_path = Path.cwd() / "live_test_db.db"
db_manager = DatabaseManager(db_path=test_db_path)
db_session = db_manager.get_session()

print("=== ADVANCED FTS5 DEBUG ===")

# Test how FTS5 rank works
print("1. Testing FTS5 ranking system...")
try:
    # Test the rank column
    result = db_session.execute(text("""
        SELECT question, answer, rank, bm25(qa_search)
        FROM qa_search
        WHERE qa_search MATCH 'Vitamin'
    """))
    rows = result.fetchall()
    print(f"FTS5 rank test: {len(rows)} results")
    for row in rows:
        print(f"  Question: {row[0][:40]}...")
        print(f"  Rank: {row[2]}")
        print(f"  BM25: {row[3]}")
        print()

except Exception as e:
    print(f"FTS5 rank test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test the exact query from repository search
print("2. Testing repository-style query...")
try:
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
          AND qa_search.rank >= :min_score
        ORDER BY final_score DESC, e.timestamp DESC
        LIMIT :limit
    """

    params = {'query': 'Vitamin', 'min_score': 0.0, 'limit': 20}
    result = db_session.execute(text(sql), params)
    rows = result.fetchall()
    print(f"Repository-style query: {len(rows)} results")

    for row in rows:
        print(f"  Question: {row[2][:40]}...")
        print(f"  FTS Rank: {row[12]}")
        print(f"  Final Score: {row[13]}")
        print()

except Exception as e:
    print(f"Repository-style query failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test without rank filter
print("3. Testing without rank filter...")
try:
    sql = """
        SELECT
            e.exchange_id,
            qa_search.rank as fts_rank
        FROM qa_search
        JOIN qa_exchanges e ON qa_search.rowid = e.rowid
        JOIN sessions s ON e.session_id = s.session_id
        WHERE qa_search MATCH :query
        ORDER BY qa_search.rank DESC
    """

    result = db_session.execute(text(sql), {'query': 'Vitamin'})
    rows = result.fetchall()
    print(f"Without rank filter: {len(rows)} results")

    for row in rows:
        print(f"  Exchange ID: {row[0]}")
        print(f"  FTS Rank: {row[1]}")

except Exception as e:
    print(f"No rank filter query failed: {e}")
    import traceback
    traceback.print_exc()

print()
db_session.close()
print("=== ADVANCED DEBUG COMPLETED ===")