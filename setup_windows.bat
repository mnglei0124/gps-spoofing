@echo off
title GPS Spoofer Setup - Windows
echo ==========================================
echo       GPS Spoofer Setup Utility
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! 
    echo Please install Python from https://www.python.org/ and ensure "Add Python to PATH" is checked.
    pause
    exit /b
)

echo [1/2] Upgrading pip...
python -m pip install --upgrade pip

echo [2/2] Installing requirements...
pip install -r requirements.txt

echo.
echo ==========================================
echo SUCCESS: Environment is ready!
echo ==========================================
echo.
echo Use "python spoof.py --help" to get started.
pause
