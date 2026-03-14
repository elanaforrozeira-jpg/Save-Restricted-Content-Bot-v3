# Ruhvaan Bot - Entry Point (Railway/Render)

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
    logger.info("[Ruhvaan Bot] Running... Press Ctrl+C to stop.")

    # Keep bot alive: Telethon runs its own loop, Pyrogram just needs to stay open
    stop_event = asyncio.Event()

    async def telethon_task():
        await client.run_until_disconnected()
        stop_event.set()

    async def pyrogram_task():
        # Pyrogram 2.x: keep alive by waiting for stop event
        await stop_event.wait()

    try:
        await asyncio.gather(
            telethon_task(),
            pyrogram_task()
        )
    except (KeyboardInterrupt, SystemExit):
        logger.info("[Ruhvaan] Shutting down...")
    finally:
        try:
            await app.stop()
        except Exception as e:
            logger.error(f"App stop error: {e}")
        try:
            await client.disconnect()
        except Exception as e:
            logger.error(f"Client disconnect error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
