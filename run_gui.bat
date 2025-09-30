@echo off
REM Video CLI GUI Launcher for Windows
REM This script activates the virtual environment and launches the GUI

echo Starting Video CLI GUI...

REM Check if we're in the right directory
if not exist "src\video_cli" (
    echo Error: Please run this script from the Video AI project directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Error: Virtual environment not found. Please run the setup first.
    echo Run: python -m venv .venv
    echo Then: .venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment and run GUI
.venv\Scripts\python.exe gui.py

if errorlevel 1 (
    echo.
    echo An error occurred while running the GUI.
    pause
)