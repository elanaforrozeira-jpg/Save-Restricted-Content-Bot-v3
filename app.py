# Ruhvaan Bot - Railway Entry Point

import os
import sys
import asyncio
import logging
import importlib
import threading

from flask import Flask

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask for Railway health check
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "<h1>Ruhvaan Bot ✅ Running</h1>", 200

@flask_app.route("/health")
def health():
    return {"status": "ok"}, 200


def load_plugins():
    plugin_dir = "plugins"
    loaded = 0
    for fname in sorted(os.listdir(plugin_dir)):
        if fname.endswith(".py") and not fname.startswith("_"):
            try:
                importlib.import_module(f"plugins.{fname[:-3]}")
                logger.info(f"[+] {fname}")
                loaded += 1
            except Exception as e:
                logger.error(f"[!] {fname}: {e}")
    logger.info(f"[Ruhvaan] {loaded} plugins loaded")


def run_bot():
    async def _start():
        # Import real clients from shared_client
        from shared_client import app, client, userbot
        from config import BOT_TOKEN

        # Load all plugins AFTER importing app (handlers register on real app object)
        load_plugins()
        logger.info("[Ruhvaan] Plugins loaded")

        # Start Pyrogram bot
        await app.start()
        me = await app.get_me()
        logger.info(f"[Ruhvaan] ✅ Pyrogram started: @{me.username}")

        # Start Telethon
        await client.start(bot_token=BOT_TOKEN)
        logger.info("[Ruhvaan] ✅ Telethon started")

        # Start userbot if available
        if userbot:
            try:
                await userbot.start()
                logger.info("[Ruhvaan] ✅ Userbot started")
            except Exception as e:
                logger.warning(f"[Ruhvaan] Userbot failed: {e}")

        logger.info("[Ruhvaan] 🚀 BOT IS LIVE!")

        # Keep alive
        await client.run_until_disconnected()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_start())
    except Exception as e:
        logger.error(f"[Ruhvaan] CRASH: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("[Ruhvaan] Bot thread started")

    # Flask on Railway PORT (main thread - keeps process alive)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"[Ruhvaan] Web server on port {port}")
    flask_app.run(host="0.0.0.0", port=port, debug=False)
