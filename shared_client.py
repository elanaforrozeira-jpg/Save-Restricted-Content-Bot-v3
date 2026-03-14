# Ruhvaan Bot - Shared Client (lazy init to prevent crash on import)

import sys
from config import API_ID, API_HASH, BOT_TOKEN, STRING

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("[Ruhvaan] FATAL: API_ID, API_HASH, or BOT_TOKEN is missing from environment variables!")
    sys.exit(1)

from telethon import TelegramClient
from pyrogram import Client

client = TelegramClient("ruhvaan_telethon", int(API_ID), API_HASH)
app = Client("ruhvaan_pyro", api_id=int(API_ID), api_hash=API_HASH, bot_token=BOT_TOKEN)

if STRING:
    userbot = Client("ruhvaan_userbot", api_id=int(API_ID), api_hash=API_HASH, session_string=STRING)
else:
    userbot = None

async def start_client():
    if not client.is_connected():
        await client.start(bot_token=BOT_TOKEN)
        print("[Ruhvaan] Telethon client started.")
    if userbot:
        try:
            await userbot.start()
            print("[Ruhvaan] Userbot started.")
        except Exception as e:
            print(f"[Ruhvaan] Userbot error (check STRING): {e}")
            sys.exit(1)
    await app.start()
    print("[Ruhvaan] Pyrogram bot started.")
    return client, app, userbot
