"""
Quick test to verify FTS5 search syntax fix
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd().parent / "src"))

from local_insight_engine.persistence.repository import SessionRepository

print("=== FTS5 SEARCH SYNTAX FIX TEST ===")
print()

repo = SessionRepository()

# Test if we can create the search engine without SQL syntax errors
try:
    # Simple search that would trigger the syntax error before fix
    results = repo.search_qa_content("Vitamin", min_score=0.0)
    print(f"SUCCESS: Search executed without syntax error")
    print(f"Results count: {len(results)}")

    if results:
        print(f"First result: {results[0].question[:50]}...")

except Exception as e:
    print(f"ERROR: {e}")

print()
print("=== FTS5 FIX TEST COMPLETED ===")