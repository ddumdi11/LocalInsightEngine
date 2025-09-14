# 🚀 **LocalInsightEngine - Persistent Q&A System**

**Erweiterte Vision: Intelligent Document Memory System**

*Von "Session-basierte Konversationen" zu "Persistente Dokument-Intelligenz"*

---

## 🎯 **NEUE SUPERPOWERS**

### **📚 Document Memory Bank**
- **Jede Q&A-Session wird dauerhaft gespeichert**
- **Intelligente Suche** durch alle bisherigen Fragen/Antworten
- **Cross-Document-Insights** aus mehreren Dokumenten
- **Learning Effect** - bessere Antworten durch Kontext-Historie

### **🕰️ Time-Travel Q&A**
- **Session-Timeline** - springe zu jedem Zeitpunkt zurück
- **Question History** - sehe alle jemals gestellten Fragen
- **Answer Evolution** - verfolge, wie sich Antworten entwickelt haben
- **Favorites & Bookmarks** für wichtige Insights

---

## 🏗️ **ERWEITERTE ARCHITEKTUR**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                                         │
│  ├── Enhanced Chat Interface (History + Search)                            │
│  ├── Session Browser (All Documents)                                       │
│  ├── Favorites Manager                                                      │
│  └── Smart Search (Cross-Document Q&A)                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENHANCED SESSION MANAGEMENT LAYER                                          │
│  ├── PersistentSessionManager (Lifecycle + Storage)                        │
│  ├── SessionRepository (CRUD Operations)                                   │
│  ├── IntelligentConversationEngine (Context + History)                     │
│  ├── CrossSessionAnalyzer (Multi-Document Insights)                        │
│  └── SmartContextOptimizer (History-Aware)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENHANCED DATA LAYER                                                        │
│  ├── SQLite Session Database (Local + Fast)                                │
│  ├── Document Index (Fast Retrieval)                                       │
│  ├── Q&A Archive (Full-Text Search)                                        │
│  ├── Favorites & Tags Storage                                              │
│  └── Smart Cache Management                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 **DATENMODELL 2.0**

class PersistentQASession:
    # Core Session Data
    session_id: UUID
    document_path_hash: str              # HMAC-SHA256(secret_pepper, canonical_path)
    pepper_id: str                       # Reference to KMS-managed pepper (rotation support)
    document_hash: str                   # Content hash
    document_display_name: str           # Optional, sanitized
    source_id: Optional[str]             # Opaque ref instead of path

    # Analysis Data
    analysis_result: AnalysisResult
    neutralized_context: str             # Copyright-safe content
    neutralization_version: str          # e.g., "v0.1.1"
    policy_id: str                       # Policy/build that did neutralization
    retention_days: int                  # Data retention policy
    consent_basis: Optional[str]         # GDPR/CCPA basis

    # Conversation History
    conversation_history: List[QAExchange]
    session_metadata: SessionMetadata

    # Persistence & Retrieval
    created_at: datetime
    last_accessed: datetime
    total_questions: int
    session_tags: List[str]              # User-defined tags
    is_favorite: bool

    # Smart Features
    related_sessions: List[UUID]         # Cross-document connections
    auto_generated_summary: str          # AI-generated session summary
    key_insights_extracted: List[str]    # Most important findings

### **💬 Enhanced Q&A Exchange**
```python
class QAExchange:
    exchange_id: UUID
    question: str
    answer: str

    # Context & Intelligence
    context_used: str                     # What context was sent to Claude
    confidence_score: float              # 0..1
    answer_quality: Literal["excellent","good","partial","low"]

    # User Interaction
    user_rating: Optional[int]           # 1..5
    user_notes: str                      # Personal annotations
    is_bookmarked: bool

    # Meta Information
    timestamp: datetime
    processing_time: float
    tokens_used: int                     # >=0
    claude_model: str
    answer_origin: Literal["neutralized","synthesized"]
    safety_flags: List[str]              # e.g., PII_SUSPECT, COPYRIGHT_RISK
    checksum: str                        # hash(answer)

    # Relations
    related_exchanges: List[UUID]        # Follow-up questions
    document_references: List[str]       # Which parts were relevant

### **🏷️ Smart Tagging & Organization**
```python
class SessionMetadata:
    # Auto-Generated Tags
    document_type: str                   # "research", "legal", "technical"
    main_topics: List[str]              # Extracted automatically
    complexity_level: str               # "basic", "intermediate", "advanced"

    # User Organization
    custom_tags: List[str]              # User-defined
    project_name: Optional[str]         # Group sessions by project
    priority: int                       # User-defined importance

    # Smart Features
    similar_sessions: List[UUID]        # AI-detected similarities
    recommendation_score: float        # How valuable for others
