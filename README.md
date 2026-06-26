# 🌱 KrishiVani

> **An AI-powered multilingual agriculture assistant for Indian farmers.**

KrishiVani helps farmers diagnose crop diseases and receive instant agricultural guidance through **Telegram** and **WhatsApp**. The assistant supports **text, voice, and image inputs**, making expert farming advice accessible in both **Hindi** and **English**.

---

## 📌 Features

* 🌾 AI-based crop disease detection from leaf images
* 📷 Image upload for disease diagnosis
* 🎙️ Voice-to-voice conversation using speech recognition and text-to-speech
* 💬 AI-powered agricultural question answering
* 🌐 Multilingual support (Hindi & English)
* 📱 Telegram Bot integration
* 📲 WhatsApp integration using Twilio
* ⚡ Fast responses powered by Groq LLM

---

## 🛠️ Tech Stack

* **Python**
* **Flask**
* **PyTorch**
* **Hugging Face Transformers**
* **Groq API**

  * Llama 3.1 8B Instant
  * Whisper Large V3 Turbo
* **gTTS**
* **Telegram Bot API**
* **Twilio WhatsApp API**

---

## 📂 Project Structure

```text
KrishiVani/
│
├── telegram_app.py          # Telegram bot
├── twilio_app.py            # WhatsApp webhook
│
├── core/
│   ├── agent.py             # AI advisory system
│   ├── audio.py             # Speech-to-text & text-to-speech
│   ├── model.py             # Crop disease prediction
│   ├── media.py
│   └── __init__.py
│
├── tests/
│   └── test_pipeline.py
│
├── uploads/
├── requirements.txt
├── .env
└── README.md
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/KrishiVani.git
cd KrishiVani
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key

TELEGRAM_BOT_TOKEN=your_telegram_bot_token

TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

NGROK_URL=https://your-ngrok-url
```

---

## ▶️ Running the Application

### Telegram Bot

```bash
python telegram_app.py
```

### WhatsApp Server

```bash
python twilio_app.py
```

---

## 🔄 Workflow

1. Farmer sends a **crop image**, **voice message**, or **text query**.
2. Voice messages are transcribed using **Whisper Large V3 Turbo**.
3. Crop images are analyzed using a fine-tuned **MobileNetV2** disease classification model.
4. **Llama 3.1** generates treatment recommendations and prevention advice.
5. The response is returned in the user's preferred language as **text** or **voice**.

---

## 🤖 AI Models

| Component          | Model                                           |
| ------------------ | ----------------------------------------------- |
| Disease Detection  | `sanjeevani-04/indian-crop-disease-mobilenetv2` |
| Speech Recognition | `Whisper Large V3 Turbo`                        |
| Language Model     | `Llama 3.1 8B Instant`                          |
| Text-to-Speech     | Google Text-to-Speech (gTTS)                    |

---

## 🌍 Supported Languages

* 🇮🇳 Hindi
* 🇬🇧 English

---

## 🎯 Use Cases

* Crop disease identification
* Treatment and prevention recommendations
* Farming-related question answering
* Voice-based agricultural assistance
* Multilingual support for rural farmers

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Authors

Developed as an AI-powered agriculture assistant to improve crop health monitoring and provide accessible, multilingual farming guidance for Indian farmers.

---

### ⭐ If you found this project useful, consider giving it a star on GitHub!
