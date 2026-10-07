@echo off
setlocal enabledelayedexpansion
title GPS Spoofer Setup - Windows

:: Change to the directory where the script is located
cd /d "%~dp0"

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
    exit /b 1
)

echo [1/2] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip. Continuing with current version...
)

echo [2/2] Installing requirements...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ==========================================
    echo FAILED: Could not install requirements.
    echo Please check your internet connection or Python installation.
    echo ==========================================
    pause
    exit /b 1
)

echo.
echo ==========================================
echo SUCCESS: Environment is ready!
echo ==========================================
echo.
echo Use "python spoof.py --help" to get started.
pause
