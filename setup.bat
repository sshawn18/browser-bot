@echo off
echo === Browser Bot Setup ===
echo.

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Install from https://python.org
    pause & exit /b 1
)

if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

if not exist .env (
    copy .env.example .env >nul
    echo Created .env — fill in your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
)

echo.
echo Done! Edit .env then you're ready.
pause
