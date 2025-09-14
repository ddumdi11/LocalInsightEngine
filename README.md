# LocalInsightEngine 🚀

**Intelligente, urheberrechtskonforme Analyse von Sachbüchern und Dokumenten**

![Work in Progress](https://img.shields.io/badge/Status-Production%20Ready%20v0.1.1-green)
![MIT License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
[![Developed with Claude Code](https://img.shields.io/badge/Developed%20with-Claude%20Code-purple)](https://claude.ai/code)

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
