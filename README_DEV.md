# LocalInsightEngine 🚀

**Intelligente, urheberrechtskonforme Analyse von Sachbüchern und Dokumenten**

Eine vollständig funktionsfähige Python-Anwendung zur Analyse von PDF-Dokumenten mit Hilfe großer Sprachmodelle, ohne dabei urheberrechtlich geschützte Inhalte zu übertragen.

## ✨ Features

- **🔒 Urheberrechtskonform**: Niemals Originaltext an externe APIs
- **🏗️ 3-Layer-Architektur**: Saubere Trennung von Datenverarbeitung und Analyse  
- **🇩🇪 Deutsche & Englische NLP**: spaCy-basierte Named Entity Recognition
- **🤖 Claude-4 Integration**: Modernste KI-Analyse mit intelligenten Insights
- **📁 Multi-Format Support**: PDF, TXT, EPUB, DOCX mit automatischer Erkennung
- **🔍 File-Type Validation**: Erkennt echten Dateityp unabhängig von Extension
- **📊 Vollständige Nachverfolgbarkeit**: Jede Erkenntnis zurück zur Quelle verfolgbar
- **🧪 Umfassende Tests**: Unit-, Integration- und Multi-Language Tests
- **⚡ Produktionsreif**: Moderne Python-Architektur mit Code Quality

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

## 🚀 Installation

### 1. Repository klonen
```bash
git clone https://github.com/your-username/LocalInsightEngine.git
cd LocalInsightEngine
```

### 2. Virtual Environment erstellen
```bash
# Python 3.8+ erforderlich
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

### Tests & Validierung (innerhalb aktivierter venv)
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

### Programmatische Nutzung
```python
from pathlib import Path
from local_insight_engine.main import LocalInsightEngine

# Engine initialisieren
engine = LocalInsightEngine()

# Dokument analysieren
results = engine.analyze_document(Path("your-document.pdf"))

# Ergebnisse anzeigen
print(f"Analysierte {results['chunks']} Chunks")
print(f"Erkannte {results['entities']} Entitäten")
print(f"Executive Summary: {results['summary']}")
```

## 📊 Beispiel-Ausgabe

```
[PDF] Testing PDF processing with: example.pdf
============================================================
[INIT] Initializing components...
[LOAD] Loading document...
SUCCESS: Document loaded successfully!
   - File format: pdf
   - File size: 1655241 bytes
   - Page count: 383
   - Word count: 73925
   - Paragraphs: 371

[PROCESS] Processing text (neutralizing content)...
SUCCESS: Text processed successfully!
   - Total chunks: 1056
   - Total entities: 5285
   - Processing time: 15.48 seconds
   - Key themes: 10

[ANALYSIS] Running Claude analysis...
SUCCESS: Claude analysis completed!
   - Status: success
   - Model: claude-sonnet-4-20250514
   - Confidence: 0.87
   - Insights: 15
   - Questions: 8

[SUMMARY] Executive Summary:
Das Dokument behandelt komplexe philosophische Konzepte...
```

## 🛠️ Entwicklung

### Code-Qualität prüfen (innerhalb aktivierter venv)
```bash
# Formatierung
python -m black .
python -m isort .

# Linting
python -m flake8
python -m pylint src/

# Type Checking
python -m mypy .
```

### Tests ausführen (innerhalb aktivierter venv)
```bash
# Alle Tests
python -m pytest

# Mit Coverage
python -m pytest --cov --cov-report=html

# Schneller Test
python test_pdf_processing.py
```

## 📁 Projektstruktur

```
LocalInsightEngine/
├── src/local_insight_engine/
│   ├── __init__.py
│   ├── main.py                    # Haupt-API
│   ├── config/
│   │   ├── settings.py           # Konfiguration
│   ├── models/                   # Datenmodelle
│   │   ├── document.py          # PDF/Document models
│   │   ├── text_data.py         # Text processing models
│   │   └── analysis.py          # Analysis result models
│   └── services/                 # Business Logic
│       ├── data_layer/          # Layer 1: PDF/Document loading
│       ├── processing_hub/      # Layer 2: Text processing & NER
│       └── analysis_engine/     # Layer 3: Claude API integration
├── tests/                        # Test suite
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── test_pdf_processing.py       # Quick integration test
├── CLAUDE.md                    # Claude Code development guide
└── README.md                    # This file
```

## 🔧 Konfiguration

Die Anwendung kann über Umgebungsvariablen oder eine `.env`-Datei konfiguriert werden:

```bash
# Claude API
LLM_API_KEY=your-api-key-here
LLM_MODEL=claude-3-sonnet-20240229

# Text Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
SPACY_MODEL=de_core_news_sm

# Directories
DATA_DIR=~/.local_insight_engine
CACHE_DIR=~/.local_insight_engine/cache

# Limits
MAX_FILE_SIZE_MB=50
MAX_API_REQUESTS=20
```

## 📋 Roadmap

### ✅ Abgeschlossen (v0.1.0)
- [x] Vollständige 3-Layer-Architektur
- [x] PDF/EPUB/DOCX-Parser mit Mapping
- [x] spaCy-Integration (Deutsch + Englisch)
- [x] Claude API-Client
- [x] Statement-Neutralisierung
- [x] Komplette Test-Pipeline
- [x] **JSON Export-Funktionalität** (CLI, Start.bat, programmatisch)
- [x] **Export Unit-Tests** mit Anonymization Proof Tests
- [⚠️] Copyright-Compliance (needs review - canary tests failed)

### 🚧 Geplant (v0.2.0)
- [⚠️] **CRITICAL: Fix Anonymization Issues** (canary phrases in export detected)
- [ ] Add file-type detection warnings for fake PDFs
- [ ] CSV/PDF Export-Formate  
- [ ] Web-Interface (FastAPI + React)
- [ ] Batch-Processing für multiple Dokumente
- [ ] Erweiterte Visualisierungen
- [ ] Verbessertes Caching
- [ ] Plugin-System für andere LLMs

### 🔮 Zukunft (v1.0.0)
- [ ] Graphische Benutzeroberfläche
- [ ] Database-Backend für große Dokumente
- [ ] Multi-Language Support
- [ ] Collaborative Analysis Features
- [ ] Enterprise-Deployment-Optionen

## 🤝 Beitragen

Contributions sind willkommen! Bitte beachte:

1. **Fork** das Repository
2. **Branch** für dein Feature erstellen (`git checkout -b feature/amazing-feature`)
3. **Code-Quality** sicherstellen (`py -m black . && py -m flake8`)
4. **Tests** schreiben und ausführen (`py -m pytest`)
5. **Pull Request** erstellen

## 📄 Lizenz

Dieses Projekt steht unter der [MIT License](LICENSE).

## 🙏 Danksagungen

- **spaCy** für erstklassige NLP-Funktionalität
- **Anthropic** für die Claude API
- **PyPDF2** für PDF-Verarbeitung
- **Pydantic** für robuste Datenvalidierung

## 🐛 Probleme melden

Falls du Probleme findest:

1. **spaCy-Modelle** installiert? `py -m spacy download de_core_news_sm`
2. **Virtual Environment** aktiviert? `.venv\Scripts\activate`
3. **Dependencies** aktuell? `py -m pip install -r requirements-dev.txt`

Bei weiteren Fragen öffne ein [Issue](https://github.com/your-username/LocalInsightEngine/issues).

---

**Made with ❤️ for copyright-compliant document analysis**