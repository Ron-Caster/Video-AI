@echo off
echo Starting Advanced Video Editor GUI...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Using system Python...
)

REM Install additional dependencies if needed
echo Checking dependencies...
python -c "import cv2, pygame, PIL" 2>nul
if errorlevel 1 (
    echo Installing additional dependencies...
    pip install -r app_gui_requirements.txt
)

REM Launch the application
echo Launching Advanced Video Editor...
python app_gui.py

if errorlevel 1 (
    echo.
    echo Error occurred while running the application.
    echo Please check the console output above for details.
    echo.
    pause
)