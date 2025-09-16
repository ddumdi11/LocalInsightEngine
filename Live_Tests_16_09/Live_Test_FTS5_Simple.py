# Temporärer FTS5-Test (direkte SQL-Query)
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd().parent / "src"))

from local_insight_engine.persistence.database import get_database_manager

db_manager = get_database_manager()

with db_manager.get_session() as session:
  from sqlalchemy import text

  # Einfache FTS5 Suche (ohne komplexe Ranking)
  result = session.execute(text("""
	  SELECT question, answer
	  FROM qa_search
	  WHERE qa_search MATCH 'Vitamin'
  """))

  rows = result.fetchall()
  print(f"Simple FTS5 search: {len(rows)} results")

  for row in rows:
	  print(f"  Q: {row.question[:50]}...")
	  print(f"  A: {row.answer[:50]}...")