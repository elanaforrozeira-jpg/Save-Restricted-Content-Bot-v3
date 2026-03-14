# Ruhvaan Bot - Main Entry Point

import asyncio
import importlib
import os
import logging
from shared_client import start_client, app, client, userbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLUGIN_DIR = "plugins"

def load_plugins():
    for fname in sorted(os.listdir(PLUGIN_DIR)):
        if fname.endswith(".py") and not fname.startswith("_"):
            mod = f"{PLUGIN_DIR}.{fname[:-3]}"
            try:
                importlib.import_module(mod)
                logger.info(f"[Ruhvaan] Loaded plugin: {mod}")
            except Exception as e:
                logger.error(f"[Ruhvaan] Failed to load {mod}: {e}")

async def main():
    load_plugins()
    await start_client()
    logger.info("[Ruhvaan] Bot is running...")
    await asyncio.gather(
        client.run_until_disconnected(),
        app.idle()
    )

if __name__ == "__main__":
    asyncio.run(main())
