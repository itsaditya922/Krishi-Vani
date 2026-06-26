#!/bin/bash
# KrishiVani Quick Setup Script for macOS/Linux
# This script sets up the development environment automatically

set -e  # Exit on error

echo ""
echo "======================================"
echo "  KrishiVani Setup - macOS/Linux"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install it using: brew install python3 (macOS) or apt-get install python3 (Linux)"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Found: $PYTHON_VERSION"

echo "[1/5] Creating virtual environment..."
python3 -m venv .venv

echo "[2/5] Activating virtual environment..."
source .venv/bin/activate

echo "[3/5] Upgrading pip..."
python -m pip install --upgrade pip -q

echo "[4/5] Installing dependencies..."
if pip install -r requirements.txt; then
    echo "✓ Dependencies installed"
else
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[5/5] Setting up environment..."
if [ -f .env ]; then
    echo ".env file already exists - skipping creation"
else
    echo "Creating .env.example template..."
    if [ -f .env.example ]; then
        cp .env.example .env
    fi
    
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your API credentials"
    echo ""
    echo "Required:"
    echo "  - TELEGRAM_BOT_TOKEN (from @BotFather on Telegram)"
    echo "  - GROQ_API_KEY (from console.groq.com)"
    echo ""
fi

echo ""
echo "======================================"
echo "  Setup Complete! ✓"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API credentials"
echo "  2. Run Telegram bot:    python telegram_app.py"
echo "  3. Run WhatsApp server: python twilio_app.py"
echo ""
echo "Activate environment later:"
echo "  source .venv/bin/activate"
echo ""
