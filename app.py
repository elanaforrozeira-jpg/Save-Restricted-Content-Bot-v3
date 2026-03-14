# Ruhvaan Bot - Entry Point (Railway web dyno compatible)

import asyncio
import importlib
import os
import logging
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PLUGIN_DIR = "plugins"

# ---- Tiny health server so Railway doesn't kill the process ----
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Ruhvaan Bot is running OK")
    def log_message(self, *args): pass  # silence access logs

def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"[Ruhvaan] Health server on port {port}")
    server.serve_forever()

# ----------------------------------------------------------------

def load_plugins():
    loaded = 0
    for fname in sorted(os.listdir(PLUGIN_DIR)):
        if fname.endswith(".py") and not fname.startswith("_"):
            mod = f"{PLUGIN_DIR}.{fname[:-3]}"
            try:
                importlib.import_module(mod)
                logger.info(f"[+] {fname}")
                loaded += 1
            except Exception as e:
                logger.error(f"[!] {fname}: {e}")
    logger.info(f"[Ruhvaan] {loaded} plugins loaded.")

async def run():
    from shared_client import app, client, userbot
    from config import BOT_TOKEN

    # Load plugins BEFORE starting (registers all handlers)
    load_plugins()

    # Start Pyrogram
    await app.start()
    logger.info("[Ruhvaan] Pyrogram bot started.")

    # Start Telethon
    await client.start(bot_token=BOT_TOKEN)
    logger.info("[Ruhvaan] Telethon client started.")

    # Start userbot if available
    if userbot:
        try:
            await userbot.start()
            logger.info("[Ruhvaan] Userbot started.")
        except Exception as e:
            logger.error(f"[Ruhvaan] Userbot failed: {e}")

    logger.info("[Ruhvaan] ✅ Bot is LIVE!")

    # Keep alive via Telethon
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Start health server in background thread
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()

    # Run the bot
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        logger.info("[Ruhvaan] Stopped.")
