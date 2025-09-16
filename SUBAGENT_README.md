# Subagent-Aktivierung für LocalInsightEngine

## 🎯 Quick Reference Guide

Kopiere einfach die gewünschten Kommandos und füge sie in Claude Code ein.

---

## 🚀 Einzelne Subagents aktivieren

### Performance-Optimizer Agent

**Wann nutzen:** PDF-Processing zu langsam, Memory-Probleme, Performance-Optimierung
```
Starte Performance-Optimizer Agent für LocalInsightEngine.

FOKUS: PDF-Processing Optimization, Memory Management, Async Processing
ARBEITSBEREICH: src/local_insight_engine/services/data_layer/
ZIEL: Performance-Verbesserung bei PDF-Verarbeitung

AUFGABEN:
1. Analysiere aktuelle PDF-Processing Performance
2. Identifiziere Memory- und Performance-Bottlenecks
3. Optimiere für große PDF-Dateien
4. Erstelle Performance-Benchmarks
5. Implementiere Streaming/Chunking-Optimierungen

WICHTIG: Aktiviere .venv mit `.venv\Scripts\activate`, nutze "python" statt "py"
STANDARDS: CLAUDE.md Guidelines, Type Hints, pytest für Benchmarks
```

### Test-Engineer Agent

**Wann nutzen:** Test Coverage verbessern, Edge Cases testen, Qualitätssicherung
```
Starte Test-Engineer Agent für LocalInsightEngine.

FOKUS: Comprehensive Test Coverage, Edge Cases, Performance Tests
ARBEITSBEREICH: tests/ + Test-Integration in alle Module
ZIEL: 95% Test Coverage und Edge Case Abdeckung

AUFGABEN:
1. Analysiere aktuelle Test Coverage
2. Identifiziere und teste Edge Cases für PDF-Processing
3. Erweitere Tests für Error-Handling und Memory-Issues
4. Erstelle Performance-Validierungstests
5. Quick Coverage-Check kritischer Module

WICHTIG: Aktiviere .venv mit `.venv\Scripts\activate`, nutze "python" statt "py"
STANDARDS: pytest, Type Hints, CLAUDE.md Guidelines
```

### API-Developer Agent

**Wann nutzen:** REST API implementieren, OpenAPI Specs, Client SDKs
```
Starte API-Developer Agent für LocalInsightEngine.

FOKUS: REST API Interface Implementation für v0.3.0
ARBEITSBEREICH: Neue API Layer (src/local_insight_engine/api/)
ZIEL: Production-ready REST API mit OpenAPI Documentation

AUFGABEN:
1. Designe REST API Struktur für Document Analysis
2. Implementiere FastAPI/Flask Setup
3. Erstelle OpenAPI Specifications
4. Implementiere Request/Response Validation
5. Erstelle Client SDK Grundlagen

WICHTIG: Aktiviere .venv mit `.venv\Scripts\activate`, nutze "python" statt "py"
STANDARDS: CLAUDE.md Guidelines, Type Hints, RESTful Design
```

### DevOps-Automation Agent

**Wann nutzen:** Docker Setup, CI/CD Pipeline, Deployment Automation
```
Starte DevOps-Automation Agent für LocalInsightEngine.

FOKUS: CI/CD, Docker, Deployment Automation
ARBEITSBEREICH: Docker, GitHub Actions, Infrastructure
ZIEL: Production-ready Deployment Pipeline

AUFGABEN:
1. Erstelle Docker Container für LocalInsightEngine
2. Implementiere GitHub Actions CI/CD Pipeline
3. Setup Deployment Automation
4. Erstelle Docker Compose für Development
5. Implementiere Infrastructure as Code

WICHTIG: Aktiviere .venv mit `.venv\Scripts\activate`, nutze "python" statt "py"
STANDARDS: CLAUDE.md Guidelines, Docker Best Practices
```

### Documentation-Specialist Agent

**Wann nutzen:** Technical Documentation, User Guides, API Docs erstellen
```
Starte Documentation-Specialist Agent für LocalInsightEngine.

FOKUS: Technical Documentation, User Guides, API Documentation
ARBEITSBEREICH: docs/, README Updates, Code Documentation
ZIEL: Comprehensive Documentation für v1.0.0

AUFGABEN:
1. Erstelle Technical Documentation mit Sphinx/MkDocs
2. Schreibe User Guides und Tutorials
3. Dokumentiere API Endpoints und Schemas
4. Erstelle Developer Guides
5. Verbessere Code Documentation und Docstrings

WICHTIG: Aktiviere .venv mit `.venv\Scripts\activate`, nutze "python" statt "py"
STANDARDS: CLAUDE.md Guidelines, Sphinx/MkDocs Standards
```

