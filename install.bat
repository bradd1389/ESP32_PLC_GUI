@echo off
REM Installation script for ESP32 PLC GUI (Windows)
REM This script sets up the development environment

echo ESP32 PLC GUI - Installation Script
echo ===================================

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://python.org
    pause
    exit /b 1
)

python --version
echo Checking Python version compatibility...
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3.11 or higher is required
    pause
    exit /b 1
)
echo ✓ Python version is compatible

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo To run the application:
echo   1. Activate virtual environment: .venv\Scripts\activate
echo   2. Run the application: python Main.py
echo.
echo For more information, see README.md
pause
