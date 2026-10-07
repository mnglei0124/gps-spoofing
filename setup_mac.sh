#!/usr/bin/env bash
set -e

# Run from the directory this script lives in
cd "$(dirname "$0")"

echo "=========================================="
echo "      GPS Spoofer Setup Utility (macOS)"
echo "=========================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 not found!"
    echo "Install it with Homebrew (brew install python) or from https://www.python.org/"
    exit 1
fi

echo "[1/3] Creating virtual environment (.venv)..."
python3 -m venv .venv

echo "[2/3] Upgrading pip..."
.venv/bin/python -m pip install --upgrade pip || echo "[WARNING] Failed to upgrade pip. Continuing..."

echo "[3/3] Installing requirements..."
.venv/bin/python -m pip install -r requirements.txt

echo
echo "=========================================="
echo "SUCCESS: Environment is ready!"
echo "=========================================="
echo
echo "Activate it with:  source .venv/bin/activate"
echo "Then run:          python spoof.py --help"
