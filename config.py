# Ruhvaan Bot - Config
import os
from dotenv import load_dotenv
load_dotenv()

# Core
API_ID       = os.getenv("API_ID", "").strip()
API_HASH     = os.getenv("API_HASH", "").strip()
BOT_TOKEN    = os.getenv("BOT_TOKEN", "").strip()
MONGO_DB     = os.getenv("MONGO_DB", "").strip()
DB_NAME      = os.getenv("DB_NAME", "ruhvaan_bot")

# Owner
OWNER_ID     = list(map(int, filter(None, os.getenv("OWNER_ID", "").split())))
STRING       = os.getenv("STRING", "").strip() or None
LOG_GROUP    = int(os.getenv("LOG_GROUP", "0") or 0)
FORCE_SUB    = int(os.getenv("FORCE_SUB", "0") or 0)

# Security
MASTER_KEY   = os.getenv("MASTER_KEY", "gK8HzLfT9QpViJcYeB5wRa3DmN7P2xUq")
IV_KEY       = os.getenv("IV_KEY", "s7Yx5CpVmE3F")

# Cookies
INST_COOKIES = os.getenv("INSTA_COOKIES", "")
YTUB_COOKIES = os.getenv("YT_COOKIES", "")
YT_COOKIES   = YTUB_COOKIES
INSTA_COOKIES = INST_COOKIES

# Limits
FREEMIUM_LIMIT = int(os.getenv("FREEMIUM_LIMIT", "0") or 0)
PREMIUM_LIMIT  = int(os.getenv("PREMIUM_LIMIT", "500") or 500)

# Branding
BOT_NAME      = "Ruhvaan Bot"
BOT_USERNAME  = os.getenv("BOT_USERNAME", "@RuhvaanBot")
JOIN_LINK     = os.getenv("JOIN_LINK", "https://t.me/Ruhvaan")
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "https://t.me/Ruhvaan")

# Watermark
WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "@Ruhvaan")
WATERMARK_LOGO = os.getenv("WATERMARK_LOGO", "")

# Plans
P0 = {
    "d": {"s": int(os.getenv("PLAN_D_S", 1) or 1), "du": 1, "u": "days",  "l": "Daily"},
    "w": {"s": int(os.getenv("PLAN_W_S", 3) or 3), "du": 1, "u": "weeks", "l": "Weekly"},
    "m": {"s": int(os.getenv("PLAN_M_S", 5) or 5), "du": 1, "u": "month", "l": "Monthly"},
}
