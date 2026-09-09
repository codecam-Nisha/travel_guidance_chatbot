import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import (
    BOT_NAME,
    BOT_ICON,
    BOT_TAGLINE,
    THEME_COLOR,
    ACCENT_COLOR,
    SUGGESTED_QUESTIONS,
    SYSTEM_PROMPT,
)

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=SYSTEM_PROMPT)

app = Flask(__name__)

chat_sessions = {}


@app.route("/")
def home():
    return render_template(
        "index.html",
        bot_name=BOT_NAME,
        bot_icon=BOT_ICON,
        bot_tagline=BOT_TAGLINE,
        theme_color=THEME_COLOR,
        accent_color=ACCENT_COLOR,
        suggested_questions=SUGGESTED_QUESTIONS,
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"reply": "Please type a message before sending."}), 400

    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])

    try:
        response = chat_sessions[session_id].send_message(user_message)
        reply_text = response.text
    except Exception as error:
        reply_text = "Something went wrong while contacting the AI service: " + str(error)

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
