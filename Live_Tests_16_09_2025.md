🧪 Live-Test #1: Basic Persistence + Repository

  # Aktiviere das venv und starte Python
  source .venv/Scripts/activate
  python

  # Test-Code:
  from pathlib import Path
  import sys
  sys.path.insert(0, str(Path.cwd() / "src"))

  from local_insight_engine.persistence.repository import SessionRepository
  from local_insight_engine.models.analysis import AnalysisResult, Insight
  from uuid import uuid4

  # Repository erstellen
  repo = SessionRepository()

  # Test-Dokument (nimm eine echte PDF/TXT Datei)
  test_doc = Path("german_sample.txt")  # oder eine andere Datei die du hast

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

  print(f"Session created: {session.session_id}")
  print(f"Document: {session.document_display_name}")
  print(f"Tags: {session.session_tags}")

  Was ich wissen möchte:
  1. Funktioniert die Session-Erstellung ohne Fehler?
  2. Wird eine Session-ID generiert?
  3. Werden die Tags korrekt gespeichert?

  ---
  🧪 Live-Test #2: Q&A Exchanges hinzufügen

  # Nach Test #1 weitermachen:

  # Q&A Exchange hinzufügen
  exchange1 = repo.add_qa_exchange(
      session.session_id,
      "Was ist der Hauptinhalt dieses Dokuments?",
      "Das Dokument behandelt verschiedene Themen rund um Gesundheit und Ernährung, mit besonderem Fokus auf
  Vitamine.",
      confidence_score=0.85,
      tokens_used=150,
      claude_model="claude-sonnet-4-20250514"
  )

  exchange2 = repo.add_qa_exchange(
      session.session_id,
      "Welche Vitamine werden erwähnt?",
      "Hauptsächlich werden B-Vitamine wie B3 (Niacin) und B12 erwähnt, sowie Vitamin C und D.",
      confidence_score=0.92,
      tokens_used=120,
      is_bookmarked=True
  )

  print(f"Exchange 1: {exchange1.exchange_id}")
  print(f"Exchange 2: {exchange2.exchange_id}")
  print(f"Bookmarked: {exchange2.is_bookmarked}")

  # Session-Info aktualisiert?
  updated_session = repo.get_session_by_id(session.session_id)
  print(f"Total questions: {updated_session.total_questions}")

  Was mich interessiert:
  1. Werden die Q&A Exchanges korrekt erstellt?
  2. Wird der total_questions Counter aktualisiert?
  3. Wird das Bookmark korrekt gesetzt?

  ---
  🧪 Live-Test #3: FTS5 Search

  # Nach Test #1 + #2:

  # Verschiedene Suchbegriffe testen
  search_results = repo.search_qa_content("Vitamin")
  print(f"Search 'Vitamin': {len(search_results)} results")

  for result in search_results:
      print(f"  - Question: {result.question[:50]}...")
      print(f"  - Score: {result.final_score:.3f}")
      print(f"  - Document: {result.document_display_name}")

  # Komplexere Suche
  search_results2 = repo.search_qa_content("Gesundheit Ernährung")
  print(f"Search 'Gesundheit Ernährung': {len(search_results2)} results")

  # Bookmark-only Suche
  bookmark_results = repo.search_qa_content("Vitamin", bookmarked_only=True)
  print(f"Bookmarked 'Vitamin': {len(bookmark_results)} results")

  Was ich testen möchte:
  1. Funktioniert die FTS5-Suche?
  2. Werden relevante Ergebnisse gefunden?
  3. Funktioniert das Bookmark-Filter?
  4. Sind die Scores sinnvoll?

  ---
  Fang erstmal mit Test #1 an und schick mir die Ergebnisse! Je nachdem was passiert, passen wir die nächsten Tests
  an.

  Besonders interessiert mich:
  - Funktioniert die Database-Erstellung ohne Fehler?
  - Werden die Sessions korrekt persistiert?
  - Gibt es irgendwelche Import-Probleme oder Unicode-Issues?

  Starte einfach und wir gehen Step-by-Step durch! 🚀