# Ruhvaan Bot - QR Login System
# QR-based Telegram login (no phone number needed)

import asyncio
import os
import logging
import qrcode
import io
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded, BadRequest, MessageNotModified
from config import API_ID, API_HASH
from shared_client import app as bot
from utils.func import save_user_session, get_user_data, remove_user_session, save_user_bot, remove_user_bot
from utils.encrypt import ecs, dcs
from plugins.batch import UB, UC
from utils.custom_filters import set_user_step, get_user_step

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track QR login sessions
qr_sessions = {}
qr_tasks = {}

# ─── QR LOGIN ─────────────────────────────────────────────────────────────────

async def _generate_qr_image(token: str) -> bytes:
    """Generate QR code bytes from token URL."""
    url = f"tg://login?token={token}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

async def _qr_login_task(client_obj, user_id: int, status_msg, bot_client):
    """Background task that refreshes QR and waits for scan."""
    try:
        while True:
            try:
                qr_login = await client_obj.qr_login()
                token = qr_login.url.split("token=")[-1] if "token=" in qr_login.url else qr_login.url
                img_bytes = await _generate_qr_image(token)

                # Edit caption + send QR
                try:
                    await status_msg.delete()
                except: pass
                status_msg = await bot_client.send_photo(
                    chat_id=user_id,
                    photo=img_bytes,
                    caption=(
                        "📱 **Scan this QR code in Telegram**\n\n"
                        "1. Open Telegram on your phone\n"
                        "2. Go to **Settings → Devices → Link Desktop Device**\n"
                        "3. Scan the QR code above\n\n"
                        "⏳ QR expires in 30 seconds — auto-refreshes\n"
                        "❌ Use /cancel to abort"
                    )
                )
                qr_sessions[user_id]["status_msg"] = status_msg

                # Wait for scan (30s timeout per QR)
                try:
                    await asyncio.wait_for(qr_login.wait(), timeout=30)
                    # ── SUCCESS ──
                    session_string = await client_obj.export_session_string()
                    encrypted = ecs(session_string)
                    await save_user_session(user_id, encrypted)
                    await client_obj.disconnect()
                    qr_sessions.pop(user_id, None)
                    qr_tasks.pop(user_id, None)
                    set_user_step(user_id, None)
                    try:
                        await status_msg.delete()
                    except: pass
                    await bot_client.send_message(
                        user_id,
                        "✅ **Logged in successfully!**\n\nYou can now use /batch to extract files from private channels."
                    )
                    return
                except asyncio.TimeoutError:
                    # QR expired → loop regenerates
                    continue
                except SessionPasswordNeeded:
                    # 2FA needed
                    qr_sessions[user_id]["step"] = "password"
                    qr_sessions[user_id]["client"] = client_obj
                    set_user_step(user_id, 99)  # password step marker
                    try:
                        await status_msg.delete()
                    except: pass
                    await bot_client.send_message(
                        user_id,
                        "🔒 **Two-step verification enabled.**\n\nPlease send your password:"
                    )
                    return

            except Exception as ex:
                logger.error(f"[QR] loop error for {user_id}: {ex}")
                await asyncio.sleep(3)
                continue

    except asyncio.CancelledError:
        try:
            await client_obj.disconnect()
        except: pass
        qr_sessions.pop(user_id, None)


@bot.on_message(filters.command("login") & filters.private)
async def login_command(bot_client, message):
    user_id = message.from_user.id

    # Cancel existing
    if user_id in qr_tasks and not qr_tasks[user_id].done():
        qr_tasks[user_id].cancel()
    if user_id in qr_sessions and "client" in qr_sessions[user_id]:
        try:
            await qr_sessions[user_id]["client"].disconnect()
        except: pass
    qr_sessions.pop(user_id, None)

    await message.delete()
    status_msg = await message.reply("🔄 Starting QR login...")
    set_user_step(user_id, 1)

    temp_client = Client(
        f"ruhvaan_qr_{user_id}",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True
    )
    try:
        await temp_client.connect()
    except Exception as ex:
        await status_msg.edit(f"❌ Connection error: {ex}")
        return

    qr_sessions[user_id] = {"client": temp_client, "status_msg": status_msg}
    task = asyncio.create_task(_qr_login_task(temp_client, user_id, status_msg, bot_client))
    qr_tasks[user_id] = task


