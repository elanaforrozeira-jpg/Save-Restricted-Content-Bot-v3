# Ruhvaan Bot - Shared Client
# Real clients initialized here so all plugins get the same object

import os
import sys
from dotenv import load_dotenv
load_dotenv()

API_ID    = os.environ.get("API_ID", "").strip()
API_HASH  = os.environ.get("API_HASH", "").strip()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
STRING    = os.environ.get("STRING", "").strip() or None

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("[FATAL] API_ID / API_HASH / BOT_TOKEN missing from environment!")
    sys.exit(1)

from pyrogram import Client

# Main bot client - all plugins use this
app = Client(
    "ruhvaan_pyro",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Userbot (optional)
if STRING:
    userbot = Client(
        "ruhvaan_userbot",
        api_id=int(API_ID),
        api_hash=API_HASH,
        session_string=STRING
    )
else:
    userbot = None

# Telethon (for restricted channel access)
from telethon import TelegramClient
client = TelegramClient("ruhvaan_tele", int(API_ID), API_HASH)
