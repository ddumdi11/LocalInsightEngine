from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd().parent / "src"))

from local_insight_engine.persistence.repository import SessionRepository
from local_insight_engine.persistence.models import QAExchange
from local_insight_engine.models.analysis import AnalysisResult, Insight
from uuid import uuid4

# Repository erstellen
repo = SessionRepository()

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
  document_path=Path("german_sample.txt"),
  analysis_result=analysis,
  display_name="Live Test Document Fixed",
  tags=["test", "live", "demo"]
)

print(f"Session created: {session.session_id}")

# Q&A Exchange DIREKT über Repository (umgeht das Session-Binding Problem)
with repo._get_session() as db_session:
  exchange1 = QAExchange(
      session_id=session.session_id,
      question="Was ist der Hauptinhalt dieses Dokuments?",
      answer="Das Dokument behandelt verschiedene Themen rund um Gesundheit und Ernährung, mit besonderem Fokus auf Vitamine.",
      confidence_score=0.85,
      tokens_used=150,
      claude_model="claude-sonnet-4-20250514"
  )

  exchange2 = QAExchange(
      session_id=session.session_id,
      question="Welche Vitamine werden erwähnt?",
      answer="Hauptsächlich werden B-Vitamine wie B3 (Niacin) und B12 erwähnt, sowie Vitamin C und D.",
      confidence_score=0.92,
      tokens_used=120,
      is_bookmarked=True
  )

  db_session.add(exchange1)
  db_session.add(exchange2)
  db_session.commit()

  print(f"Exchange 1: {exchange1.exchange_id}")
  print(f"Exchange 2: {exchange2.exchange_id}")
  print(f"Bookmarked: {exchange2.is_bookmarked}")

# FTS5 Search Test
search_results = repo.search_qa_content("Vitamin")
print(f"Search 'Vitamin': {len(search_results)} results")

for result in search_results:
  print(f"  - Question: {result.question[:50]}...")
  print(f"  - Score: {result.final_score:.3f}")