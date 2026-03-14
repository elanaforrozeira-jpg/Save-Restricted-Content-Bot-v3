# Ruhvaan Bot - Utility Functions

import concurrent.futures
import time
import os
import re
import logging
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB as MONGO_URI, DB_NAME

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

PUBLIC_LINK_PATTERN = re.compile(r'(https?://)?(t\.me|telegram\.me)/([^/]+)(/(\d+))?')
PRIVATE_LINK_PATTERN = re.compile(r'(https?://)?(t\.me|telegram\.me)/c/(\d+)(/(\d+))?')
VIDEO_EXTENSIONS = {"mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "mpeg", "mpg", "3gp"}

# DB init
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db["users"]
premium_users_collection = db["premium_users"]
statistics_collection = db["statistics"]
codedb = db["redeem_code"]
ruhvaan_db = db  # exported for access.py

def is_private_link(link):
    return bool(PRIVATE_LINK_PATTERN.match(link))

def thumbnail(sender):
    return f'{sender}.jpg' if os.path.exists(f'{sender}.jpg') else None

def hhmmss(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

def E(L):
    private_match = re.match(r'https://t\.me/c/(\d+)/(?:\d+/)?(\d+)', L)
    public_match = re.match(r'https://t\.me/([^/]+)/(?:\d+/)?(\d+)', L)
    if private_match:
        return f'-100{private_match.group(1)}', int(private_match.group(2)), 'private'
    elif public_match:
        return public_match.group(1), int(public_match.group(2)), 'public'
    return None, None, None

def get_display_name(user):
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    return user.first_name or user.last_name or user.username or "Unknown"

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def get_dummy_filename(info):
    ext = {"video": "mp4", "photo": "jpg", "document": "pdf", "audio": "mp3"}.get(info.get("type", ""), "bin")
    return f"ruhvaan_file_{int(time.time())}.{ext}"

async def save_user_data(user_id, key, value):
    await users_collection.update_one({"user_id": user_id}, {"$set": {key: value}}, upsert=True)

async def get_user_data_key(user_id, key, default=None):
    data = await users_collection.find_one({"user_id": int(user_id)})
    return data.get(key, default) if data else default

async def get_user_data(user_id):
    try:
        return await users_collection.find_one({"user_id": user_id})
    except Exception as e:
        logger.error(f"get_user_data error {user_id}: {e}")
        return None

async def save_user_session(user_id, session_string):
    try:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"session_string": session_string, "updated_at": datetime.now()}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"save_user_session error: {e}")
        return False

async def remove_user_session(user_id):
    try:
        await users_collection.update_one({"user_id": user_id}, {"$unset": {"session_string": ""}})
        return True
    except Exception as e:
        logger.error(f"remove_user_session error: {e}")
        return False

async def save_user_bot(user_id, bot_token):
    try:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"bot_token": bot_token, "updated_at": datetime.now()}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"save_user_bot error: {e}")
        return False

async def remove_user_bot(user_id):
    try:
        await users_collection.update_one({"user_id": user_id}, {"$unset": {"bot_token": ""}})
        return True
    except Exception as e:
        logger.error(f"remove_user_bot error: {e}")
        return False

async def process_text_with_rules(user_id, text):
    if not text: return ""
    try:
        replacements = await get_user_data_key(user_id, "replacement_words", {})
        delete_words = await get_user_data_key(user_id, "delete_words", [])
        processed = text
        for w, r in replacements.items():
            processed = processed.replace(w, r)
        if delete_words:
            processed = " ".join(w for w in processed.split() if w not in delete_words)
        return processed
    except Exception as e:
        logger.error(f"process_text_with_rules error: {e}")
        return text

async def screenshot(video: str, duration: int, sender: str):
    existing = f"{sender}.jpg"
    if os.path.exists(existing): return existing
    ts = hhmmss(duration // 2)
    out = datetime.now().isoformat("_", "seconds") + ".jpg"
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-ss", ts, "-i", video, "-frames:v", "1", out, "-y",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    return out if os.path.isfile(out) else None

async def get_video_metadata(file_path):
    default = {'width': 1, 'height': 1, 'duration': 1}
    loop = asyncio.get_event_loop()
    try:
        import cv2
        def _extract():
            try:
                cap = cv2.VideoCapture(file_path)
                if not cap.isOpened(): return default
                w = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                fc = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                cap.release()
                if fps <= 0: return default
                return {'width': w, 'height': h, 'duration': round(fc / fps)}
            except: return default
        return await loop.run_in_executor(concurrent.futures.ThreadPoolExecutor(max_workers=2), _extract)
    except: return default

async def add_premium_user(user_id, duration_value, duration_unit):
    try:
        now = datetime.now()
        units = {"min": timedelta(minutes=duration_value), "hours": timedelta(hours=duration_value),
                 "days": timedelta(days=duration_value), "weeks": timedelta(weeks=duration_value),
                 "month": timedelta(days=30*duration_value), "year": timedelta(days=365*duration_value),
                 "decades": timedelta(days=3650*duration_value)}
        if duration_unit not in units: return False, "Invalid duration unit"
        expiry = now + units[duration_unit]
        await premium_users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "subscription_start": now, "subscription_end": expiry, "expireAt": expiry}},
            upsert=True
        )
        await premium_users_collection.create_index("expireAt", expireAfterSeconds=0)
        return True, expiry
    except Exception as e:
        logger.error(f"add_premium_user error: {e}")
        return False, str(e)

async def is_premium_user(user_id):
    try:
        u = await premium_users_collection.find_one({"user_id": user_id})
        if u and "subscription_end" in u:
            return datetime.now() < u["subscription_end"]
        return False
    except: return False

async def get_premium_details(user_id):
    try:
        return await premium_users_collection.find_one({"user_id": user_id})
    except: return None
