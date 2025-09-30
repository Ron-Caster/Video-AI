#!/bin/bash
echo "Starting Advanced Video Editor GUI..."
echo

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Using system Python..."
fi

# Install additional dependencies if needed
echo "Checking dependencies..."
python -c "import cv2, pygame, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing additional dependencies..."
    pip install -r app_gui_requirements.txt
fi

# Launch the application
echo "Launching Advanced Video Editor..."
python app_gui.py

if [ $? -ne 0 ]; then
    echo
    echo "Error occurred while running the application."
    echo "Please check the console output above for details."
    echo
    read -p "Press Enter to continue..."
fi