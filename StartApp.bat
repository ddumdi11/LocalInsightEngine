@echo off
rem LocalInsightEngine v0.1.1 - GUI Launcher
rem Copyright-compliant document analysis with Q&A functionality
rem
rem This script launches the graphical user interface for LocalInsightEngine
rem Features: File selection, analysis actions, interactive Q&A, export functionality

setlocal enabledelayedexpansion

rem Change to script directory to ensure relative paths work regardless of invocation location
pushd "%~dp0"

echo [GUI] LocalInsightEngine v0.1.1 - Starting GUI Application...

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

rem Check if tkinter is available
python -c "import tkinter; print('[CHECK] tkinter available')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] tkinter not available! GUI cannot start.
    echo.
    echo tkinter should be included with Python by default.
    echo If you're using a custom Python installation, you may need to install tkinter separately.
    echo.
    pause
    exit /b 1
)

rem Set PYTHONPATH to include src directory (now relative to script directory)
set PYTHONPATH=%~dp0src;%PYTHONPATH%

echo [START] Launching LocalInsightEngine GUI...
echo [INFO] Features available:
echo   - Document analysis (PDF, TXT, EPUB, DOCX)
echo   - Interactive Q^&A about your documents
echo   - Export to JSON format
echo   - Test suite execution
echo.

rem Launch GUI application
python -m local_insight_engine.gui.main_window

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] GUI application failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] GUI application closed successfully!

rem Restore original directory
popd

pause