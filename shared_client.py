# Ruhvaan Bot - Shared Client

from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN, STRING
from pyrogram import Client
import sys

client = TelegramClient("ruhvaan_telethon", API_ID, API_HASH)
app = Client("ruhvaan_pyro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("ruhvaan_userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)

async def start_client():
    if not client.is_connected():
        await client.start(bot_token=BOT_TOKEN)
        print("[Ruhvaan] Telethon client started...")
    if STRING:
        try:
            await userbot.start()
            print("[Ruhvaan] Userbot started...")
        except Exception as e:
            print(f"[Ruhvaan] Invalid or expired STRING session: {e}")
            sys.exit(1)
    await app.start()
    print("[Ruhvaan] Pyrogram bot started...")
    return client, app, userbot