```

---

## 🔍 **INTELLIGENT SEARCH SYSTEM**

### **Unified SQLite FTS5 Search Architecture**
```python
class SmartSearchEngine:
    """
    Single-source-of-truth search using SQLite FTS5 with BM25 + time-decay ranking.
    No separate in-memory SearchIndex to prevent index drift and duplication.
    """

    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection
        self.fts5_table = "qa_search_fts"  # Only neutralized content indexed
        self._setup_fts5_ranking_view()

    def search_qa_history(self, query: str, time_decay: float = 0.1) -> List[SearchResult]:
        # 🔍 SQLite FTS5 full-text search with BM25 ranking
        # ⏱️ Configurable time-decay scoring (recent = higher score)
        # 🛡️ Only searches neutralized/sanitized content
        # 🚀 Single database query, no memory overhead

    def find_similar_questions(self, question: str) -> List[QAExchange]:
        # 🤖 FTS5 MATCH query with semantic keywords
        # 📊 BM25 relevance scoring
        # 🔗 Cross-document connections via FTS5 joins

    def discover_related_insights(self, session_id: UUID) -> List[Insight]:
        # 🕸️ FTS5 content analysis with ranking views
        # 🧩 Pattern recognition through SQL aggregations
        # 💡 Suggest follow-up questions from similar content

    def _setup_fts5_ranking_view(self):
        # Creates persistent ranking view combining:
        # - BM25 relevance score from FTS5
        # - Time-decay factor (configurable)
        # - Ensures only neutralized content is searchable
        # - Provides single rebuild/refresh procedure to prevent drift
