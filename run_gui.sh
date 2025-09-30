#!/bin/bash
# Video CLI GUI Launcher for Unix-like systems
# This script activates the virtual environment and launches the GUI

echo "Starting Video CLI GUI..."

# Check if we're in the right directory
if [ ! -d "src/video_cli" ]; then
    echo "Error: Please run this script from the Video AI project directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run the setup first."
    echo "Run: python -m venv .venv"
    echo "Then: source .venv/bin/activate"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run GUI
.venv/bin/python gui.py