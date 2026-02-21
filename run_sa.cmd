@echo off
echo Starting SAHelper setup and launch...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b %errorlevel%
)

:: Install requirements
echo Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt --quiet

:: Install Playwright browsers
echo Ensuring Playwright Chromium is installed...
python -m playwright install chromium

:: Run the application
echo Launching SAHelper (Enterprise Edition)...
python -m sahelper.main

if %errorlevel% neq 0 (
    echo Application exited with error code %errorlevel%.
    pause
)
