@echo off
REM Data Intelligence Suite - Backend Setup for Windows

echo.
echo ========================================
echo Data Intelligence Suite - Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+ from python.org
    pause
    exit /b 1
)

echo ✓ Python found
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo ERROR: Failed to create venv
    pause
    exit /b 1
)

echo ✓ Virtual environment created
echo.

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)

echo ✓ Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ Setup Complete!
echo ========================================
echo.
echo To start the backend:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: python main.py
echo.
echo Server will run on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
pause
