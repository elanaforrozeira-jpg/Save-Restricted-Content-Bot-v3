# Ruhvaan Bot - Configuration

import os
from dotenv import load_dotenv
load_dotenv()

INST_COOKIES = """
# write insta cookies here
"""

YTUB_COOKIES = """
# write yt cookies here
"""

# --- BOT / DATABASE ---
API_ID       = os.getenv("API_ID", "")
API_HASH     = os.getenv("API_HASH", "")
BOT_TOKEN    = os.getenv("BOT_TOKEN", "")
MONGO_DB     = os.getenv("MONGO_DB", "")
DB_NAME      = os.getenv("DB_NAME", "ruhvaan_bot")

# --- OWNER / CONTROL ---
OWNER_ID     = list(map(int, filter(None, os.getenv("OWNER_ID", "").split())))
STRING       = os.getenv("STRING", None) or None
LOG_GROUP    = int(os.getenv("LOG_GROUP", "0") or 0)
FORCE_SUB    = int(os.getenv("FORCE_SUB", "0") or 0)

# --- SECURITY ---
MASTER_KEY   = os.getenv("MASTER_KEY", "gK8HzLfT9QpViJcYeB5wRa3DmN7P2xUq")
IV_KEY       = os.getenv("IV_KEY", "s7Yx5CpVmE3F")

# --- COOKIES ---
YT_COOKIES    = os.getenv("YT_COOKIES", YTUB_COOKIES)
INSTA_COOKIES = os.getenv("INSTA_COOKIES", INST_COOKIES)

# --- LIMITS ---
FREEMIUM_LIMIT = int(os.getenv("FREEMIUM_LIMIT", "0") or 0)
PREMIUM_LIMIT  = int(os.getenv("PREMIUM_LIMIT", "500") or 500)

# --- BRANDING ---
BOT_NAME      = "Ruhvaan Bot"
BOT_USERNAME  = os.getenv("BOT_USERNAME", "@RuhvaanBot")
JOIN_LINK     = os.getenv("JOIN_LINK", "https://t.me/Ruhvaan")
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "https://t.me/Ruhvaan")

# --- WATERMARK ---
WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "@Ruhvaan")
WATERMARK_LOGO = os.getenv("WATERMARK_LOGO", "")

# --- PREMIUM PLANS ---
P0 = {
    "d": {"s": int(os.getenv("PLAN_D_S", 1) or 1), "du": int(os.getenv("PLAN_D_DU", 1) or 1), "u": os.getenv("PLAN_D_U", "days"), "l": os.getenv("PLAN_D_L", "Daily")},
    "w": {"s": int(os.getenv("PLAN_W_S", 3) or 3), "du": int(os.getenv("PLAN_W_DU", 1) or 1), "u": os.getenv("PLAN_W_U", "weeks"), "l": os.getenv("PLAN_W_L", "Weekly")},
    "m": {"s": int(os.getenv("PLAN_M_S", 5) or 5), "du": int(os.getenv("PLAN_M_DU", 1) or 1), "u": os.getenv("PLAN_M_U", "month"), "l": os.getenv("PLAN_M_L", "Monthly")},
}
