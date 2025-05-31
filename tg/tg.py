import os
import logging
import requests
import uuid

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from pydub import AudioSegment

FORMAT="mp3"
VOICE_DIR="mp3_files"
SERVER_IP="http://65.109.75.37:8000/"
PUSH_PATH="push_msg"

TELEGRAM_BOT_TOKEN="<your-telegram-api-key>"
TOKEN = "<your-datacrunch-interfer-api-key>"

def make_all_work_for_me(text):
    logging.info(f"Start work on next request: {text}")

    url = SERVER_IP + PUSH_PATH
    unique_id = str(uuid.uuid4())

    data = {
    "text": text,
    "id": unique_id
    }

    response_post = requests.post(url, json=data)

def convert_voice_message(voice_msg, converted_voice_msg):
    audio = AudioSegment.from_file(voice_msg, format="ogg")
    audio.export(converted_voice_msg, format=FORMAT)

def transcript(audio_path):
    audio_url = SERVER_IP + audio_path

    url = "https://fin-02.inference.datacrunch.io/v1/raw/whisperx/predict"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }

    data = {
        "audio_input": audio_url
    }

    response = requests.post(url, headers=headers, json=data)
    json_data = response.json()

    segments = json_data.get("segments", [])
    texts = [s.get("text", "") for s in segments]
    full_text = " ".join(texts).strip()

    return full_text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Ask your question")

async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if not text:
        await update.message.reply_text("No text found.")
        return

    try:
        make_all_work_for_me(text)
        await update.message.reply_text("Your request is ongoing.")

    except Exception as e:
        logging.error(f"Issue during text processing: {e}")
        await update.message.reply_text("Something wrong happened.")


async def process_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        voice = update.message.voice
        if not voice:
            await update.message.reply_text("No request.")
            return

        file_id = voice.file_id
        voice_file = await context.bot.get_file(file_id)
        
        logging.debug(f"Downloading customer request: {voice_file}")
        voice_msg_path_path = f"{VOICE_DIR}/voice_{file_id}.ogg"
        await voice_file.download_to_drive(custom_path=voice_msg_path_path)

        logging.debug(f"Convert customer request to appropriate format")
        converted_msg_path = f"{VOICE_DIR}/voice_{file_id}.{FORMAT}"
        convert_voice_message(voice_msg_path_path, converted_msg_path)

        logging.debug(f"Transcript customer request")
        text = transcript(f"voice_{file_id}.{FORMAT}")

        make_all_work_for_me(text)

        if text:
            await update.message.reply_text("Your request is ongoing.")
        else:
            await update.message.reply_text("Request is empty")

    except Exception as e:
        logging.error(f"Issue during transcribing: {e}")
        await update.message.reply_text("Something wrong happened")
    finally:
        if os.path.exists(voice_msg_path_path):
            os.remove(voice_msg_path_path)
        if os.path.exists(converted_msg_path):
            os.remove(converted_msg_path)


def tg() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    load_dotenv()

    TOKEN = os.getenv("TOKEN")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not TELEGRAM_BOT_TOKEN:
        print("Error:TELEGRAM_BOT_TOKEN is missing.")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, process_voice))
    app.add_handler(MessageHandler(filters.TEXT, process_text))

    app.run_polling()

if __name__ == "__main__":
    tg()
