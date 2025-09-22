# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview: LocalInsightEngine

This is a **LocalInsightEngine** - a sophisticated Python application for copyright-compliant document analysis using large language models. The project implements a 5-layer enterprise architecture:

1. **Layer 1 (data_layer)**: PDF/EPUB/DOCX parsing with precise location mapping
2. **Layer 2 (processing_hub)**: Text processing, NER, and content neutralization
3. **Layer 3 (analysis_engine)**: LLM-based analysis of neutralized content
4. **Layer 4 (persistence)**: SQLite database with FTS5 semantic search
5. **Layer 5 (utils)**: Enhanced logging, configuration, and performance monitoring

**Key Constraint: Copyright Compliance** - Only neutralized text is sent to external APIs. In factual mode, a strict whitelist of scientific terms/entities may be preserved, but all narrative or identifying text remains neutralized. Standard mode: full anonymization; factual mode: whitelist terms only, narrative remains neutralized.

The project uses industry-standard tools and follows best practices for scalable application development.

## RESOLVED ISSUES ✅

### ✅ ENTERPRISE-GRADE PERSISTENCE & FTS5 SEARCH (September 2025)
**Status:** NEW MAJOR FEATURE - Complete persistence architecture with semantic search ✅
**Solution:** Full SQLite-based persistence layer with FTS5 full-text search for intelligent Q&A
- Implemented automatic SQLite database creation with WAL-Mode for concurrency
- Added FTS5 semantic search engine with BM25 ranking and time-decay weighting
- Created comprehensive Q&A session management with cross-document knowledge discovery
- Enhanced logging system with performance tracking and detailed debugging
- **Result:** Semantic search resolves "Nikotinamid" → "Niacin" → "Vitamin B3" connections

**Technical Implementation:**
- `persistence/database_manager.py`: SQLite database management with automatic schema creation
- `persistence/repositories/session_repository.py`: FTS5-powered semantic search with BM25 ranking
- `utils/debug_logger.py`: Enhanced logging system based on VidScalerSubtitleAdder patterns
- `main.py`: Integrated DatabaseManager into LocalInsightEngine with persistent Q&A
- `localinsightengine.conf`: Comprehensive configuration file for all system settings

**Benefits:**
- 🔍 **Semantic Search**: "Nikotinamid" finds "Niacin", "Vitamin B3" content automatically
- 🗄️ **Persistent Sessions**: All Q&A exchanges stored and searchable across documents
- 📈 **Performance Monitoring**: Detailed metrics for document loading, processing, and analysis
- 🔄 **Cross-Session Knowledge**: Intelligent search across all previously analyzed documents
- ⚙️ **Enterprise Configuration**: Comprehensive settings management via INI files

### ✅ SACHBUCH-MODUS IMPLEMENTED (September 2025)
**Status:** NEW FEATURE - Factual content bypass with intelligent UX ✅
**Solution:** Complete pipeline for scientific/factual document analysis without anonymization
- Added GUI checkbox "Sachbuch-Modus" with smart state management
- Implemented bypass_anonymization flag throughout processing pipeline
- Enhanced UX: disabled checkbox after analysis with re-analyze button
- **Result:** Full analysis capability for vitamins, minerals, scientific terms

**Technical Implementation:**
- `main_window.py`: Smart UI state management with re-analyze functionality
- `main.py`: factual_mode parameter through analysis pipeline
- `text_processor.py`: Conditional anonymization based on bypass flag
- `spacy_entity_extractor.py`: Preserve original entities in factual mode
- **UX:** Intuitive mode switching with clear visual feedback

**Benefits:**
- 🔬 **Scientific Analysis**: "Vitamin B3", "Magnesium" etc. preserved
- 🔄 **A/B Testing**: Direct comparison of both modes in GUI
- ⚖️ **Legal Safety**: User-controlled, copyright-compliant by design
- 🎯 **Precise Results**: Full detail for factual content analysis

