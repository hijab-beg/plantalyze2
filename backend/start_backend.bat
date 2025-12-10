@echo off
REM Plantalyze Backend Startup Script for Windows

echo ====================================
echo Starting Plantalyze Backend Server
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/Update dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Check if model files exist
if not exist "unet_model.h5" (
    echo WARNING: unet_model.h5 not found in backend directory!
    echo Please copy your UNet model file to the backend folder.
    echo.
)

if not exist "Best_ShuffleNet_Model.pth" (
    echo WARNING: Best_ShuffleNet_Model.pth not found in backend directory!
    echo Please copy your ShuffleNet model file to the backend folder.
    echo.
)

REM Start Flask server
echo ====================================
echo Starting Flask server on port 5000...
echo Press Ctrl+C to stop the server
echo ====================================
echo.

python app.py

REM If server stops
echo.
echo Server stopped.
pause
