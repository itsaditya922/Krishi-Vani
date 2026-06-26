# KrishiVani - Setup Guide

KrishiVani is an AI-powered agriculture assistant that provides crop disease diagnosis, farming advice, and multilingual voice support through Telegram and WhatsApp.

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/KrishiVani.git
cd KrishiVani
```

### 2. Create Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with your API credentials:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Groq API (for LLM)
GROQ_API_KEY=your_groq_api_key_here

# Twilio/WhatsApp (optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# ngrok URL (for WhatsApp webhooks)
NGROK_URL=https://your-ngrok-url.io
```

### How to Get API Keys

#### Telegram Bot Token
1. Chat with [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command to create a bot
3. Copy the bot token provided

#### Groq API Key
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Generate an API key from the API Keys section
4. Copy your key to `.env`

#### Twilio WhatsApp (optional)
1. Create account at [twilio.com](https://www.twilio.com)
2. Get your Account SID and Auth Token
3. Set up WhatsApp integration
4. For webhooks, use [ngrok](https://ngrok.com) to create a public URL

## Running the Application

### Run Telegram Bot

```bash
python telegram_app.py
```

The bot will start polling Telegram servers. You can now message your bot on Telegram.

### Run WhatsApp Server

```bash
python twilio_app.py
```

The Flask server will start on `http://127.0.0.1:5000`. The webhook endpoint is at `/webhook`.

### Run Both Simultaneously

Open two separate terminal windows in the project directory:

**Terminal 1 (Telegram Bot):**
```bash
.venv\Scripts\Activate  # or: source .venv/bin/activate
python telegram_app.py
```

**Terminal 2 (WhatsApp Server):**
```bash
.venv\Scripts\Activate  # or: source .venv/bin/activate
python twilio_app.py
```

## Project Structure

```
KrishiVani/
├── telegram_app.py          # Telegram bot application
├── twilio_app.py            # Twilio/WhatsApp server
├── core/
│   ├── __init__.py          # Package exports
│   ├── agent.py             # AI agent for farming advice
│   ├── audio.py             # Audio transcription & TTS
│   ├── model.py             # Crop disease prediction
│   └── media.py             # Media utilities
├── tests/
│   └── test_pipeline.py     # Example test pipeline
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── .gitignore               # Git ignore patterns
└── readme.md                # Project overview
```

## Usage

### Telegram Bot

1. Find your bot on Telegram using the username from BotFather
2. Send `/start` to initiate
3. You can:
   - Send crop photos for disease diagnosis
   - Send voice notes for advice in your language
   - Ask questions in Hindi or English

### WhatsApp Bot

1. Configure Twilio webhook to point to `http://your-ngrok-url.io/webhook`
2. Send messages to your WhatsApp bot number
3. Same functionality as Telegram

## Features

✅ **Crop Disease Detection** - Upload photos, get AI-powered disease identification
✅ **Multilingual Support** - Hindi & English for text and voice
✅ **Voice I/O** - Send voice notes, receive voice replies
✅ **Farming Advice** - Get expert agriculture recommendations
✅ **Multiple Platforms** - Telegram & WhatsApp integration

## Troubleshooting

### "No module named 'flask'" error
- Ensure you've activated the virtual environment
- Run: `pip install -r requirements.txt`

### "TELEGRAM_BOT_TOKEN not found" error
- Create `.env` file in project root
- Add your token: `TELEGRAM_BOT_TOKEN=your_token_here`

### Flask server won't start on port 5000
- Check if port 5000 is in use: `netstat -ano | findstr :5000` (Windows)
- Use different port in `twilio_app.py`: Change `port=5000` to `port=5001`

### WhatsApp messages not received
- Ensure ngrok tunnel is running
- Update Twilio webhook URL to your current ngrok URL
- Check Twilio logs for errors

## Testing

Run the test pipeline to verify setup:

```bash
python tests/test_pipeline.py
```

This will test language detection, QA, and text-to-speech functions.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

## License

This project is open source. See LICENSE file for details.

## Support

For issues or questions:
- Create an issue on GitHub
- Check existing documentation
- Review error logs in console output

## Dependencies

Main packages used:
- **Flask** - Web framework for WhatsApp server
- **python-telegram-bot** - Telegram API wrapper
- **Twilio** - WhatsApp/SMS integration
- **Groq** - LLM API for AI advice
- **transformers** - Hugging Face model library
- **gTTS** - Google Text-to-Speech
- **Pillow** - Image processing

See `requirements.txt` for complete list with versions.