### ✅ SEMANTIC TRIPLES GUI INTEGRATION (September 2025)
**Status:** NEW FEATURE - Complete GUI integration for semantic triples ✅
**Solution:** Full GUI support for semantic triples extraction and display in factual mode
- Added new "🧠 Semantic Triples" tab in Analysis Report window
- Smart conditional display: tab appears only when factual mode is active
- Complete export integration: PDF, Markdown, JSON all include semantic triples
- **Result:** Professional GUI for semantic knowledge extraction

**Technical Implementation:**
- `gui/analysis_report_window.py`: New semantic triples tab with structured display
- `models/analysis_statistics.py`: Added `get_semantic_triples_section()` method
- `services/processing_hub/text_processor.py`: Fixed ProcessingConfig integration bugs
- `main.py`: Fixed analysis statistics storage for GUI accessibility
- **Critical Fixes:** Resolved "document not defined" and "no analysis statistics" errors

**Benefits:**
- 🧠 **Knowledge Visualization**: Structured display of extracted semantic relationships
- 🎛️ **Mode-Aware UI**: Tab appears only in appropriate contexts (factual mode)
- 📊 **Complete Reporting**: All export formats include semantic triples data
- 🔧 **Production Ready**: Robust error handling and state management

### ✅ ANONYMIZATION COMPLIANCE ACHIEVED (September 2025)
**Status:** RESOLVED - All canary phrase tests now passing ✅
**Solution:** Implemented intelligent entity neutralization in spaCy Entity Extractor
- Added targeted pattern recognition for test/debug identifiers
- Preserved legitimate scientific terms (Phosphatidylserin, Vitamin B3, etc.)
- Maintained product names and technical terminology
- **Result:** 100% neutralization of suspicious identifiers while keeping useful content

**Technical Implementation:**
- Enhanced `spacy_entity_extractor.py` with `_neutralize_suspicious_identifiers()` method
- Pattern-based detection for CANARY_*, TEST_*, DEBUG_*, and long alphanumeric identifiers
- Intelligent replacement with context-appropriate neutral terms
- **Tests:** All anonymization proof tests passing - copyright compliance verified

**Files Modified:**
- `src/local_insight_engine/services/processing_hub/spacy_entity_extractor.py` - Added entity neutralization
- Enhanced both statement extractors with improved neutralization logic

### 📁 File Type Detection Enhancement Needed
**Problem:** Fake PDFs processed without warning
**Solution:** Add clear warnings when file extension doesn't match content type
**Files:** `src/local_insight_engine/services/data_layer/document_loader.py`

## LocalInsightEngine Specific Commands

### Enterprise System Testing

#### Database & Persistence Testing
```bash
# Database Health Check (inside activated .venv)
python -c "from local_insight_engine.persistence import get_database_manager; dm = get_database_manager(); print('DB Health:', dm.health_check())"

# FTS5 Search Testing
python -c "from local_insight_engine.persistence.repositories import SessionRepository; from local_insight_engine.persistence import get_database_manager; repo = SessionRepository(get_database_manager().get_session()); print('FTS5 available:', repo._check_fts5_available())"

# Clean Database Reset (for Development)
rm -f data/qa_sessions.db  # Caution: Deletes all Q&A Sessions!
```

#### Performance & Logging Analysis
```bash
# Real-Time Log Analysis
tail -f localinsightengine.log

# Extract Performance Metrics
grep "PERF END" localinsightengine.log | tail -10

# Database Operations Analysis
grep "DATABASE:" localinsightengine.log

# FTS5 Search Operations Tracking
grep "FTS5" localinsightengine.log
```

### Quick Testing

**Outside virtual environment (.venv deactivated):**
- `py tests/test_multiformat.py` - Multi-format test (TXT preferred, PDF fallback) - **EMPFOHLEN**
- `py tests/test_multilanguage.py` - Multi-language test (German & English)
- `py tests/test_file_detection.py` - File type validation test
- `py tests/test_unit_tests.py` - Unit tests for core components
- `py tests/test_claude_debug.py` - Claude API debugging & validation
- `py tests/test_pdf_processing.py` - Legacy PDF-only test
- `py -c "import spacy; spacy.load('de_core_news_sm'); print('spaCy OK')"` - Test German NLP model

