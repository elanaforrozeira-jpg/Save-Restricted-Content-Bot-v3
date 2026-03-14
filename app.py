# Ruhvaan Bot - Railway Optimized Entry Point
# Railway requires a web server listening on PORT
# Bot runs in background thread, Flask handles health checks

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

# ── Flask app (Railway needs HTTP on PORT) ──────────────────────
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "<h1>Ruhvaan Bot ✅ Running</h1>", 200

@flask_app.route("/health")
def health():
    return {"status": "ok", "bot": "Ruhvaan"}, 200

# ── Plugin Loader ───────────────────────────────────────────────
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
                logger.error(f"[!] {fname} failed: {e}")
    logger.info(f"[Ruhvaan] {loaded} plugins loaded")

# ── Bot Runner (runs in separate thread) ────────────────────────
def run_bot():
    async def _start():
        # Validate env vars first
        API_ID    = os.environ.get("API_ID", "")
        API_HASH  = os.environ.get("API_HASH", "")
        BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
        STRING    = os.environ.get("STRING", "") or None

        if not API_ID or not API_HASH or not BOT_TOKEN:
            logger.error("[FATAL] Missing API_ID / API_HASH / BOT_TOKEN")
            sys.exit(1)

        from pyrogram import Client
        from telethon import TelegramClient

        # Init clients
        pyro = Client(
            "ruhvaan_pyro",
            api_id=int(API_ID),
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
        )
        tele = TelegramClient("ruhvaan_tele", int(API_ID), API_HASH)

        userbot = None
        if STRING:
            userbot = Client(
                "ruhvaan_userbot",
                api_id=int(API_ID),
                api_hash=API_HASH,
                session_string=STRING
            )

        # Share globally so plugins can import
        import shared_client as sc
        sc.app    = pyro
        sc.client = tele
        sc.userbot = userbot

        # Load plugins (registers all @app.on_message handlers)
        load_plugins()

        # Start Pyrogram
        await pyro.start()
        me = await pyro.get_me()
        logger.info(f"[Ruhvaan] Bot started: @{me.username}")

        # Start Telethon
        await tele.start(bot_token=BOT_TOKEN)
        logger.info("[Ruhvaan] Telethon started")

        # Start userbot
        if userbot:
            try:
                await userbot.start()
                logger.info("[Ruhvaan] Userbot started")
            except Exception as e:
                logger.warning(f"[Ruhvaan] Userbot failed: {e}")

        logger.info("[Ruhvaan] ✅ ALL SYSTEMS GO!")
        await tele.run_until_disconnected()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_start())

# ── Main ────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("[Ruhvaan] Bot thread started")

    # Start Flask on Railway's PORT (blocks main thread = Railway happy)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"[Ruhvaan] Web server on port {port}")
    flask_app.run(host="0.0.0.0", port=port)
