# Ruhvaan Bot - Entry point (Railway/Render)
# Runs bot directly — no Flask needed (Railway supports long-running processes)

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
    for fname in sorted(os.listdir(PLUGIN_DIR)):
        if fname.endswith(".py") and not fname.startswith("_"):
            mod = f"{PLUGIN_DIR}.{fname[:-3]}"
            try:
                importlib.import_module(mod)
                logger.info(f"Loaded: {mod}")
            except Exception as e:
                logger.error(f"Failed {mod}: {e}")

async def run():
    from shared_client import start_client, client, app
    load_plugins()
    await start_client()
    logger.info("[Ruhvaan Bot] Running...")
    await asyncio.gather(
        client.run_until_disconnected(),
        app.idle()
    )

if __name__ == "__main__":
    asyncio.run(run())
