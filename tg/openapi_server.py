from quart import Quart, request, send_from_directory, jsonify
import os

app = Quart(__name__)

# whisper on datacranch doesn't support sending audio files
# let's use openapi server for providing URL to them
AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mp3_files"))

@app.route("/all_audio")
async def show_all_audio():
    files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")]
    links = [f"<a href='/{f}'>{f}</a><br>" for f in files]
    return "<h2>MP3 Files:</h2>" + "\n".join(links)

@app.route("/<filename>")
async def provide_mp3(filename):
    return await send_from_directory(AUDIO_DIR, filename)

# we need to connect main applicatiom with telegram bot
# let's provide last message from telegram bot 
last_message = None

@app.route("/get_last_msg", methods=["GET"])
async def get_last_msg():
    if last_message is None:
        return jsonify({"error": "No message yet"}), 404
    return jsonify(last_message)

@app.route("/push_msg", methods=["POST", "PUT"])
async def push_msg():
    global last_message
    data = await request.get_json()

    if not isinstance(data, dict) or "text" not in data or "id" not in data:
        return jsonify({"error": "Invalid JSON, 'text' and 'id' required"}), 400

    last_message = {
        "text": data["text"],
        "id": data["id"]
    }

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    os.makedirs(AUDIO_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=8000)