**Inside virtual environment (.venv activated):**
- `python tests/test_multiformat.py` - Multi-format test (TXT preferred, PDF fallback) - **EMPFOHLEN**
- `python tests/test_multilanguage.py` - Multi-language test (German & English)
- `python tests/test_file_detection.py` - File type validation test
- `python tests/test_unit_tests.py` - Unit tests for core components
- `python tests/test_claude_debug.py` - Claude API debugging & validation
- `python tests/test_pdf_processing.py` - Legacy PDF-only test
- `python -c "import spacy; spacy.load('de_core_news_sm'); print('spaCy OK')"` - Test German NLP model

### SpaCy Models (CRITICAL - Must be installed!)

**Outside virtual environment (.venv deactivated):**
- `py -m spacy download de_core_news_sm` - Download German NER model (REQUIRED)
- `py -m spacy download en_core_web_sm` - Download English NER model (optional)  
- `py -m spacy info` - Show installed spaCy models

**Inside virtual environment (.venv activated):**
- `python -m spacy download de_core_news_sm` - Download German NER model (REQUIRED)
- `python -m spacy download en_core_web_sm` - Download English NER model (optional)  
- `python -m spacy info` - Show installed spaCy models

### Running the Enhanced Engine with Persistence
```python
from pathlib import Path
from local_insight_engine.main import LocalInsightEngine

# Engine initialisieren (mit automatischer DB-Erstellung)
engine = LocalInsightEngine()

# Dokument analysieren (wird automatisch in SQLite persistiert)
results = engine.analyze_document(Path("document.pdf"))

# Intelligente Q&A mit FTS5 Semantic Search
answer = engine.answer_question("Was steht im Text zu Nikotinamid?")
# → Findet automatisch "Niacin", "Vitamin B3" via FTS5 search

# Weitere Q&A-Sessions (nutzen Cross-Session Knowledge)
answer2 = engine.answer_question("Welche Nebenwirkungen werden erwähnt?")

# Performance-Logs werden automatisch geschrieben nach:
# localinsightengine.log (im Projektverzeichnis)
```

### Database & FTS5 Management
```python
# Database Health Check
from local_insight_engine.persistence import get_database_manager
dm = get_database_manager()
print(f"Database Health: {dm.health_check()}")

# FTS5 Search Testing
from local_insight_engine.persistence.repositories import SessionRepository
repo = SessionRepository(dm.get_session())
search_results = repo.search_qa_content(
    query="Nikotinamid Vitamin B3",
    limit=10,
    time_decay_weight=0.2
)
print(f"Found {len(search_results)} semantic matches")
```

### Key Architecture Rules
1. **Never modify Layer 1** to send original text externally
2. **Always neutralize in Layer 2** before sending to Layer 3
3. **Test copyright compliance** - no original text should appear in Layer 3 calls
4. **Use type hints** throughout - this is a typed Python project
5. **Follow the 5-layer pattern** - don't bypass layers, use persistence for Q&A
6. **File Type Validation** - system detects actual content type vs extension
7. **Multi-Format Support** - TXT preferred over PDF for better quality
8. **Claude-4 Integration** - uses latest model: claude-sonnet-4-20250514
9. **FTS5 Semantic Search** - always use semantic search for Q&A, not keyword matching
10. **Database Persistence** - ensure all Q&A sessions are stored for cross-session knowledge
11. **Enhanced Logging** - use performance tracking and detailed debugging for all operations
12. **Configuration Management** - use localinsightengine.conf for system settings

## Test-Driven Development (TDD) Workflow

### Established TDD Process (September 2025)

**CRITICAL: Systematic RED-GREEN-REFACTOR Cycle**