---

## ⚡ Quick Start Kombinationen

### Option 1: Beide Core-Agents (Empfohlen für sofortige Verbesserungen)
```
Starte Performance-Optimizer Agent und Test-Engineer Agent parallel für LocalInsightEngine.

PERFORMANCE-AGENT:
- FOKUS: PDF-Processing Optimization, Memory Management
- ZIEL: Performance-Verbesserung bei großen PDF-Dateien

TEST-ENGINEER-AGENT:
- FOKUS: Test Coverage Verbesserung, Edge Cases
- ZIEL: 95% Coverage und robuste Edge Case Abdeckung

Beide sollen .venv aktivieren (`.venv\Scripts\activate`) und "python" statt "py" nutzen.
Arbeite nach CLAUDE.md Guidelines mit Type Hints und pytest.
```

### Option 2: Development-Trio (Performance + Test + API)
```
Starte Performance-Optimizer, Test-Engineer und API-Developer Agents parallel für LocalInsightEngine.

PERFORMANCE: PDF-Processing Optimization
TEST-ENGINEER: Coverage + Edge Cases
API-DEVELOPER: REST API für v0.3.0

Alle Agents: .venv aktivieren, "python" nutzen, CLAUDE.md Guidelines befolgen.
```

### Option 3: Full-Stack Agents (Alle 5 parallel)
```
Starte alle 5 Subagents parallel für LocalInsightEngine:

1. Performance-Optimizer: PDF-Processing Optimization
2. Test-Engineer: Test Coverage + Edge Cases
3. API-Developer: REST API Implementation
4. DevOps-Automation: Docker + CI/CD
5. Documentation-Specialist: Technical Documentation

Alle: .venv aktivieren, "python" nutzen, CLAUDE.md Guidelines.
```

---

## 🔄 Reaktivierung nach Claude Code Neustart

### Nach `claude` Kommando im Terminal:
```
Reaktiviere Performance-Optimizer und Test-Engineer Agents parallel basierend auf vorherigen Sessions.

Kontext: Beide Agents haben bereits an LocalInsightEngine gearbeitet:
- Performance-Optimizer hat StreamingDocumentLoader mit PyMuPDF erstellt
- Test-Engineer hat Coverage-Analyse durchgeführt (36% → 95% Ziel)

Setze die Arbeit fort wo sie aufgehört haben.
```

---

## 📋 Spezialisierte Aufgaben

### Performance-Troubleshooting
```
Starte Performance-Optimizer Agent für akutes Performance-Problem.

SPEZIFISCHES PROBLEM: [Beschreibe das Problem hier]
ZIEL: Sofortige Diagnose und Lösung
```

### Bug-Fix mit Tests
```
Starte Test-Engineer Agent für Bug-Reproduktion und Fixes.

BUG-BESCHREIBUNG: [Beschreibe den Bug hier]
ZIEL: Test-First Bug-Fix mit Edge Case Coverage
```

### API-Endpoint hinzufügen
```
Starte API-Developer Agent für neuen Endpoint.

ENDPOINT: [/api/v1/analyze oder ähnlich]
FUNKTIONALITÄT: [Was soll der Endpoint machen]
```

---

## 💡 Tipps für optimale Subagent-Nutzung

### ✅ Best Practices:
- **Immer spezifisches Ziel angeben** statt nur "mach was"
- **Parallele Aktivierung** für unabhängige Aufgaben nutzen
- **Kontext mitgeben** wenn Agents auf vorherige Arbeit aufbauen sollen
- **Performance + Test** Agents fast immer zusammen nutzen

### ❌ Vermeiden:
- Subagents für triviale Ein-Zeilen-Änderungen
- Überlappende Aufgaben ohne Koordination
- Vergessen der .venv Aktivierung in den Prompts

---

## 📞 Häufige Aktivierungsszenarien

| Situation | Empfohlener Agent | Quick Command |
|-----------|-------------------|---------------|
| PDF zu langsam | Performance-Optimizer | "Performance-Optimizer für PDF-Optimierung starten" |
| Tests fehlen | Test-Engineer | "Test-Engineer für Coverage-Verbesserung starten" |
| API gebraucht | API-Developer | "API-Developer für REST Interface starten" |
| Deployment Setup | DevOps-Automation | "DevOps-Agent für Docker/CI-CD starten" |
| Doku erstellen | Documentation-Specialist | "Documentation-Agent für Tech-Docs starten" |
| Alles parallel | Full-Stack | "Alle 5 Subagents parallel starten" |

---

**Tipp:** Speichere diese Datei als Bookmark - so hast du alle Kommandos griffbereit!