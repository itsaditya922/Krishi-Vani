@echo off
REM KrishiVani Quick Setup Script for Windows
REM This script sets up the development environment automatically

echo.
echo ======================================
echo   KrishiVani Setup - Windows
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [5/5] Setting up environment...
if exist .env (
    echo .env file already exists - skipping creation
) else (
    echo Creating .env.example template...
    copy .env.example .env >nul
    echo.
    echo ⚠️  IMPORTANT: Edit .env file with your API credentials
    echo.
    echo Required:
    echo   - TELEGRAM_BOT_TOKEN (from @BotFather on Telegram)
    echo   - GROQ_API_KEY (from console.groq.com)
    echo.
)

echo.
echo ======================================
echo   Setup Complete! ✓
echo ======================================
echo.
echo Next steps:
echo   1. Edit .env with your API credentials
echo   2. Run Telegram bot:    python telegram_app.py
echo   3. Run WhatsApp server: python twilio_app.py
echo.
echo Activate environment later:
echo   .venv\Scripts\activate
echo.
pause