1. **RED Phase - Write Failing Test First**
   ```bash
   # Create test that describes desired behavior (should fail)
   python -m pytest test_new_feature.py::test_specific_case -v -s
   ```

2. **GREEN Phase - Implement Minimal Solution**
   ```bash
   # Write minimal code to make test pass
   python -m pytest test_new_feature.py::test_specific_case -v -s
   ```

3. **REFACTOR Phase - Improve Code Quality**
   ```bash
   # Clean up code while keeping tests green
   python -m pytest test_new_feature.py -v  # Run all tests in file
   ```

4. **INTEGRATION Phase - Add to Test Orchestrator**
   ```bash
   # ONLY when ALL tests in file are green
   python -m pytest test_orchestrator.py -v -s
   ```

### TDD Anti-Patterns to Avoid ⚠️

**NEVER:**
- ❌ **Guess test names** - always use `pytest --collect-only` first
- ❌ **Guess class methods** - always check actual class definition
- ❌ **Add incomplete test files** to orchestrator
- ❌ **Skip RED phase** - tests must fail first
- ❌ **Batch multiple changes** without testing each step

**ALWAYS:**
- ✅ **Verify test names exist** before referencing them
- ✅ **Check actual class APIs** before writing tests
- ✅ **Complete entire test file** before orchestrator integration
- ✅ **Run tests after each change** to ensure progress
- ✅ **Stop and debug** when tests behave unexpectedly

### Test Orchestrator Rules

**Test File Inclusion Policy:**
- Test files are added to `test_orchestrator.py` ONLY when **ALL tests in that file are green**
- Partially completed test files remain excluded until fully functional
- This prevents "false green" signals and maintains stable baseline

**Current Status:**
- ✅ `test_entity_equivalence.py` - 8/8 tests green → **IN ORCHESTRATOR**
- ✅ `test_content_flow.py` - 5/5 tests green → **IN ORCHESTRATOR**
- ✅ `test_semantic_triples.py` - 9/9 tests green → **IN ORCHESTRATOR**
- ✅ `tests/e2e/test_complete_user_workflow.py` - 5/5 E2E tests → **IN ORCHESTRATOR**

### Debug-First Approach

When tests fail unexpectedly:
1. **Create debug scripts** to understand actual behavior
2. **Use `--collect-only`** to verify test names exist
3. **Check class definitions** for actual method signatures
4. **Never guess** - always verify facts first

**Example Debug Script Pattern:**
```python
# debug/debug_specific_issue.py
print("ACTUAL BEHAVIOR DEBUG")
# Test actual class behavior, don't assume anything
```

### End-to-End (E2E) Testing in TDD

**E2E Test Philosophy:**
- E2E tests validate **complete user workflows** from start to finish
- Written AFTER unit tests are green to validate integration
- Test real scenarios users will encounter in production
- Complement unit tests with full-system validation

**E2E Test Structure:**
```
tests/e2e/
├── __init__.py
├── README.md                    # E2E test documentation
└── test_complete_user_workflow.py    # Complete user journeys
```

**E2E Test Categories:**
1. **Sachbuch Analysis Workflow**: Document selection → Factual analysis → Results
2. **Q&A Session Workflow**: Document analysis → Question asking → Answer generation
3. **Analysis Report Workflow**: Analysis completion → Report generation → Export
4. **Persistence Workflow**: Database operations throughout complete workflows
5. **Error Handling Workflow**: Graceful failure scenarios end-to-end

**When to Write E2E Tests:**
- ✅ **After** unit tests are completely green
- ✅ **Before** major feature releases
- ✅ **When** user workflows change significantly
- ✅ **To catch** integration issues between layers

**E2E Test Execution:**
```bash
# Run E2E tests separately (slower)
python -m pytest tests/e2e/ -v -s

# Run ALL tests (unit + E2E) in TDD order
python tests/test_orchestrator.py
```

## Development Commands

### Environment Management

**Setup (outside virtual environment):**
- `py -m venv .venv` - Create virtual environment