# ─── 2FA PASSWORD HANDLER ─────────────────────────────────────────────────────

@bot.on_message(
    filters.private & filters.text &
    ~filters.command(["start", "batch", "cancel", "login", "logout", "stop", "set", "setbot", "rembot"])
)
async def handle_2fa_password(bot_client, message):
    user_id = message.from_user.id
    step = get_user_step(user_id)
    if step != 99:
        return  # Not in 2FA step

    text = message.text.strip()
    session_info = qr_sessions.get(user_id, {})
    client_obj = session_info.get("client")
    if not client_obj:
        await message.reply("❌ Session expired. Please use /login again.")
        set_user_step(user_id, None)
        return

    try:
        await message.delete()
    except: pass

    prog = await message.reply("🔄 Verifying password...")
    try:
        await client_obj.check_password(text)
        session_string = await client_obj.export_session_string()
        encrypted = ecs(session_string)
        await save_user_session(user_id, encrypted)
        await client_obj.disconnect()
        qr_sessions.pop(user_id, None)
        set_user_step(user_id, None)
        await prog.edit("✅ **Logged in successfully!**\n\nYou can now use /batch.")
    except BadRequest as ex:
        await prog.edit(f"❌ Wrong password: {ex}\n\nTry again or /cancel")
    except Exception as ex:
        await prog.edit(f"❌ Error: {ex}")
        set_user_step(user_id, None)


# ─── CANCEL ───────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("cancel") & filters.private)
async def cancel_command(bot_client, message):
    user_id = message.from_user.id
    await message.delete()

    cancelled = False
    if user_id in qr_tasks and not qr_tasks[user_id].done():
        qr_tasks[user_id].cancel()
        cancelled = True
    if user_id in qr_sessions:
        try:
            if "client" in qr_sessions[user_id]:
                await qr_sessions[user_id]["client"].disconnect()
        except: pass
        try:
            if "status_msg" in qr_sessions[user_id]:
                await qr_sessions[user_id]["status_msg"].delete()
        except: pass
        qr_sessions.pop(user_id, None)
        cancelled = True

    set_user_step(user_id, None)
    msg = await message.reply(
        "✅ Login cancelled." if cancelled else "ℹ️ No active login session."
    )
    await asyncio.sleep(4)
    try: await msg.delete()
    except: pass


# ─── LOGOUT ───────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("logout") & filters.private)
async def logout_command(bot_client, message):
    user_id = message.from_user.id
    await message.delete()
    prog = await message.reply("🔄 Logging out...")
    try:
        session_data = await get_user_data(user_id)
        if not session_data or "session_string" not in session_data:
            await prog.edit("❌ No active session found.")
            return
        session_string = dcs(session_data["session_string"])
        temp = Client(f"ruhvaan_logout_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
        try:
            await temp.connect()
            await temp.log_out()
        except Exception as ex:
            logger.error(f"Logout session error: {ex}")
        finally:
            try: await temp.disconnect()
            except: pass
        await remove_user_session(user_id)
        if UC.get(user_id):
            del UC[user_id]
        for f in [f"{user_id}_client.session", f"ruhvaan_qr_{user_id}.session"]:
            try:
                if os.path.exists(f): os.remove(f)
            except: pass
        await prog.edit("✅ Logged out successfully!")
    except Exception as ex:
        await prog.edit(f"❌ Error during logout: {ex}")
        try: await remove_user_session(user_id)
        except: pass


# ─── SETBOT / REMBOT ──────────────────────────────────────────────────────────

@bot.on_message(filters.command("setbot") & filters.private)
async def set_bot_token(_, message):
    user_id = message.from_user.id
    if user_id in UB:
        try:
            await UB[user_id].stop()
            del UB[user_id]
        except: pass
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("⚠️ Usage: `/setbot token`")
        return
    await save_user_bot(user_id, args[1].strip())
    await message.reply("✅ Custom bot token saved.")


@bot.on_message(filters.command("rembot") & filters.private)
async def rem_bot_token(_, message):
    user_id = message.from_user.id
    if user_id in UB:
        try:
            await UB[user_id].stop()
            del UB[user_id]
        except: pass
    await remove_user_bot(user_id)
    for f in [f"user_{user_id}.session"]:
        try:
            if os.path.exists(f): os.remove(f)
        except: pass
    await message.reply("✅ Custom bot token removed.")
