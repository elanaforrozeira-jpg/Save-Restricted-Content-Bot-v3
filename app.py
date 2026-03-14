# Ruhvaan Bot - Minimal startup for Railway debug
import asyncio
import os
import sys
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Ruhvaan OK")
    def log_message(self, *a): pass

def health():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), H).serve_forever()

async def main():
    logger.info("=== RUHVAAN BOT STARTING ===")

    # Step 1: Check env vars
    API_ID = os.environ.get("API_ID", "")
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    MONGO_DB = os.environ.get("MONGO_DB", "")

    logger.info(f"API_ID present: {bool(API_ID)}")
    logger.info(f"API_HASH present: {bool(API_HASH)}")
    logger.info(f"BOT_TOKEN present: {bool(BOT_TOKEN)}")
    logger.info(f"MONGO_DB present: {bool(MONGO_DB)}")

    if not API_ID or not API_HASH or not BOT_TOKEN:
        logger.error("FATAL: Missing env vars! Check Railway Variables tab.")
        sys.exit(1)

    # Step 2: Import pyrogram
    logger.info("Importing Pyrogram...")
    try:
        from pyrogram import Client
        logger.info("Pyrogram import OK")
    except Exception as e:
        logger.error(f"Pyrogram import FAILED: {e}")
        sys.exit(1)

    # Step 3: Import telethon
    logger.info("Importing Telethon...")
    try:
        from telethon import TelegramClient
        logger.info("Telethon import OK")
    except Exception as e:
        logger.error(f"Telethon import FAILED: {e}")
        sys.exit(1)

    # Step 4: Start Pyrogram bot
    logger.info("Starting Pyrogram bot...")
    try:
        bot = Client("ruhvaan_test", api_id=int(API_ID), api_hash=API_HASH, bot_token=BOT_TOKEN)
        await bot.start()
        me = await bot.get_me()
        logger.info(f"Pyrogram OK! Bot: @{me.username}")
    except Exception as e:
        logger.error(f"Pyrogram start FAILED: {e}")
        sys.exit(1)

    # Step 5: Start Telethon
    logger.info("Starting Telethon...")
    try:
        tc = TelegramClient("ruhvaan_tl", int(API_ID), API_HASH)
        await tc.start(bot_token=BOT_TOKEN)
        logger.info("Telethon OK!")
    except Exception as e:
        logger.error(f"Telethon start FAILED: {e}")
        sys.exit(1)

    logger.info("=== ALL SYSTEMS GO! BOT IS LIVE ===")
    await tc.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=health, daemon=True).start()
    asyncio.run(main())