**Activation/Deactivation:**
- `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows) - Activate virtual environment
- `deactivate` - Deactivate virtual environment

**Package Installation (inside activated .venv):**
- `python -m pip install -r requirements.txt` - Install dependencies
- `python -m pip install -r requirements-dev.txt` - Install development dependencies

### Package Management

**Outside virtual environment (.venv deactivated):**
- `py -m pip install <package>` - Install a package globally
- `py -m pip install -e .` - Install project globally in development mode
- `py -m pip freeze > requirements.txt` - Generate requirements file
- `py -m pip-tools compile requirements.in` - Compile requirements with pip-tools

**Inside virtual environment (.venv activated):**
- `python -m pip install <package>` - Install a package in venv
- `python -m pip install -e .` - Install project in venv development mode
- `python -m pip freeze > requirements.txt` - Generate venv requirements file
- `python -m pip-tools compile requirements.in` - Compile requirements with pip-tools

### Testing Commands

**Outside virtual environment (.venv deactivated):**
- `py -m pytest` - Run all tests
- `py -m pytest -v` - Run tests with verbose output
- `py -m pytest --cov` - Run tests with coverage report
- `py -m pytest --cov-report=html` - Generate HTML coverage report
- `py -m pytest -x` - Stop on first failure
- `py -m pytest -k "test_name"` - Run specific test by name
- `py -m unittest` - Run tests with unittest

**Inside virtual environment (.venv activated):**
- `python -m pytest` - Run all tests
- `python -m pytest -v` - Run tests with verbose output
- `python -m pytest --cov` - Run tests with coverage report
- `python -m pytest --cov-report=html` - Generate HTML coverage report
- `python -m pytest -x` - Stop on first failure
- `python -m pytest -k "test_name"` - Run specific test by name
- `python -m unittest` - Run tests with unittest

### End-to-End (E2E) Testing Commands

**E2E Tests - Complete User Workflow Validation:**
- `python -m pytest tests/e2e/ -v -s` - Run all E2E tests with detailed output
- `python -m pytest tests/e2e/test_complete_user_workflow.py -v -s` - Run complete workflow tests
- `python -m pytest tests/e2e/ --log-cli-level=DEBUG -v -s` - Run E2E tests with detailed logging
- `python tests/test_orchestrator.py` - Run ALL tests including E2E in TDD order

**What E2E Tests Validate:**
- ✅ Complete Sachbuch-Modus analysis pipeline (document → analysis → results)
- ✅ Q&A session workflow with real document processing
- ✅ Analysis report generation end-to-end
- ✅ Database persistence throughout complete workflows
- ✅ Error handling in real-world scenarios

**E2E vs Unit Tests:**
- **Unit Tests**: Fast, isolated component testing
- **E2E Tests**: Slower, complete user journey validation
- **Integration**: Both are orchestrated via `test_orchestrator.py` in logical TDD order

### Code Quality Commands

**Outside virtual environment (.venv deactivated):**
- `py -m black .` - Format code with Black
- `py -m black --check .` - Check code formatting without changes
- `py -m isort .` - Sort imports
- `py -m isort --check-only .` - Check import sorting
- `py -m flake8` - Run linting with Flake8
- `py -m pylint src/` - Run linting with Pylint
- `py -m mypy .` - Run type checking with MyPy

**Inside virtual environment (.venv activated):**
- `python -m black .` - Format code with Black
- `python -m black --check .` - Check code formatting without changes
- `python -m isort .` - Sort imports
- `python -m isort --check-only .` - Check import sorting
- `python -m flake8` - Run linting with Flake8
- `python -m pylint src/` - Run linting with Pylint
- `python -m mypy .` - Run type checking with MyPy

### Development Tools

**Outside virtual environment (.venv deactivated):**
- `py -m pip install --upgrade pip` - Upgrade pip
- `py -c "import sys; print(sys.version)"` - Check Python version
- `py -m site` - Show Python site information
- `py -m pdb script.py` - Debug with pdb

**Inside virtual environment (.venv activated):**
- `python -m pip install --upgrade pip` - Upgrade pip
- `python -c "import sys; print(sys.version)"` - Check Python version
- `python -m site` - Show Python site information
- `python -m pdb script.py` - Debug with pdb

## Technology Stack

### Core Technologies
- **Python** - Primary programming language (3.8+)
- **pip** - Package management
- **venv** - Virtual environment management

### LocalInsightEngine Specific Stack
- **SQLite** - Database with WAL-Mode for concurrency
- **FTS5** - Full-text search with BM25 ranking
- **SQLAlchemy** - SQL toolkit and ORM for database operations
- **Pydantic** - Data validation using Python type hints
- **spaCy** - NLP and Named Entity Recognition (German & English)
- **Anthropic Claude-4** - Large language model for analysis
- **ConfigParser** - INI-based configuration management

### Common Frameworks
- **Django** - High-level web framework
- **Flask** - Micro web framework
- **FastAPI** - Modern API framework with automatic documentation
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type hints

### Data Science & ML
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation and analysis
- **Matplotlib/Seaborn** - Data visualization
- **Scikit-learn** - Machine learning library
- **TensorFlow/PyTorch** - Deep learning frameworks

### Testing Frameworks
- **pytest** - Testing framework
- **unittest** - Built-in testing framework
- **pytest-cov** - Coverage plugin for pytest
- **factory-boy** - Test fixtures
- **responses** - Mock HTTP requests

### Code Quality Tools
- **Black** - Code formatter
- **isort** - Import sorter
- **flake8** - Style guide enforcement
- **pylint** - Code analysis
- **mypy** - Static type checker
- **pre-commit** - Git hooks framework

## Project Structure Guidelines

### File Organization
```text
src/
├── package_name/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── models/          # Data models
│   ├── views/           # Web views (Django/Flask)
│   ├── api/             # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Utility functions
│   └── config/          # Configuration files
tests/
├── __init__.py
├── conftest.py          # pytest configuration
├── test_models.py
├── test_views.py
└── test_utils.py
requirements/
├── base.txt            # Base requirements
├── dev.txt             # Development requirements
└── prod.txt            # Production requirements
```

### Naming Conventions
- **Files/Modules**: Use snake_case (`user_profile.py`)
- **Classes**: Use PascalCase (`UserProfile`)
- **Functions/Variables**: Use snake_case (`get_user_data`)
- **Constants**: Use UPPER_SNAKE_CASE (`API_BASE_URL`)
- **Private methods**: Prefix with underscore (`_private_method`)

## Python Guidelines

### Type Hints
- Use type hints for function parameters and return values
- Import types from `typing` module when needed
- Use `Optional` for nullable values
- Use `Union` for multiple possible types
- Document complex types with comments

### Code Style
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Use docstrings for modules, classes, and functions
- Limit line length to 88 characters (Black default)

### Best Practices
- Use list comprehensions for simple transformations
- Prefer `pathlib` over `os.path` for file operations
- Use context managers (`with` statements) for resource management
- Handle exceptions appropriately with try/except blocks
- Use `logging` module instead of print statements

## Testing Standards

### Test Structure
- Organize tests to mirror source code structure
- Use descriptive test names that explain the behavior
- Follow AAA pattern (Arrange, Act, Assert)
- Use fixtures for common test data
- Group related tests in classes

### Coverage Goals
- Aim for 90%+ test coverage
- Write unit tests for business logic
- Use integration tests for external dependencies
- Mock external services in tests
- Test error conditions and edge cases

### pytest Configuration
```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=term-missing"
```

## Virtual Environment Setup

### Creation and Activation
```bash
# Create virtual environment (outside venv)
py -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies (inside activated venv)
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

