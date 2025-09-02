# Test Runner

Run Python tests with pytest, unittest, or other testing frameworks.

## Purpose

This command helps you run Python tests effectively with proper configuration and reporting.

## Usage

```
/test
```

## What this command does

1. **Detects test framework** (pytest, unittest, nose2)
2. **Runs appropriate tests** with proper configuration
3. **Provides coverage reporting** if available
4. **Shows clear test results** with failure details

## Example Commands

### pytest (recommended)
```bash
# Run all tests
py -m pytest

# Run with coverage
py -m pytest --cov=src --cov-report=html

# Run specific test file
py -m pytest tests/test_models.py

# Run with verbose output
py -m pytest -v

# Run tests matching pattern
py -m pytest -k "test_user"
```

### unittest
```bash
# Run all tests
py -m unittest discover

# Run specific test file
py -m unittest tests.test_models

# Run with verbose output
py -m unittest -v
```

### Django tests
```bash
# Run all Django tests
py manage.py test

# Run specific app tests
py manage.py test myapp

# Run with coverage
py -m coverage run --source='.' manage.py test
py -m coverage report
```

## Best Practices

- Write tests for all critical functionality
- Use descriptive test names
- Keep tests isolated and independent
- Mock external dependencies
- Aim for high test coverage (80%+)