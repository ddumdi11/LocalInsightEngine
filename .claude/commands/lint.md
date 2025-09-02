# Python Linter

Run Python code linting and formatting tools.

## Purpose

This command helps you maintain code quality using Python's best linting and formatting tools.

## Usage

```
/lint
```

## What this command does

1. **Runs multiple linters** (flake8, pylint, black, isort)
2. **Provides detailed feedback** on code quality issues
3. **Auto-fixes formatting** where possible
4. **Checks type hints** if mypy is configured

## Example Commands

### Black (code formatting)
```bash
# Format all Python files
py -m black .

# Check formatting without changing files
py -m black --check .

# Format specific file
py -m black src/main.py
```

### flake8 (style guide enforcement)
```bash
# Check all Python files
py -m flake8 .

# Check specific directory
py -m flake8 src/

# Check with specific rules
py -m flake8 --max-line-length=88 .
```

### isort (import sorting)
```bash
# Sort imports in all files
py -m isort .

# Check import sorting
py -m isort --check-only .

# Sort imports in specific file
py -m isort src/main.py
```

### pylint (comprehensive linting)
```bash
# Run pylint on all files
py -m pylint src/

# Run with specific score threshold
py -m pylint --fail-under=8.0 src/

# Generate detailed report
py -m pylint --output-format=html src/ > pylint_report.html
```

### mypy (type checking)
```bash
# Check types in all files
py -m mypy .

# Check specific module
py -m mypy src/models.py

# Check with strict mode
py -m mypy --strict src/
```

## Configuration Files

Most projects benefit from configuration files:

### .flake8
```ini
[flake8]
max-line-length = 88
exclude = .git,__pycache__,venv
ignore = E203,W503
```

### pyproject.toml
```toml
[tool.black]
line-length = 88

[tool.isort]
profile = "black"
```

## Best Practices

- Run linters before committing code
- Use consistent formatting across the project
- Fix linting issues promptly
- Configure linters to match your team's style
- Use type hints for better code documentation