# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview: LocalInsightEngine

This is a **LocalInsightEngine** - a sophisticated Python application for copyright-compliant document analysis using large language models. The project implements a 3-layer architecture:

1. **Layer 1 (data_layer)**: PDF/EPUB/DOCX parsing with precise location mapping
2. **Layer 2 (processing_hub)**: Text processing, NER, and content neutralization  
3. **Layer 3 (analysis_engine)**: LLM-based analysis of neutralized content

**Key Constraint: Copyright Compliance** - Original text must NEVER be sent to external APIs. Only neutralized, processed content is transmitted.

The project uses industry-standard tools and follows best practices for scalable application development.

## LocalInsightEngine Specific Commands

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

### Running the Engine
```python
from local_insight_engine.main import LocalInsightEngine
engine = LocalInsightEngine()
results = engine.analyze_document(Path("document.pdf"))
```

### Key Architecture Rules
1. **Never modify Layer 1** to send original text externally
2. **Always neutralize in Layer 2** before sending to Layer 3  
3. **Test copyright compliance** - no original text should appear in Layer 3 calls
4. **Use type hints** throughout - this is a typed Python project
5. **Follow the 3-layer pattern** - don't bypass layers
6. **File Type Validation** - system detects actual content type vs extension
7. **Multi-Format Support** - TXT preferred over PDF for better quality
8. **Claude-4 Integration** - uses latest model: claude-sonnet-4-20250514

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
```
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
```python
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
1. Run full test suite: `python -m pytest`
2. Check code formatting: `python -m black --check .`
3. Sort imports: `python -m isort --check-only .`
4. Run linting: `python -m flake8`
5. Run type checking: `python -m mypy .`