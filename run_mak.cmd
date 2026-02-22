@echo off
setlocal
echo Starting SAHelper setup and launch...

:: Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Creating .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment. Ensure Python is installed.
        pause
        exit /b %errorlevel%
    )
)

set PYTHON_EXE=.venv\Scripts\python.exe

:: Install/Update requirements
echo Installing/Updating dependencies in .venv...
%PYTHON_EXE% -m pip install -r requirements.txt --quiet

:: Install Playwright browsers
echo Ensuring Playwright Chromium is installed...
%PYTHON_EXE% -m playwright install chromium

:: Run the application
echo Launching SAHelper (Enterprise Edition)...
%PYTHON_EXE% -m sahelper.main

if %errorlevel% neq 0 (
    echo Application exited with error code %errorlevel%.
    pause
)
endlocal
