# Ruhvaan Bot - Shared Client

import sys
from config import API_ID, API_HASH, BOT_TOKEN, STRING

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("[Ruhvaan] FATAL: API_ID, API_HASH or BOT_TOKEN missing!")
    sys.exit(1)

from telethon import TelegramClient
from pyrogram import Client

_api_id = int(API_ID)

# Telethon client (for raw MTProto / restricted channel access)
client = TelegramClient("ruhvaan_telethon", _api_id, API_HASH)

# Pyrogram bot (for all /commands and handlers)
app = Client(
    "ruhvaan_pyro",
    api_id=_api_id,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

BOT_TOKEN_INT = True  # marker used in app.py

# Userbot (optional, for private channel access)
if STRING and STRING.strip():
    userbot = Client(
        "ruhvaan_userbot",
        api_id=_api_id,
        api_hash=API_HASH,
        session_string=STRING
    )
else:
    userbot = None