```

**Key Architecture Benefits:**
- ✅ **Single Source of Truth**: Only SQLite FTS5, no duplicate in-memory index
- ✅ **No Index Drift**: One canonical search index prevents synchronization issues
- ✅ **Copyright Compliance**: Strict pipeline ensures only neutralized content is indexed
- ✅ **Performance**: BM25 + time-decay ranking with sub-second response times
- ✅ **Consistency**: Single rebuild/refresh procedure, no complex synchronization

### **Search Interface**
```
┌─ SEARCH: "vitamin b3 benefits" ─────────── [🔍] ─┐
│ Results across 12 sessions:                      │
│                                                  │
│ 📄 nutrition_study.pdf (3 months ago)           │
│   🙋 "What are the benefits of vitamin B3?"     │
│   💡 "Niacin supports energy metabolism..."     │
│   ⭐⭐⭐⭐⭐ (5/5) 🔖 Bookmarked               │
│                                                  │
│ 📄 supplement_guide.txt (1 week ago)            │
│   🙋 "Side effects of niacin supplements?"      │
│   💡 "High doses can cause flushing..."         │
│   ⭐⭐⭐⭐ (4/5)                               │
└──────────────────────────────────────────────────┘
```

---

## 💾 **PERSISTENCE STRATEGY**

### **Local SQLite Database**
-- Sessions Table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    document_path_hash TEXT NOT NULL,        -- HMAC-SHA256(secret_pepper, canonical_path)
    pepper_id TEXT NOT NULL,                 -- KMS pepper reference for rotation support
    document_hash TEXT NOT NULL,
    document_display_name TEXT,
    created_at TEXT NOT NULL,            -- ISO-8601 UTC
    last_accessed TEXT NOT NULL,         -- ISO-8601 UTC
    is_favorite INTEGER NOT NULL DEFAULT 0 CHECK(is_favorite IN (0,1)),
    session_tags TEXT NOT NULL CHECK(json_valid(session_tags)), -- JSON array
    neutralized_context TEXT,
    analysis_result_json TEXT NOT NULL,  -- Full AnalysisResult
    neutralization_version TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    retention_days INTEGER NOT NULL CHECK(retention_days >= 0),
    consent_basis TEXT CHECK(consent_basis IN ('consent','contract','legal_obligation','vital_interests','public_task','legitimate_interests')),
    expires_at TEXT GENERATED ALWAYS AS (
      datetime(created_at, printf('+%d days', retention_days))
    ) VIRTUAL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_sessions_dochash ON sessions(document_hash);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_pepper_id ON sessions(pepper_id);  -- Support pepper rotation queries

-- Q&A Exchanges Table
CREATE TABLE qa_exchanges (
    exchange_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    timestamp TEXT NOT NULL,             -- ISO-8601 UTC
    user_rating INTEGER CHECK(user_rating BETWEEN 1 AND 5),
    is_bookmarked INTEGER NOT NULL DEFAULT 0 CHECK(is_bookmarked IN (0,1)),
    context_used TEXT,
    tokens_used INTEGER NOT NULL CHECK(tokens_used >= 0),
    confidence_score REAL CHECK(confidence_score BETWEEN 0 AND 1),
    answer_quality TEXT,
    answer_origin TEXT,
    safety_flags TEXT,                   -- JSON array
    checksum TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_exchanges_session_ts ON qa_exchanges(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_sessions_last_accessed ON sessions(last_accessed);

-- Full-Text Search Index
CREATE VIRTUAL TABLE qa_search USING fts5(
    question, answer, context_used,
    content='qa_exchanges'
);

-- Keep FTS in sync
CREATE TRIGGER IF NOT EXISTS qa_exchanges_ai AFTER INSERT ON qa_exchanges BEGIN
  INSERT INTO qa_search(rowid, question, answer, context_used)
  VALUES (new.rowid, new.question, new.answer, new.context_used);
END;
CREATE TRIGGER IF NOT EXISTS qa_exchanges_ad AFTER DELETE ON qa_exchanges BEGIN
  INSERT INTO qa_search(qa_search, rowid, question, answer, context_used)
  VALUES('delete', old.rowid, old.question, old.answer, old.context_used);
END;
CREATE TRIGGER IF NOT EXISTS qa_exchanges_au AFTER UPDATE ON qa_exchanges BEGIN
  INSERT INTO qa_search(qa_search, rowid, question, answer, context_used)
  VALUES('delete', old.rowid, old.question, old.answer, old.context_used);
  INSERT INTO qa_search(rowid, question, answer, context_used)
  VALUES (new.rowid, new.question, new.answer, new.context_used);
END;

### **Smart Caching Strategy**
```python
class PersistenceManager:
    def __init__(self):
        self.db_path = Path("data/qa_sessions.db")
        self.cache = LRUCache(maxsize=100)      # Recent sessions in memory
        self.index = SearchIndex()              # Fast full-text search

    async def save_session(self, session: PersistentQASession):
        # 💾 Save to SQLite
        # 🔍 Update search index
        # 🧠 Extract insights for recommendations
        # 🔗 Find similar sessions

    async def load_session(self, session_id: UUID) -> PersistentQASession:
        # ⚡ Check cache first
        # 📂 Load from database
        # 🔄 Update last_accessed
```

---

## 🎨 **GUI TRANSFORMATION 2.0**

### **Multi-Panel Interface**
```
┌─ LocalInsightEngine ─────────────────────────── [⚙️] ─┐
│ ┌─ SESSION BROWSER ─┐ ┌─ ACTIVE CHAT ─────────────┐   │
│ │ 📂 Recent Sessions │ │ 📄 Current: research.pdf  │   │
│ │ ⭐ Favorites        │ │                           │   │
│ │ 🔍 Search History  │ │ 🙋 You: What about B12?  │   │
│ │ 🏷️ By Tags         │ │ 💡 AI: B12 is crucial... │   │
│ │ 📊 Statistics      │ │                           │   │
│ │                    │ │ 🙋 You: Compare to B3?   │   │
│ │ 📄 nutrition.pdf   │ │ 💡 AI: Both are water-   │   │
│ │   Last: 2 days ago │ │     soluble vitamins...   │   │
│ │   Questions: 23    │ │                           │   │
│ │                    │ │ [Type question...]  [📤] │   │
│ │ 📄 supplement.txt  │ └───────────────────────────┘   │
│ │   Last: 1 week ago │                               │
│ │   Questions: 8     │ ┌─ INSIGHTS PANEL ────────┐   │
│ │                    │ │ 🔗 Related Questions:   │   │
│ │ + Load New Doc...  │ │ • "B vitamin absorption" │   │
│ └────────────────────┘ │ • "Supplement timing"    │   │
│                         │                          │   │
│                         │ 🏷️ Suggested Tags:      │   │
│                         │ #vitamins #nutrition     │   │
│                         │                          │   │
│                         │ ⭐ Quick Actions:        │   │
│                         │ [🔖 Bookmark] [⭐ Rate] │   │
│                         └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### **Session Timeline View**
```
┌─ SESSION TIMELINE: nutrition.pdf ─────────────────────────┐
│                                                           │
│ ● 2025-01-10 14:30 - Session Started                     │
│   🙋 "What vitamins are mentioned?"                      │
│   💡 "The document mentions B3, B12, C, and D..."       │
│                                                           │
│ ● 2025-01-10 14:35 - Follow-up Questions                 │
│   🙋 "Tell me more about B3"                             │
│   💡 "Vitamin B3 (niacin) supports..."                  │
│   ⭐⭐⭐⭐⭐ Rated 5/5 🔖 Bookmarked                    │
│                                                           │
│ ● 2025-01-15 09:20 - Resumed Session                     │
│   🙋 "What about B3 dosage recommendations?"             │
│   💡 "The recommended daily allowance..."                │
│                                                           │
│ [📥 Export Timeline] [🔍 Search in Session] [⭐ Add to Favorites] │
└───────────────────────────────────────────────────────────┘
```

