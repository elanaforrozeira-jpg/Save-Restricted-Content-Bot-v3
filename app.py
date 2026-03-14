# Ruhvaan Bot - Web Health Check (for Railway/Render keep-alive)

from flask import Flask
import threading
import asyncio
from main import main

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "<h2>Ruhvaan Bot is running ✅</h2>"

@flask_app.route("/health")
def health():
    return {"status": "ok", "bot": "Ruhvaan Bot"}

def run_bot():
    asyncio.run(main())

if __name__ == "__main__":
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    flask_app.run(host="0.0.0.0", port=8080)
