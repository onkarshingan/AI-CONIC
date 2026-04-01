@echo off
:: ─────────────────────────────────────────────────────────────
::  AI Smart Attendance System – Quick Launcher (Windows)
:: ─────────────────────────────────────────────────────────────

echo.
echo   AI Smart Attendance System
echo   ──────────────────────────

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python not found. Install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Create venv if missing
if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)

:: Activate
call venv\Scripts\activate.bat

:: Install deps if flask missing
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo   Installing core dependencies...
    pip install flask pandas openpyxl numpy Pillow -q
)

:: Run setup
python setup.py

:: Start server
echo.
echo   Starting server at http://127.0.0.1:5000
echo   Press Ctrl+C to stop.
echo.
python app.py
pause