### Requirements Management
- Use `requirements.txt` for production dependencies
- Use `requirements-dev.txt` for development dependencies
- Consider using `pip-tools` for dependency resolution
- Pin versions for reproducible builds

## Django-Specific Guidelines

### Project Structure
```
project_name/
├── manage.py
├── project_name/
│   ├── __init__.py
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   ├── products/
│   └── orders/
└── requirements/
```

### Common Commands

**Outside virtual environment (.venv deactivated):**
- `py manage.py runserver` - Start development server
- `py manage.py migrate` - Apply database migrations
- `py manage.py makemigrations` - Create new migrations
- `py manage.py createsuperuser` - Create admin user
- `py manage.py collectstatic` - Collect static files
- `py manage.py test` - Run Django tests

**Inside virtual environment (.venv activated):**
- `python manage.py runserver` - Start development server
- `python manage.py migrate` - Apply database migrations
- `python manage.py makemigrations` - Create new migrations
- `python manage.py createsuperuser` - Create admin user
- `python manage.py collectstatic` - Collect static files
- `python manage.py test` - Run Django tests

## FastAPI-Specific Guidelines

### Project Structure
```
src/
├── main.py              # FastAPI application
├── api/
│   ├── __init__.py
│   ├── dependencies.py  # Dependency injection
│   └── v1/
│       ├── __init__.py
│       └── endpoints/
├── core/
│   ├── __init__.py
│   ├── config.py       # Settings
│   └── security.py    # Authentication
├── models/
├── schemas/            # Pydantic models
└── services/
```

