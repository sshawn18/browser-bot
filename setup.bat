@echo off
echo ============================================
echo  Browser Bot - One-Time Setup
echo ============================================
echo.

REM Check Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found.
    echo Please install Python 3.11+ from https://python.org
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Found Python %PYVER%
echo.

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Done.
) else (
    echo Virtual environment already exists, skipping.
)

echo.
echo Installing Python packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install packages.
    pause
    exit /b 1
)

echo.
echo Installing Playwright Chromium browser...
python -m playwright install chromium
if %ERRORLEVEL% neq 0 (
    echo ERROR: Playwright install failed.
    pause
    exit /b 1
)

REM Copy .env.example to .env if not already present
if not exist .env (
    copy .env.example .env >nul
    echo.
    echo Created .env from template.
)

echo.
echo ============================================
echo  Setup complete!
echo ============================================
echo.
echo Next steps:
echo   1. Edit .env and fill in your credentials
echo   2. Double-click start_chrome.bat
echo   3. Run: venv\Scripts\python.exe bot.py
echo.
pause
