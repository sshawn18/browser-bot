@echo off
echo ============================================
echo  Starting Chrome with Remote Debugging
echo ============================================
echo.

REM Try standard Chrome install location first
set CHROME_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe
if not exist "%CHROME_EXE%" (
    set CHROME_EXE=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
)
if not exist "%CHROME_EXE%" (
    echo ERROR: Chrome not found at standard locations.
    echo Please edit this file and set CHROME_EXE to your Chrome path.
    pause
    exit /b 1
)

echo Starting Chrome with remote debugging on port 9222...
echo Your existing profile and logins will be preserved.
echo.

start "" "%CHROME_EXE%" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data" ^
  --no-first-run ^
  --no-default-browser-check

echo Chrome started!
echo.
echo You can now run: python bot.py
echo.
pause
