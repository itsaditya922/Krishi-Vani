# KrishiVani

This repository contains the KrishiVani agriculture assistant application. The following files are included with their source code.

## telegram_app.py

Telegram bot integration

`python
import os
import tempfile
import base64
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from core.agent import *
from core.audio import *
from core.model import *

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs("uploads", exist_ok=True)  # Ensure uploads directory exists

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

#-------------------Welcome Message--------------------------------

def  get_welcome_message(lang_code: str)-> str:
    if lang_code == "hi":
        return (
            "नमस्ते! 🌱 मैं KrishiVani हूँ, आपका कृषि सहायक।\n\n"
            "आप यह कर सकते हैं:\n"
            "• फसल की फोटो भेजें → बीमारी पहचान\n"
            "• आवाज़ में सवाल पूछें → आवाज़ में जवाब\n"
            "• हिंदी या English में लिखें\n\n"
            "अपनी फसल की समस्या बताइए!"
        )
    return (
        "Hello! 🌱 I am KrishiVani, your agriculture helper.\n\n"
        "You can:\n"
        "• Send a crop photo → get disease diagnosis\n"
        "• Send a voice note → get voice reply\n"
        "• Ask in Hindi or English\n\n"
        "Tell me about your crop problem!"
    )

def is_greeting(text: str)-> bool:
    greetings = {
        "hi", "hello", "hey", "helo", "start",
        "नमस्ते", "नमस्कार", "हेलो", "हाय",
        "sat sri akal", "good morning", "good evening"
    }
    return text.lower().strip() in greetings


#----------------------Telegram Bot Handlers------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start command handler."""
    await update.message.reply_text(get_welcome_message("en"))


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    user_text = update.message.text.strip()
    lang_code = detect_language(user_text)

    logger.info(f"Text: '{user_text}' | Lang: {lang_code}")

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    if is_greeting(user_text):
        reply = get_welcome_message(lang_code)
    else:
        reply = answer_general_question(user_text, language_code=lang_code)

    await update.message.reply_text(reply)


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle crop photos — run disease detection."""
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    logger.info("Image received, running disease detection...")

    # Download image from Telegram
    photo   = update.message.photo[-1]   # get highest resolution
    file    = await context.bot.get_file(photo.file_id)

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".jpg", dir="uploads"
    )
    await file.download_to_drive(tmp.name)
    tmp.close()

    # Run disease detection
    predictions = predict_disease(tmp.name)
    top         = predictions[0]
    cleanup_audio_files(tmp.name)

    logger.info(f"Detected: {top['disease']} ({top['confidence']:.0%})")

    # Get language from caption if provided
    caption   = update.message.caption or ""
    lang_code = detect_language(caption) if caption else "en"

    reply = get_advice(
        disease_label  = top["disease"],
        confidence     = top["confidence"],
        transcript     = caption,
        reply_language = lang_code
    )
    

    await update.message.reply_text(reply)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice notes — transcribe and reply with voice."""
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="record_voice"
    )

    logger.info("Voice note received...")

    # Get voice note file
    voice = update.message.voice or update.message.audio
    file  = await context.bot.get_file(voice.file_id)

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".ogg", dir="uploads"
    )
    await file.download_to_drive(tmp.name)
    tmp.close()

    # Validate
    is_valid, error_msg = validate_audio(tmp.name)
    if not is_valid:
        cleanup_audio_files(tmp.name)
        await update.message.reply_text(f"Voice note error: {error_msg}")
        return

    # Transcribe
    transcript, lang_code = transcribe_audio(tmp.name)
    cleanup_audio_files(tmp.name)

    logger.info(f"Transcript: '{transcript}' | Lang: {lang_code}")

    if not transcript.strip():
        await update.message.reply_text(get_welcome_message(lang_code))
        return

    # Generate text reply
    reply_text = answer_general_question(transcript, language_code=lang_code)

    # Convert to voice
    audio_path = text_to_audio(reply_text, lang_code)

    # Send voice reply
    with open(audio_path, "rb") as audio_file:
        await update.message.reply_voice(voice=audio_file)

    # Also send text version
    await update.message.reply_text(reply_text)

    cleanup_audio_files(audio_path)


async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stickers, documents, locations etc."""
    await update.message.reply_text(
        "कृपया फोटो, आवाज़ या टेक्स्ट भेजें। 🌱\n"
        "Please send a photo, voice note, or text.")
    


#----------------------Main Function------------------------------
def main():
    print("🚀 Starting KrishiVani Telegram bot...")

    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO,   handle_image))
    app.add_handler(MessageHandler(filters.VOICE,   handle_audio))
    app.add_handler(MessageHandler(filters.AUDIO,   handle_audio))
    app.add_handler(MessageHandler(filters.ALL,     handle_unsupported))

    print("✅ KrishiVani bot is running! Open Telegram and message your bot.")
    print("Press Ctrl+C to stop.\n")

    # Start polling — no webhook, no ngrok needed
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
`

