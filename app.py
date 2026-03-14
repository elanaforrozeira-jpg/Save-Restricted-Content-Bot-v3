# Ruhvaan Bot - Entry Point

import asyncio
import importlib
import os
import logging
import sys

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PLUGIN_DIR = "plugins"

def load_plugins():
    """Import all plugin modules so handlers get registered on the app object."""
    loaded = 0
    for fname in sorted(os.listdir(PLUGIN_DIR)):
        if fname.endswith(".py") and not fname.startswith("_"):
            mod = f"{PLUGIN_DIR}.{fname[:-3]}"
            try:
                importlib.import_module(mod)
                logger.info(f"[+] Plugin loaded: {fname}")
                loaded += 1
            except Exception as e:
                logger.error(f"[!] Plugin FAILED {fname}: {e}")
    logger.info(f"[Ruhvaan] {loaded} plugins loaded.")

async def run():
    # Step 1: Import clients
    from shared_client import app, client, userbot, BOT_TOKEN_INT

    # Step 2: Load all plugins BEFORE starting (handlers register on app)
    load_plugins()
    logger.info("[Ruhvaan] Plugins loaded. Starting clients...")

    # Step 3: Start Pyrogram bot
    await app.start()
    logger.info("[Ruhvaan] Pyrogram bot started.")

    # Step 4: Start Telethon client
    from config import BOT_TOKEN
    await client.start(bot_token=BOT_TOKEN)
    logger.info("[Ruhvaan] Telethon client started.")

    # Step 5: Start userbot if STRING is set
    if userbot:
        try:
            await userbot.start()
            logger.info("[Ruhvaan] Userbot started.")
        except Exception as e:
            logger.error(f"[Ruhvaan] Userbot error: {e}")

    logger.info("[Ruhvaan] Bot is LIVE and responding!")

    # Step 6: Keep alive
    await asyncio.gather(
        client.run_until_disconnected()
    )

async def shutdown(app, client, userbot):
    try: await app.stop()
    except: pass
    try: await client.disconnect()
    except: pass
    if userbot:
        try: await userbot.stop()
        except: pass

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run())
    except (KeyboardInterrupt, SystemExit):
        logger.info("[Ruhvaan] Shutting down...")
    finally:
        loop.close()
