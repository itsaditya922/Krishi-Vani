from flask import Flask, request, send_from_directory
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import requests
import tempfile
import shutil
import logging
from core.model import *
from core.agent import *
from core.audio import *

load_dotenv()
logger = logging.getLogger(__name__)

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
    """Copy audio file to uploads directory and return public URL."""
    filename = os.path.basename(audio_path)
    dest = os.path.join("uploads", filename)
    
    shutil.copy2(audio_path, dest)
    os.unlink(audio_path)
    
    logger.info(f"Audio file moved to: {dest}")
    
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

@app.route("/")
def home():
    return "✅ KrishiVani agriculture assistant is running"




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
            logger.info(f"Generated audio reply: {audio_reply_path}")

            public_url = upload_audio_for_twilio(audio_reply_path)
            logger.info(f"Public audio URL: {public_url}")
            
            sid = send_whatsapp_audio(to=from_number, audio_url=public_url, caption="🌱 KrishiVani")
            logger.info(f"WhatsApp message sent (SID: {sid}) from {TWILIO_NUMBER} to {from_number}")
            return str(twiml)
        else:
            twiml.message(reply_text)
            return str(twiml)

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return str(MessagingResponse()), 500
    
if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("🚀 Starting KrishiVani Twilio/WhatsApp server...")
    logger.info(f"Listening on http://127.0.0.1:5000")
    logger.info(f"Webhook endpoint: http://127.0.0.1:5000/webhook")
    app.run(debug=True, port=5000)