## twilio_app.py

Twilio/WhatsApp integration

`python
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os, requests, tempfile, time
from core.model import *
from core.agent import *
from core.audio import *

load_dotenv()
app = Flask(__name__)

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")


def download_media(media_url: str, ext: str) -> str:
    """Download Twilio media to a temp file, return local path."""
    resp = requests.get(
        media_url,
        auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    )
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(resp.content)
    tmp.close()
    return tmp.name


def upload_audio_for_twilio(audio_path: str) -> str:
    filename = os.path.basename(audio_path)
    dest = os.path.join("uploads", filename)
    
    import shutil
    shutil.copy2(audio_path, dest)  # copy instead of rename — works across drives
    os.unlink(audio_path)           # then delete the original
    
    print(f"[DEBUG] File in uploads after move: {os.path.exists(dest)}")  # must be True
    
    ngrok_url = os.getenv("NGROK_URL", "").rstrip("/")
    return f"{ngrok_url}/audio/{filename}"


@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(                # ← was tempfile.gettempdir()
        os.path.join(os.getcwd(), "uploads"),  # ← now matches where the file actually is
        filename
    )


def send_whatsapp_audio(to: str, audio_url: str, caption: str = ""):
    """Send a WhatsApp audio message via Twilio."""

    message = twilio_client.messages.create(
        from_= TWILIO_NUMBER,
        to= to ,
        body=caption,
        media_url=[audio_url]
    )

    return message.sid


def cleanup(*paths):
    """Delete temporary files."""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.unlink(p)
        except Exception as e:
            pass
        
#-------------------------------------------------------------------
def get_welcome_message(lang_code: str) -> str:
    """Return welcome message based on detected language."""
    if lang_code == "hi":
        return (
            "नमस्ते! 🌱 मैं KrishiVani हूँ, आपका कृषि सहायक।\n\n"
            "आप यह कर सकते हैं:\n"
            "• फसल की फोटो भेजें → बीमारी पहचान\n"
            "• आवाज़ में सवाल पूछें → आवाज़ में जवाब\n"
            "• हिंदी या English में लिखें\n\n"
            "अपनी फसल की समस्या बताइए!"
        )
    else:
        return (
            "Hello! 🌱 I am KrishiVani, your agriculture helper.\n\n"
            "You can:\n"
            "• Send a crop photo → get disease diagnosis\n"
            "• Send a voice note → get voice reply\n"
            "• Ask in Hindi or English\n\n"
            "Tell me about your crop problem!"
        )


def is_greeting(text: str) -> bool:
    """Check if the message is a greeting."""
    greetings = {
        "hi", "hello", "hey", "helo",          # English
        "नमस्ते", "नमस्कार", "हेलो", "हाय",    # Hindi
        "sat sri akal", "jai hind",              # Regional
        "good morning", "good evening"
    }
    return text.lower().strip() in greetings





#------------------ Flask app routes ------------------
from flask import send_from_directory

@app.route("/")
def home():
    return "✅ KisanVoice server is running"




@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        num_media = int(request.form.get("NumMedia", 0))
        media_type = request.form.get("MediaContentType0", "")
        user_text = request.form.get("Body", "").strip()
        from_number = request.form.get("From")

        image_path = None
        audio_path = None
        transcript = ""
        lang_code = "en"
        is_audio_input = False

        if num_media > 0:
            media_url = request.form.get("MediaUrl0")
            if "image" in media_type:
                image_path = download_media(media_url, ".jpg")
            elif "audio" in media_type or "ogg" in media_type:
                audio_path = download_media(media_url, ".ogg")
                is_audio_input = True

        if is_audio_input and audio_path:
            transcript, lang_code = transcribe_audio(audio_path)
            cleanup(audio_path)
            if not user_text:
                user_text = transcript

        if user_text and not is_audio_input:
            lang_code = detect_language(user_text)

        if image_path:
            prediction = predict_disease(image_path)
            top = prediction[0]
            cleanup(image_path)
            reply_text = get_advice(
                disease_label=top["disease"],
                confidence=top["confidence"],
                transcript=user_text or transcript,
                reply_language=lang_code
            )
        elif user_text:
            if is_greeting(user_text):
                reply_text = get_welcome_message(lang_code)
            else:
                reply_text = answer_general_question(user_text, language_code=lang_code)
        else:
            reply_text = get_welcome_message("hi")



        twiml = MessagingResponse()

        if is_audio_input and reply_text:
            audio_reply_path = text_to_audio(reply_text, lang_code)
            print(f"[DEBUG] audio_reply_path: {audio_reply_path}")

            public_url = upload_audio_for_twilio(audio_reply_path)
            print(f"[DEBUG] public_url: {public_url}")
            import os
            print(f"[DEBUG] file exists: {os.path.exists('uploads/' + os.path.basename(audio_reply_path))}")
            sid = send_whatsapp_audio(to=from_number, audio_url=public_url, caption="🌱 KisanVoice")
            print(f"[DEBUG] Twilio SID: {sid}")
            print(f"[DEBUG] from={TWILIO_NUMBER}, to={from_number}")
            return str(twiml)
        else:
            twiml.message(reply_text)
            return str(twiml)

    except Exception as e:
        import traceback
        traceback.print_exc()  # ← THE REAL ERROR WILL APPEAR HERE
        return str(MessagingResponse()), 500
    
if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True, port=5000)
`

