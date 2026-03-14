# Ruhvaan Bot - Main Entry

import asyncio
import importlib
import os
import logging

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
                logger.info(f"[Ruhvaan] Plugin loaded: {mod}")
            except Exception as e:
                logger.error(f"[Ruhvaan] Plugin FAILED {mod}: {e}")

async def main():
    from shared_client import start_client, client, app
    load_plugins()
    await start_client()
    logger.info("[Ruhvaan] All systems running.")
    await asyncio.gather(
        client.run_until_disconnected(),
        app.idle()
    )

if __name__ == "__main__":
    asyncio.run(main())
