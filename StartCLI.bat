@echo off
rem LocalInsightEngine v0.1.0 - Start Script
rem Copyright-compliant document analysis with 3-layer architecture
rem
rem Usage:
rem   Start.bat                             - Show help
rem   Start.bat document.pdf                - Analyze document 
rem   Start.bat document.pdf --export       - Analyze and export to JSON
rem   Start.bat document.pdf --export --format json --output results - Custom export
rem   Start.bat --version                   - Show version info
rem   Start.bat --test                      - Run quick test suite

setlocal enabledelayedexpansion

rem Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   py -m venv .venv
    echo   .venv\Scripts\activate
    echo   python -m pip install -r requirements-dev.txt
    echo   python -m spacy download de_core_news_sm
    echo.
    pause
    exit /b 1
)

rem Activate virtual environment
echo [INIT] Activating virtual environment...
call .venv\Scripts\activate.bat

rem Handle special commands
if "%1"=="--version" (
    echo LocalInsightEngine v0.1.0
    echo Copyright-compliant document analysis
    python -m local_insight_engine.main --version
    goto end
)

if "%1"=="--test" (
    echo [TEST] Running quick multi-format test...
    python tests/test_multiformat.py
    goto end
)

if "%1"=="--help" (
    goto help
)

rem Check if document path provided
if "%1"=="" (
    goto help
)

rem Check if file exists
if not exist "%1" (
    echo [ERROR] Document not found: %1
    echo.
    echo Please provide a valid path to a PDF, TXT, EPUB, or DOCX file.
    echo.
    pause
    exit /b 1
)

rem Run analysis with all parameters
echo [START] LocalInsightEngine v0.1.0
echo [INFO] Analyzing document: %1

rem Check if export parameters are present
set EXPORT_INFO=
if "%2"=="--export" (
    set EXPORT_INFO=with JSON export
)
if not "%EXPORT_INFO%"=="" (
    echo [INFO] Export enabled %EXPORT_INFO%
)
echo.

rem Set PYTHONPATH to include src directory and run analysis
set PYTHONPATH=%CD%\src;%PYTHONPATH%
python -m local_insight_engine.main %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Analysis failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] Analysis completed!
goto end

:help
echo LocalInsightEngine v0.1.0 - Copyright-compliant document analysis
echo.
echo Usage:
echo   Start.bat document.pdf                           Analyze a document
echo   Start.bat document.pdf --export                  Analyze and export to JSON
echo   Start.bat document.pdf --export --output results Export with custom output path
echo   Start.bat --version                              Show version information  
echo   Start.bat --test                                 Run quick test suite
echo   Start.bat --help                                 Show this help
echo.
echo Supported formats: PDF, TXT, EPUB, DOCX
echo Export formats: JSON (CSV, PDF coming in v0.2.0)
echo.
echo Examples:
echo   Start.bat example.pdf
echo   Start.bat example.pdf --export
echo   Start.bat "C:\Documents\My Book.txt" --export --output "C:\Results\analysis"
echo   Start.bat research.epub --export
echo.

:end
pause