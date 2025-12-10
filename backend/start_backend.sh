#!/bin/bash
# Plantalyze Backend Startup Script for Linux/Mac

echo "===================================="
echo "Starting Plantalyze Backend Server"
echo "===================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found!"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo
echo "Installing dependencies..."
pip install -r requirements.txt
echo

# Check if model files exist
if [ ! -f "unet_model.h5" ]; then
    echo "WARNING: unet_model.h5 not found in backend directory!"
    echo "Please copy your UNet model file to the backend folder."
    echo
fi

if [ ! -f "Best_ShuffleNet_Model.pth" ]; then
    echo "WARNING: Best_ShuffleNet_Model.pth not found in backend directory!"
    echo "Please copy your ShuffleNet model file to the backend folder."
    echo
fi

# Start Flask server
echo "===================================="
echo "Starting Flask server on port 5000..."
echo "Press Ctrl+C to stop the server"
echo "===================================="
echo

python app.py

# If server stops
echo
echo "Server stopped."