---

## ⚡ **PERFORMANCE OPTIMIERUNGEN 2.0**

### **Intelligent Context Management**
```python
class HistoryAwareContextOptimizer:
    def optimize_context(self, session: PersistentQASession, new_question: str):
        # 🧠 Analyze question against full history
        # 🎯 Select most relevant past exchanges
        # 🔗 Include cross-references from related sessions
        # ⚡ Minimize token usage through smart summarization

        context_strategy = self.determine_strategy(new_question, session.conversation_history)

        if context_strategy == "historical_reference":
            # User asks about something discussed before
            return self.build_historical_context(session, new_question)
        elif context_strategy == "cross_session_insight":
            # Question could benefit from other documents
            return self.build_cross_session_context(session, new_question)
        else:
            # Standard context with session memory
            return self.build_enhanced_context(session, new_question)
```

### **Token Efficiency mit History**
| Strategie | Tokens (Initial) | Tokens (With History) | Einsparung |
|-----------|------------------|----------------------|------------|
| Cold Start | 4000 | 4000 | 0% |
| Session Follow-up | 3000 | 800 | 73% |
| Related Question | 3500 | 1200 | 66% |
| Cross-Document | 5000 | 2000 | 60% |

---

class ComplianceManager:
    def audit_session_storage(self, session_id: UUID):
        # ✅ Verify only neutralized content is stored (sample rows + regex checks)
        # ✅ No original text in database
        # ✅ All Q&As use processed content only (answer_origin != "raw")
        # ✅ Export logs for compliance review
        # ✅ Validate FTS index parity and deletions (GDPR)

    def generate_compliance_report(self) -> ComplianceReport:
        # 📋 Full audit + pipeline version, policy_id, neutralization_version
        # 🔍 Detection of any potential violations
        # 📊 Statistics on content neutralization
        # ✅ Certification of copyright compliance

