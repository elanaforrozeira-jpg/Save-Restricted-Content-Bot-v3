# Ruhvaan Bot - Access Control & User Tracking

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shared_client import app
from config import OWNER_ID, LOG_GROUP
import datetime

# ─── DB helpers (motor/pymongo via utils.db) ──────────────────────────────────
try:
    from utils.db import ruhvaan_db as db
except:
    db = None

# ─── ACCESS CHECK ─────────────────────────────────────────────────────────────
async def has_access(user_id: int) -> bool:
    """Returns True if user is owner or has been granted access."""
    if user_id in OWNER_ID:
        return True
    if db is None:
        return False
    user = await db["allowed_users"].find_one({"user_id": user_id})
    return user is not None

async def track_user(user_id: int, username: str, full_name: str):
    """Log user activity to DB."""
    if db is None:
        return
    now = datetime.datetime.utcnow()
    await db["users"].update_one(
        {"user_id": user_id},
        {"$set": {"username": username, "full_name": full_name, "last_seen": now},
         "$setOnInsert": {"first_seen": now}},
        upsert=True
    )

# ─── /allow COMMAND ───────────────────────────────────────────────────────────
@app.on_message(filters.command("allow") & filters.private)
async def allow_user(client, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("🚫 Only owner can grant access.")
        return
    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.reply("Usage: `/allow user_id`")
        return
    try:
        uid = int(parts[1])
    except:
        await message.reply("❌ Invalid user ID.")
        return
    if db is None:
        await message.reply("❌ DB not connected.")
        return
    await db["allowed_users"].update_one(
        {"user_id": uid},
        {"$set": {"user_id": uid, "granted_at": datetime.datetime.utcnow()}},
        upsert=True
    )
    await message.reply(f"✅ Access granted to `{uid}`.")
    try:
        await client.send_message(uid, "✅ You have been granted access to **Ruhvaan Bot**!\n\nSend /start to begin.")
    except: pass

# ─── /revoke COMMAND ──────────────────────────────────────────────────────────
@app.on_message(filters.command("revoke") & filters.private)
async def revoke_user(client, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("🚫 Only owner can revoke access.")
        return
    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.reply("Usage: `/revoke user_id`")
        return
    try:
        uid = int(parts[1])
    except:
        await message.reply("❌ Invalid user ID.")
        return
    if db is None:
        await message.reply("❌ DB not connected.")
        return
    result = await db["allowed_users"].delete_one({"user_id": uid})
    if result.deleted_count:
        await message.reply(f"✅ Access revoked from `{uid}`.")
        try:
            await client.send_message(uid, "❌ Your access to **Ruhvaan Bot** has been revoked.")
        except: pass
    else:
        await message.reply(f"ℹ️ User `{uid}` was not in allowed list.")

# ─── /users COMMAND ───────────────────────────────────────────────────────────
@app.on_message(filters.command("users") & filters.private)
async def list_users(client, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("🚫 Owner only.")
        return
    if db is None:
        await message.reply("❌ DB not connected.")
        return
    total = await db["users"].count_documents({})
    allowed = await db["allowed_users"].count_documents({})
    # Get last 10 active users
    cursor = db["users"].find({}).sort("last_seen", -1).limit(10)
    lines = []
    async for u in cursor:
        name = u.get("full_name", "Unknown")
        uname = u.get("username") or "no_username"
        uid = u.get("user_id")
        last = u.get("last_seen", "-")
        if hasattr(last, 'strftime'):
            last = last.strftime("%d %b %H:%M")
        lines.append(f"• {name} (@{uname}) `{uid}` — {last}")
    text = (
        f"📊 **Ruhvaan Bot — User Stats**\n\n"
        f"👥 Total users: `{total}`\n"
        f"✅ Allowed users: `{allowed}`\n\n"
        f"**🕒 Last 10 Active:**\n" + "\n".join(lines)
    )
    await message.reply(text)

# ─── /allowed COMMAND ─────────────────────────────────────────────────────────
@app.on_message(filters.command("allowed") & filters.private)
async def list_allowed(client, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("🚫 Owner only.")
        return
    if db is None:
        await message.reply("❌ DB not connected.")
        return
    cursor = db["allowed_users"].find({})
    lines = []
    async for u in cursor:
        uid = u.get("user_id")
        granted = u.get("granted_at", "-")
        if hasattr(granted, 'strftime'):
            granted = granted.strftime("%d %b %Y")
        lines.append(f"• `{uid}` — granted {granted}")
    if not lines:
        await message.reply("ℹ️ No users allowed yet. Use `/allow user_id`.")
        return
    await message.reply("✅ **Allowed Users:**\n" + "\n".join(lines))