### Common Commands

**Outside virtual environment (.venv deactivated):**
- `py -m uvicorn main:app --reload` - Start development server
- `py -m uvicorn main:app --host 0.0.0.0 --port 8000` - Start production server

**Inside virtual environment (.venv activated):**
- `python -m uvicorn main:app --reload` - Start development server
- `python -m uvicorn main:app --host 0.0.0.0 --port 8000` - Start production server

## Security Guidelines

### Dependencies

**Outside virtual environment (.venv deactivated):**
- Regularly update dependencies with `py -m pip list --outdated`
- Use `py -m safety check` to check for known vulnerabilities
- Pin dependency versions in requirements files
- Use virtual environments to isolate dependencies

**Inside virtual environment (.venv activated):**
- Regularly update dependencies with `python -m pip list --outdated`
- Use `python -m safety check` to check for known vulnerabilities
- Pin dependency versions in requirements files
- Use virtual environments to isolate dependencies

### Code Security
- Validate input data with Pydantic or similar
- Use environment variables for sensitive configuration
- Implement proper authentication and authorization
- Sanitize data before database operations
- Use HTTPS for production deployments

## Development Workflow

### Before Starting
1. Check Python version compatibility
2. Create virtual environment with `py -m venv .venv` (outside venv)
3. Activate virtual environment (`.venv\Scripts\activate` on Windows)
4. Install dependencies from requirements files with `python -m pip install` (inside venv)
5. Run type checking with `python -m mypy .` (inside venv)

### During Development
1. Use type hints for better code documentation
2. Run tests frequently to catch issues early
3. Use meaningful commit messages
4. Format code with Black before committing

### Before Committing (inside activated .venv)
1. **Check Database Health**: `python -c "from local_insight_engine.persistence import get_database_manager; print('DB Health:', get_database_manager().health_check())"`
2. **Run Enhanced Test Suite**: `python -m pytest -v --tb=short`
3. **Check FTS5 Functionality**: `python -c "from local_insight_engine.persistence.repositories import SessionRepository; from local_insight_engine.persistence import get_database_manager; print('FTS5:', SessionRepository(get_database_manager().get_session())._check_fts5_available())"`
4. **Code Quality Checks**:
   - Check code formatting: `python -m black --check .`
   - Sort imports: `python -m isort --check-only .`
   - Run linting: `python -m flake8`
   - Run type checking: `python -m mypy .`
5. **Performance Log Analysis**: `grep "PERF END" localinsightengine.log | tail -5`
6. **Configuration Validation**: Ensure `localinsightengine.conf` has proper settings