### **Data Privacy Features**
```python
class PrivacyControls:
    def anonymize_session(self, session_id: UUID):
        # 🎭 Remove personal information from Q&As
        # 🔒 Encrypt sensitive data
        # 🗑️ Right to be forgotten:
        # 1) DELETE FROM qa_exchanges WHERE session_id=?
        # 2) DELETE FROM sessions WHERE session_id=?
        # 3) Purge qa_search entries (triggers handle, else manual)
        # 4) EXECUTE: PRAGMA wal_checkpoint(TRUNCATE); VACUUM;
        # 5) Verify no residuals via compliance audit

    def export_user_data(self) -> UserDataExport:
        # 📦 GDPR-compliant data export
        # 🔍 Full transparency over stored data
        # 🗂️ Machine-readable format

class SecurePepperManager:
    """🔐 SECURITY: HMAC-SHA256 Path Hashing with Pepper Management"""

    def generate_document_path_hash(self, canonical_path: str, pepper_id: str) -> str:
        # 🛡️ SECURITY: HMAC-SHA256(secret_pepper, canonical_path)
        # ✅ Prevents path-guessing attacks vs plain SHA-256
        # 🔄 Supports pepper rotation via pepper_id
        secret_pepper = self.get_pepper_by_id(pepper_id)  # From KMS
        return hmac.new(secret_pepper, canonical_path.encode(), hashlib.sha256).hexdigest()

    def get_pepper_by_id(self, pepper_id: str) -> bytes:
        # 🔑 KMS Integration: Retrieve pepper by ID
        # 🚫 NEVER persist raw pepper values in database
        # 🔄 Support multiple pepper versions for rotation
        pass

    def rotate_pepper(self, old_pepper_id: str, new_pepper_id: str):
        # 🔄 Pepper Rotation Strategy:
        # 1) Generate new pepper in KMS
        # 2) Re-hash all document_path_hash with new pepper
        # 3) Update pepper_id references
        # 4) Mark old pepper for deprecation (not immediate deletion)
        # 5) Background process to verify migration completeness
        pass

---

## 🎯 **IMPLEMENTATION ROADMAP 2.0**

### **Phase 1: Core Persistence** (4-6 Stunden)
- [ ] SQLite Database Schema
- [ ] PersistentQASession Model
- [ ] Basic SessionRepository
- [ ] Simple GUI Session List

### **Phase 2: Enhanced Features** (6-8 Stunden)
- [ ] Full-Text Search Implementation
- [ ] Session Timeline View
- [ ] Bookmarks & Favorites
- [ ] Cross-Session Intelligence

### **Phase 3: Advanced GUI** (4-6 Stunden)
- [ ] Multi-Panel Interface
- [ ] Smart Context Display
- [ ] Search & Filter Controls
- [ ] Export & Import Features

### **Phase 4: Intelligence Layer** (8-10 Stunden)
- [ ] Cross-Document Analysis
- [ ] Smart Recommendations
- [ ] Auto-Tagging System
- [ ] Performance Analytics

### **Phase 5: Production Ready** (2-4 Stunden)
- [ ] Compliance Auditing
- [ ] Error Recovery
- [ ] Performance Optimization
- [ ] Documentation & Testing

---

## 📈 **ERWARTETE SUPERPOWERS**

| Feature | Before | With Persistent Sessions | Verbesserung |
|---------|--------|-------------------------|-------------|
| Q&A Speed | 8-12s | 2-4s | **75% faster** |
| Token Usage | ~3000/Q | ~400/Q | **87% less** |
| Knowledge Retention | None | Infinite | **∞ better** |
| Cross-Document Insights | None | Full | **New capability** |
| Search & Discovery | None | Instant | **New capability** |
| User Experience | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **Professional grade** |

---

## 🎉 **DAS ENDRESULTAT**

**Eine persistente Dokument-Intelligenz** die:

🧠 **Nie vergisst** - jede Frage und Antwort permanent verfügbar
🔍 **Blitzschnell sucht** - durch alle jemals gestellten Fragen
🌐 **Verbindungen erkennt** - zwischen verschiedenen Dokumenten
⚡ **Rasend schnell antwortet** - durch intelligenten Kontext-Cache
💡 **Schlauer wird** - mit jeder Nutzung durch Cross-Reference-Learning
🛡️ **Copyright-konform** - auch bei dauerhafter Speicherung
🎨 **Professionell aussieht** - wie eine echte Knowledge-Management-Suite

---

## 🔧 **TECHNISCHE DETAILS**

### **Aktuelle Probleme zu lösen:**
1. **Q&A Context-Building** - Bessere Extraktion der analysierten Inhalte
2. **Response Parsing** - Robustere Antwort-Extraktion aus Claude API
3. **Performance** - Token-Optimierung für Follow-up Fragen

### **Neue Dateien zu erstellen:**
- `src/local_insight_engine/persistence/` - Persistence Layer
- `src/local_insight_engine/gui/session_browser.py` - Session Management GUI
- `src/local_insight_engine/search/` - Search Engine
- `data/qa_sessions.db` - SQLite Database

### **Bestehende Dateien zu erweitern:**
- `main_window.py` - Integration mit Session System
- `claude_client.py` - History-aware Context Building
- `models/` - Neue Session Models

---

*Dokumentation erstellt am: 2025-09-13*
*Version: 2.0*
*Status: Ready for Implementation* ✅

---

**Ready to build the future of document intelligence?** 🚀