## core/__init__.py

Core package helpers and shared functions

`python
from .agent import get_advice, answer_general_question, detect_language
from .audio import transcribe_audio, text_to_audio
from .model import predict_disease

__all__ = ["get_advice", "answer_general_question", "detect_language", "transcribe_audio", "text_to_audio", "predict_disease"]
`

## core/agent.py

AI advice and question answering

`python
from groq import Groq
from dotenv import load_dotenv
from gtts import gTTS
from langdetect import detect
import os

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def detect_language(text: str) -> str:
    """Returns 'hi' for Hindi, 'en' for English, else 'hi' as default."""
    try:
        lang = detect(text)
        return lang if lang in ["hi", "en"] else "hi"
    except Exception:
        return "hi"
    
#---------------------------------------------------------------------------    

SYSTEM_PROMPT = """You are KisanVoice, an expert agricultural advisor for Indian farmers.
You have deep knowledge of crop diseases, organic and chemical treatments, 
Indian farming practices, seeds, fertilizers, weather, and market prices.

Rules:
- If the question is in Hindi → reply ONLY in Hindi (Devanagari script)
- If the question is in English → reply ONLY in English
- Maximum 120 words — this is a WhatsApp message
- Simple language, no technical jargon
- Mention cost in Indian Rupees whenever relevant
- Suggest  actions the farmer must take to treat/prevent the disease.
- End with ONE prevention tip
- Never mix Hindi and English in the same reply"""


def get_advice(disease_label: str, confidence: float, transcript: str ="", reply_language: str = "en")-> str:

    """Get advice from Groq based on the disease label, confidence, and farmer's question."""

    USER_PROMPT = f"""A farmer has a crop disease with {confidence:.2f}% confidence of being {disease_label}.
    The farmer's question is: "{transcript}".
    Write a WhatsApp advisory message in {reply_language} following format:
    Disease name with its prevention and treatment tips."""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",   # Fast + free on Groq
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ],
        max_tokens=200,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


def answer_general_question(user_text: str, language_code: str = "en")-> str:
    """Answer any farming question — not necessarily disease related."""
    lang_instruction = "reply in Hindi" if language_code == "hi" else "reply in English"

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{lang_instruction}. The farmer's question is: {user_text}"}
        ],
        max_tokens=200,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
`

## core/audio.py

Audio transcription, TTS, and validation

