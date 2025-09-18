# LocalInsightEngine 🚀

**Intelligente, urheberrechtskonforme Analyse von Sachbüchern und Dokumenten**

![Work in Progress](https://img.shields.io/badge/Status-Production%20Ready%20v0.1.1-green)
![MIT License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
[![Developed with Claude Code](https://img.shields.io/badge/Developed%20with-Claude%20Code-purple)](https://claude.ai/code)

Eine vollständig funktionsfähige Python-Anwendung zur Analyse von PDF-Dokumenten mit Hilfe großer Sprachmodelle, ohne dabei urheberrechtlich geschützte Inhalte zu übertragen.

## ✨ Features

- **📖 Sachbuch-Modus**: Bypass für faktische Inhalte - keine Anonymisierung wissenschaftlicher Begriffe
- **🔒 Urheberrechtskonform**: Niemals Originaltext an externe APIs (außer im bewusst gewählten Sachbuch-Modus)
- **🏗️ 3-Layer-Architektur**: Saubere Trennung von Datenverarbeitung und Analyse
- **🇩🇪 Deutsche & Englische NLP**: spaCy-basierte Named Entity Recognition
- **🤖 Claude-4 Integration**: Modernste KI-Analyse mit intelligenten Insights
- **📁 Multi-Format Support**: PDF, TXT, EPUB, DOCX mit automatischer Erkennung
- **🔍 File-Type Validation**: Erkennt echten Dateityp unabhängig von Extension
- **📊 Vollständige Nachverfolgbarkeit**: Jede Erkenntnis zurück zur Quelle verfolgbar
- **🧪 Umfassende Tests**: Unit-, Integration- und Multi-Language Tests
- **⚡ Produktionsreif**: Moderne Python-Architektur mit Code Quality

### 🆕 Neue Enterprise-Features (v0.1.1)

- **🔍 FTS5 Semantic Search**: SQLite-basierte Volltext-Suche mit BM25-Ranking für intelligente Q&A
- **🗄️ Persistent Q&A Sessions**: Automatische SQLite-Persistierung aller Analyse-Sessions
- **📊 Enhanced Debug Logging**: Comprehensive Performance-Tracking und detaillierte Analyse-Logs
- **⚙️ Konfigurationsdatei**: `localinsightengine.conf` für alle System-Einstellungen
- **🚀 Database Auto-Creation**: Automatische SQLite-DB-Erstellung mit WAL-Mode und FTS5-Support
- **🎯 Smart Q&A System**: Multi-Layer Search (FTS5 → Keyword → Fallback) mit Context-Awareness
- **📈 Performance Monitoring**: Detaillierte Metriken für Document Loading, Processing und LLM Analysis
- **🔄 Robust Fallback Systems**: Graceful Degradation bei Database/FTS5-Fehlern

## 🏛️ Architektur

### Layer 1: Daten-Layer (`data_layer`)
- **PDF/EPUB/DOCX Parser** mit präzisem Seiten- und Absatz-Mapping
- **Unterstützte Formate**: PDF, TXT, EPUB, Word-Dokumente
- **Metadaten-Extraktion**: Autor, Titel, Seitenanzahl, etc.

### Layer 2: Verarbeitungs-Layer (`processing_hub`)  
- **spaCy NER**: Hochpräzise Entitätenerkennung für Deutsch & Englisch
- **Statement-Extraktor**: Neutralisierung von Kernaussagen
- **Text-Chunking**: Intelligente Aufteilung mit Überlappung
- **Copyright-Compliance**: Vollständige Neutralisierung vor externer Übertragung

### Layer 3: Analyse-Layer (`analysis_engine`)
- **Claude-4 API Integration**: Modernste KI-Analyse mit intelligenten Insights
- **Robuste JSON-Parsing**: Automatische Fallback-Mechanismen
- **Strukturierte Outputs**: Erkenntnisse, Fragen, Zusammenfassungen
- **Mock-Modus**: Funktioniert auch ohne API-Key für Tests

### 🆕 Persistence Layer (`persistence`)
- **SQLite Database**: Automatische Erstellung mit WAL-Mode für Concurrency
- **FTS5 Full-Text Search**: BM25-Ranking mit Time-Decay für semantische Suche
- **Q&A Session Management**: Vollständige Persistierung aller Analyse-Sessions
- **Smart Search Engine**: Cross-Session Knowledge Discovery und Related Insights
- **Repository Pattern**: High-Level CRUD Operations mit Business Logic

### 🆕 Enhanced Logging (`utils`)
- **Debug Logger**: Performance-Tracking und detaillierte System-Metriken
- **Konfigurable Log-Pfade**: Projektverzeichnis oder temporärer Ordner
- **Log Rotation**: 50MB max, 5 Backup-Dateien mit automatischer Cleanup
- **Dependency Validation**: Automatische Checks aller kritischen Komponenten

## 🚀 Installation

### 1. Repository klonen
```bash
git clone https://github.com/ddumdi11/LocalInsightEngine.git
cd LocalInsightEngine
```

### 2. Virtual Environment erstellen
```bash
# Python 3.8+ erforderlich (außerhalb venv)
py -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac  
source .venv/bin/activate
```

### 3. Dependencies installieren
```bash
# Alle Abhängigkeiten installieren (innerhalb aktivierter venv)
python -m pip install -r requirements-dev.txt

# SpaCy-Modelle herunterladen
python -m spacy download de_core_news_sm  # Deutsch
python -m spacy download en_core_web_sm   # Englisch (optional)
```

### 4. (Optional) Claude API-Key setzen
```bash
# Für echte KI-Analyse
export LLM_API_KEY="your-claude-api-key"

# Oder in .env Datei:
echo "LLM_API_KEY=your-claude-api-key" > .env
```

## 📖 Sachbuch-Modus (Neu!)

**Für wissenschaftliche und faktische Inhalte** - Der Sachbuch-Modus ermöglicht die vollständige Analyse von Sachbüchern ohne Anonymisierung gängiger Begriffe.

### 🔄 Funktionsweise

**Vor der Analyse:**
```
☐ Sachbuch-Modus (keine Anonymisierung gängiger Begriffe) [AKTIV]
[Analyze Document] Button
```

**Nach Analyse im Standard-Modus:**
```
☐ Standard-Modus aktiv [AUSGEGRAUT]
[🔄 Neu analysieren im Sachbuch-Modus] Button
```

**Nach Analyse im Sachbuch-Modus:**
```
☑ Sachbuch-Modus aktiv [AUSGEGRAUT]
[🔄 Neu analysieren im Standard-Modus] Button
```

### 🎯 Vorteile des Sachbuch-Modus

- ✅ **Präzise Vitamin-Analysen**: "Vitamin B3" bleibt erhalten statt neutralisiert
- ✅ **Wissenschaftliche Begriffe**: Niacin, Magnesium, Folsäure werden nicht anonymisiert
- ✅ **A/B Testing**: Direkter Vergleich beider Modi in der GUI
- ✅ **User-Kontrolle**: Bewusste Entscheidung pro Dokument
- ✅ **Rechtssicherheit**: Standard-Modus bleibt aktiv für urheberrechtlich geschützte Literatur

### ⚖️ Rechtliche Einordnung

**Sachbuch-Modus ist sicher für:**
- Wissenschaftliche Fachbegriffe (Vitamin B3, Calcium, etc.)
- Medizinische Terminologie
- Allgemeine Sachbuch-Inhalte
- Faktische Informationen

**Standard-Modus verwenden für:**
- Belletristik und kreative Werke
- Persönliche/private Dokumente
- Unbekannte Urheberrechtssituation

## 🎯 Nutzung

### Einfacher Start mit Start.bat (Empfohlen)
```bash
# Dokument analysieren
Start.bat document.pdf

# Version anzeigen
Start.bat --version

# Schnelltest ausführen
Start.bat --test

# Hilfe anzeigen
Start.bat --help
```

### Direkte CLI-Nutzung (innerhalb aktivierter .venv)
```bash
# Dokument analysieren
python -m local_insight_engine.main document.pdf

# Version anzeigen
python -m local_insight_engine.main --version

# Hilfe anzeigen
python -m local_insight_engine.main --help
```

### Tests & Validierung (innerhalb aktivierter .venv)
```bash
# Multi-Format Test (TXT bevorzugt, PDF Fallback) - EMPFOHLEN
python tests/test_multiformat.py

# Multi-Language Test (Deutsch & Englisch)  
python tests/test_multilanguage.py

# File-Type Detection & Validation
python tests/test_file_detection.py

# Unit Tests für Core-Komponenten
python tests/test_unit_tests.py

# Claude API Debugging
python tests/test_claude_debug.py

# Legacy PDF-only Test
python tests/test_pdf_processing.py
```

## ⚙️ Konfiguration

### localinsightengine.conf (Neu!)

Das System erstellt automatisch eine Konfigurationsdatei `localinsightengine.conf` im Projektverzeichnis mit allen wichtigen Einstellungen:

```ini
[Logging]
# Log-Verzeichnis: 'temp' für System-Temp oder absoluter Pfad
log_directory = .
log_filename = localinsightengine.log
log_level = DEBUG
console_output = true
max_log_size_mb = 50
backup_count = 5

[Database]
# SQLite-Datenbank-Pfad
database_path = data/qa_sessions.db
auto_create_db = true
enable_fts5 = true

[Analysis]
# Standard-Modus für Sachbuch-Analyse
default_factual_mode = false
max_qa_chunks = 100
enable_semantic_search = true

[Performance]
# Performance-Logging aktivieren
enable_performance_logging = true
log_chunk_details = true
log_entity_details = true
```

### 📊 Enhanced Logging

**Automatische Log-Erstellung:**
- **Log-Datei**: `localinsightengine.log` (konfigurierbar)
- **Performance-Tracking**: Detaillierte Metriken für alle Operationen
- **Debug-Informationen**: Chunk-Details, Entity-Extraktion, Q&A-Sessions
- **Dependency-Validation**: Automatische Checks aller Komponenten

**Log-Beispiel:**
```
2025-09-18 07:26:28 | INFO | LocalInsightEngine | STEP 1: Initializing LocalInsightEngine
2025-09-18 07:26:28 | INFO | LocalInsightEngine | DATABASE: Database initialized
2025-09-18 07:26:28 | INFO | LocalInsightEngine | ✅ spaCy model de_core_news_sm: Available
2025-09-18 07:26:29 | INFO | LocalInsightEngine | PERF END: document_analysis - Duration: 15.234s
```

### 🗄️ Persistent Database

**Automatische SQLite-Erstellung:**
- **Datei**: `data/qa_sessions.db` (mit WAL-Mode)
- **FTS5-Support**: Volltext-Suche mit BM25-Ranking
- **Session-Management**: Alle Q&A-Sessions persistent gespeichert
- **Cross-Session Search**: Intelligente Suche über alle Dokumente

### Programmatische Nutzung
```python
from pathlib import Path
from local_insight_engine.main import LocalInsightEngine

# Engine initialisieren (mit automatischer DB-Erstellung)
engine = LocalInsightEngine()

# Dokument im Standard-Modus analysieren
results = engine.analyze_document(Path("your-document.pdf"))

# Dokument im Sachbuch-Modus analysieren
results_factual = engine.analyze_document(Path("scientific-paper.pdf"), factual_mode=True)

# Intelligente Q&A mit FTS5 Semantic Search
answer = engine.answer_question("Was steht im Text zu Vitamin B3?")
print(f"Antwort: {answer}")

# Weitere Q&A-Sessions (nutzen automatisch Semantic Search)
answer2 = engine.answer_question("Welche Nebenwirkungen werden erwähnt?")

# Ergebnisse anzeigen
print(f"Status: {results['status']}")
print(f"Erkenntnisse: {len(results.get('insights', []))}")
print(f"Executive Summary: {results.get('executive_summary', 'N/A')}")

# Performance-Logs werden automatisch geschrieben nach:
# localinsightengine.log (im Projektverzeichnis)
```

## 📁 Projektstruktur

```
LocalInsightEngine/
├── src/
tests/
README.md
└── README.md
```

## 🤝 Development mit Claude Code

Dieses Projekt wird in Zusammenarbeit mit [Claude Code](https://claude.ai/code) entwickelt - einem KI-gestützten Entwicklungsassistenten, der bei:

- 🔍 Code-Analyse und Refactoring
- 📝 Dokumentation und README-Erstellung  
- 🐛 Debugging und Problemlösung
- 🧪 Test-Implementierung
- 📊 Repository-Optimierung

unterstützt hat.

## 📈 Roadmap

### ✅ Abgeschlossen (v0.1.1)
- [x] Vollständige 3-Layer-Architektur
- [x] PDF/EPUB/DOCX-Parser mit präzisem Mapping
- [x] spaCy-Integration (Deutsch + Englisch)
- [x] Claude-4 API-Client mit modernsten Modellen
- [x] Statement-Neutralisierung für Copyright-Compliance
- [x] Komplette Test-Pipeline mit Unit- und Integrationstests
- [x] **JSON Export-Funktionalität** (CLI, Start.bat, programmatisch)
- [x] **Copyright-Compliance** (✅ All anonymization tests passing)

### 🚧 Geplant (v0.2.0)
- [x] **Anonymization Issues Fixed** (✅ Intelligent entity neutralization)
- [ ] **Persistent QA System** - Interactive document analysis with session memory
  - [ ] Knowledge graph persistence across sessions
  - [ ] Context-aware question answering
  - [ ] Incremental learning from user interactions
  - [ ] Bookmark and annotation system
- [ ] File-type detection warnings for mismatched extensions
- [ ] CSV/PDF Export-Formate
- [ ] Web-Interface (FastAPI + React)
- [ ] Batch-Processing für multiple Dokumente

### 🔮 Zukunft (v1.0.0)
- [ ] Graphische Benutzeroberfläche
- [ ] Database-Backend für große Dokumente
- [ ] Multi-Language Support (erweitert)
- [ ] Collaborative Analysis Features
- [ ] Enterprise-Deployment-Optionen

## 🤔 Probleme & Lösungen

### Bekannte Issues:
- **Problem**: Kleinere Performance-Issues
  - **Status**: In Bearbeitung
  - **Workaround**: Temporäre Lösung verfügbar

## 📄 Lizenz

Dieses Projekt ist unter der [MIT License](LICENSE) lizensiert - siehe [LICENSE](LICENSE) Datei für Details.

## 👨‍💻 Autor

**Diede** - *Initial work* - [ddumdi11](https://github.com/ddumdi11)

### 🛠️ Entwickelt mit Unterstützung von:
- [Claude Code](https://claude.ai/code) - KI-gestützter Entwicklungsassistent

## 🙏 Danksagungen

- Claude Code Team für die innovative Entwicklungsunterstützung
- Open Source Community

---

⭐ **Gefällt dir das Projekt?** Gib ihm einen Stern und folge mir für weitere innovative Entwicklungen!

📧 **Kontakt**: ***@*** (auf Anfrage) | 💼 **LinkedIn**: https://www.linkedin.com/in/thorsten-diederichs-a05051203/
