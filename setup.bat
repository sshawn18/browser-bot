@echo off
echo === Browser Bot — One-time Setup ===
echo.

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Install from https://python.org then re-run this.
    pause & exit /b 1
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Installing dependencies...
venv\Scripts\pip install -r requirements.txt --quiet

echo.
echo Done! Opening Claude Code to complete setup...
echo Claude will walk you through the Telegram bot configuration.
echo.
claude .
