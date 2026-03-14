# Ruhvaan Bot - Railway Entry Point

import os
import sys
import asyncio
import logging
import threading

from flask import Flask

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "<h1>Ruhvaan Bot ✅</h1>", 200

@flask_app.route("/health")
def health():
    return {"status": "ok"}, 200


def run_bot():
    """Bot runs in its own thread with its own event loop."""

    async def _bot():
        API_ID    = os.environ.get("API_ID", "").strip()
        API_HASH  = os.environ.get("API_HASH", "").strip()
        BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
        STRING    = os.environ.get("STRING", "").strip() or None

        if not all([API_ID, API_HASH, BOT_TOKEN]):
            logger.error("[FATAL] API_ID / API_HASH / BOT_TOKEN missing!")
            return

        logger.info("[Ruhvaan] Importing libraries...")
        from pyrogram import Client as PyroClient
        from telethon import TelegramClient

        # 1. Create clients
        pyro = PyroClient(
            "ruhvaan_pyro",
            api_id=int(API_ID),
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
        )
        tele = TelegramClient("ruhvaan_tele", int(API_ID), API_HASH)

        userbot = None
        if STRING:
            userbot = PyroClient(
                "ruhvaan_userbot",
                api_id=int(API_ID),
                api_hash=API_HASH,
                session_string=STRING
            )

        # 2. Inject into shared_client BEFORE plugins load
        import shared_client as sc
        sc.app     = pyro
        sc.client  = tele
        sc.userbot = userbot
        sc.API_ID    = int(API_ID)
        sc.API_HASH  = API_HASH
        sc.BOT_TOKEN = BOT_TOKEN
        logger.info("[Ruhvaan] Shared clients set.")

        # 3. Load plugins (NOW app is real, handlers register correctly)
        import importlib
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
        logger.info(f"[Ruhvaan] {loaded} plugins loaded.")

        # 4. Start Pyrogram
        await pyro.start()
        me = await pyro.get_me()
        logger.info(f"[Ruhvaan] ✅ Bot: @{me.username}")

        # 5. Start Telethon
        await tele.start(bot_token=BOT_TOKEN)
        logger.info("[Ruhvaan] ✅ Telethon started.")

        # 6. Userbot
        if userbot:
            try:
                await userbot.start()
                logger.info("[Ruhvaan] ✅ Userbot started.")
            except Exception as e:
                logger.warning(f"[Ruhvaan] Userbot failed: {e}")

        logger.info("[Ruhvaan] 🚀 ALL SYSTEMS GO!")
        await tele.run_until_disconnected()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_bot())
    except Exception as e:
        logger.error(f"[Ruhvaan] Bot thread crashed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Start bot in background
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    logger.info("[Ruhvaan] Bot thread launched.")

    # Flask on Railway's PORT (default 8080 if not set)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"[Ruhvaan] Flask on port {port}")
    flask_app.run(host="0.0.0.0", port=port, debug=False)