`python
#complete audio.py for Whisper transcription and gTTS

from transformers import pipeline
from gtts import gTTS
from .agent import detect_language
import os, tempfile
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB    = 25
MAX_DURATION_SEC    = 120
MIN_FILE_SIZE_BYTES = 500
SUPPORTED_FORMATS   = {".ogg", ".mp3", ".mp4", ".wav", ".m4a", ".mpeg", ".mpga", ".webm"}

from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # module level

def transcribe_audio(audio_path: str) -> tuple[str, str]:
    """
    Transcribe audio using Groq's Whisper API.
    Returns (transcript_text, detected_language_code).
    """
    with open(audio_path, "rb") as audio_file:
        transcription = groq_client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",  # fast + accurate + multilingual
            file=audio_file,
            response_format="json"
        )
    
    transcript = transcription.text.strip()
    language = detect_language(transcript)
    return transcript, language



def text_to_audio(text: str, lang_code: str, output_path: str | None = None):

    """
    Convert text to an MP3 file using gTTS.
    Returns path to the generated audio file.
    lang_code: 'hi' for Hindi, 'en' for English
    """

    if lang_code not in ['hi', 'en']:
        lang_code = 'hi'  # Default to Hindi if unsupported language code

    tts = gTTS(text=text, lang=lang_code, slow=False)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    tmp.close()
    return tmp.name




#---------------------------------------------------------------------
def validate_audio(audio_path: str, max_duration_seconds: int = MAX_DURATION_SEC) -> tuple[bool, str]:
    """Validate audio file before sending to Groq. Returns (is_valid, error_message)."""

    # File exists?
    if not audio_path or not os.path.exists(audio_path):
        return False, "Audio file not found"

    # Supported format?
    ext = Path(audio_path).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        return False, f"Unsupported format '{ext}'"

    # Not empty or corrupt?
    size_bytes = os.path.getsize(audio_path)
    if size_bytes < MIN_FILE_SIZE_BYTES:
        return False, "Audio file is empty or corrupt"

    # Under 25MB?
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"Voice note too large ({size_mb:.1f}MB). Max is {MAX_FILE_SIZE_MB}MB"

    # Duration check
    duration, error = _get_duration(audio_path, ext)
    if not error:
        if duration < 0.5:
            return False, "Voice note too short. Please speak a bit longer."
        if duration > max_duration_seconds:
            return False, f"Voice note too long ({duration:.0f}s). Max is {max_duration_seconds}s."

    logger.info(f"Audio valid | {ext} | {size_mb:.2f}MB | {duration:.1f}s")
    return True, ""


def _get_duration(audio_path: str, ext: str) -> tuple[float, str]:
    """Get audio duration in seconds using pydub."""
    try:
        from pydub import AudioSegment
        fmt_map = {
            ".ogg": "ogg", ".mp3": "mp3", ".mp4": "mp4",
            ".wav": "wav", ".m4a": "mp4", ".mpeg": "mp3",
            ".mpga": "mp3", ".webm": "webm"
        }
        audio = AudioSegment.from_file(audio_path, format=fmt_map.get(ext, ext.lstrip(".")))
        return len(audio) / 1000.0, ""
    except Exception as e:
        return 0.0, str(e)


def cleanup_audio_files(*paths: str) -> None:
    """Delete one or more temp files silently. Never raises."""
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            logger.warning(f"Could not delete {path}: {e}")


def get_audio_error_message(error: str, lang_code: str = "hi") -> str:
    """Return farmer-friendly error message in Hindi or English."""
    e = error.lower()
    if lang_code == "hi":
        if "not found"  in e: return "Voice note नहीं मिला। दोबारा भेजें। 🙏"
        if "large"      in e: return "Voice note बहुत बड़ा है। छोटा भेजें।"
        if "long"       in e: return "Voice note बहुत लंबा है। 2 मिनट से कम भेजें।"
        if "short"      in e: return "Voice note बहुत छोटा है। थोड़ा लंबा बोलें।"
        if "corrupt"    in e: return "Voice note खराब है। दोबारा record करें।"
        if "unsupported" in e: return "यह format supported नहीं है।"
        return "Voice note process नहीं हो सका। दोबारा भेजें। 🙏"
    else:
        if "not found"  in e: return "Voice note not received. Please send again. 🙏"
        if "large"      in e: return "Voice note too large. Send a shorter one."
        if "long"       in e: return "Voice note too long. Keep it under 2 minutes."
        if "short"      in e: return "Voice note too short. Please speak longer."
        if "corrupt"    in e: return "Voice note corrupted. Please record again."
        if "unsupported" in e: return "This audio format is not supported."
        return "Could not process voice note. Please try again. 🙏"
`

## core/model.py

Crop disease prediction model

`python
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch

MODEL_NAME = "sanjeevani-04/indian-crop-disease-mobilenetv2"

extractor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)

model.eval()

def predict_disease(image_path: str, top_k: int=3):
  image = Image.open(image_path).convert("RGB")
  inputs = extractor(images=image, return_tensors='pt')

  with torch.no_grad():
    logits = model(**inputs).logits

  probs = torch.softmax(logits, dim=-1)[0]
  top_indices = probs.topk(top_k).indices.tolist()

  results = []
  for idx in top_indices:
    label = model.config.id2label[idx]
    confidence = probs[idx].item() * 100
    results.append({
        "disease": label,
        'confidence': round(confidence, 4)
    })

  return results
`

## core/media.py

Media helpers (empty)

`python

`

## tests/test_pipeline.py

Example test pipeline

`python
from pathlib import Path
import sys

# Add project root so `core` can be imported when this file is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import detect_language, answer_general_question, text_to_audio, transcribe_audio


# Test 1 — Hindi text
text = "मेरे टमाटर की पत्तियां पीली हो रही हैं, क्या करूं?"
lang = detect_language(text)
reply1 = answer_general_question(text, lang)
print(f"Hindi reply:\n{reply1}\n")

# Test 2 — English text  
text = "My wheat crop has brown spots on the leaves. What should I do?"
lang = detect_language(text)
reply = answer_general_question(text, lang)
print(f"English reply:\n{reply}\n")

# Test 3 — Text to audio
audio_path = text_to_audio(reply1, lang_code="hi")
print(f"Audio saved to: {audio_path}")

# Test 4 — Transcribe a local audio file (if you have one)
# transcript, lang = transcribe_audio("my_voice_note.ogg")
# print(f"Transcript: {transcript} | Language: {lang}")
`
