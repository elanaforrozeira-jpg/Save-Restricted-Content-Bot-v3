# Ruhvaan Bot - Start & Help Module

from shared_client import app
from pyrogram import filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOG_GROUP, OWNER_ID, FORCE_SUB, BOT_NAME, JOIN_LINK, ADMIN_CONTACT
try:
    from plugins.access import has_access, track_user
except: pass

START_IMG = "https://graph.org/file/d44f024a08ded19452152.jpg"  # replace with your own banner

async def subscribe(app, message):
    if not FORCE_SUB:
        return 0
    try:
        user = await app.get_chat_member(FORCE_SUB, message.from_user.id)
        if str(user.status) == "ChatMemberStatus.BANNED":
            await message.reply_text(f"🚫 You are banned. Contact — {ADMIN_CONTACT}")
            return 1
    except UserNotParticipant:
        link = await app.export_chat_invite_link(FORCE_SUB)
        await message.reply_photo(
            photo=START_IMG,
            caption=f"👋 Join our channel to use **{BOT_NAME}**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Now 🚀", url=link)]])
        )
        return 1
    except Exception as ex:
        await message.reply_text(f"⚠️ Error: {ex}")
        return 1
    return 0

@app.on_message(filters.command("set"))
async def set_commands(_, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("🚫 Not authorized.")
        return
    await app.set_bot_commands([
        BotCommand("start",    "🚀 Start the bot"),
        BotCommand("batch",    "📦 Bulk extract with watermark"),
        BotCommand("login",    "🔑 Login for private channels"),
        BotCommand("logout",   "🚪 Logout"),
        BotCommand("settings", "⚙️ Personalize your settings"),
        BotCommand("allow",    "✅ Grant access to a user [Owner]"),
        BotCommand("revoke",   "❌ Revoke user access [Owner]"),
        BotCommand("users",    "👥 See all users [Owner]"),
        BotCommand("allowed",  "📋 List allowed users [Owner]"),
        BotCommand("stats",    "📊 Bot statistics"),
        BotCommand("plan",     "💎 Premium plans"),
        BotCommand("help",     "❓ Help"),
        BotCommand("cancel",   "🚫 Cancel ongoing process"),
        BotCommand("stop",     "🛑 Stop batch"),
    ])
    await message.reply("✅ Commands set!")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user = message.from_user
    # Track user
    try:
        await track_user(user.id, user.username or "", user.full_name or "")
    except: pass

    # Force sub check
    if await subscribe(client, message):
        return

    # Access check
    try:
        access = await has_access(user.id)
    except:
        access = user.id in OWNER_ID

    if not access:
        await message.reply_photo(
            photo=START_IMG,
            caption=(
                f"👋 Hello **{user.first_name}**!\n\n"
                f"Welcome to **{BOT_NAME}** 🎉\n\n"
                f"🔒 You don't have access yet.\n"
                f"Contact admin to get access:\n{ADMIN_CONTACT}"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Contact Admin", url=ADMIN_CONTACT)],
                [InlineKeyboardButton("📢 Join Channel", url=JOIN_LINK)],
            ])
        )
        return

    await message.reply_photo(
        photo=START_IMG,
        caption=(
            f"👋 Hello **{user.first_name}**!\n\n"
            f"Welcome to **{BOT_NAME}** 🚀\n\n"
            f"✅ You have access!\n\n"
            f"📦 Use /batch to extract files from restricted channels\n"
            f"⚙️ Use /settings to customize watermark, caption & more\n"
            f"❓ Use /help for all commands"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Batch", callback_data="help_batch"),
             InlineKeyboardButton("⚙️ Settings", callback_data="go_settings")],
            [InlineKeyboardButton("📢 Channel", url=JOIN_LINK),
             InlineKeyboardButton("💬 Support", url=ADMIN_CONTACT)],
        ])
    )

help_pages = [
    (
        f"📝 **{BOT_NAME} — Commands (1/2)**\n\n"
        "1. **/allow** `user_id` — Grant access [Owner]\n"
        "2. **/revoke** `user_id` — Revoke access [Owner]\n"
        "3. **/users** — View all users + last active [Owner]\n"
        "4. **/allowed** — List allowed users [Owner]\n"
        "5. **/batch** — Bulk extract from any channel\n"
        "6. **/login** — Login with session for private channels\n"
        "7. **/logout** — Logout\n"
        "8. **/settings** — Set watermark, caption, rename, thumbnail\n"
        "9. **/cancel** — Cancel current process\n"
    ),
    (
        f"📝 **{BOT_NAME} — Commands (2/2)**\n\n"
        "10. **/stats** — Bot statistics\n"
        "11. **/plan** — Premium plans\n"
        "12. **/terms** — Terms & conditions\n"
        "13. **/help** — This help\n\n"
        "⚙️ **Settings Options:**\n"
        "> SETCHATID — Upload to specific channel/group\n"
        "> SETRENAME — Add rename prefix/suffix\n"
        "> CAPTION — Custom caption\n"
        "> WATERMARK — Custom watermark text\n"
        "> THUMBNAIL — Custom thumbnail\n"
        "> RESET — Reset to defaults\n\n"
        f"**— {BOT_NAME}**"
    )
]

async def _send_help_page(client, message, page):
    if page < 0 or page >= len(help_pages): return
    btns = []
    if page > 0: btns.append(InlineKeyboardButton("◀️ Prev", callback_data=f"help_prev_{page}"))
    if page < len(help_pages)-1: btns.append(InlineKeyboardButton("Next ▶️", callback_data=f"help_next_{page}"))
    await message.delete()
    await message.reply(help_pages[page], reply_markup=InlineKeyboardMarkup([btns]) if btns else None)

@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    if await subscribe(client, message): return
    await _send_help_page(client, message, 0)

@app.on_callback_query(filters.regex(r"help_(prev|next)_(\d+)"))
async def help_nav(client, cq):
    action = cq.data.split("_")[1]
    page = int(cq.data.split("_")[2])
    page = page - 1 if action == "prev" else page + 1
    await _send_help_page(client, cq.message, page)
    await cq.answer()

@app.on_message(filters.command("terms") & filters.private)
async def terms(client, message):
    await message.reply(
        f"> 📜 **{BOT_NAME} — Terms & Conditions**\n\n"
        "• We are not responsible for misuse of this bot.\n"
        "• Do not use this bot to violate copyright laws.\n"
        "• Access can be revoked at any time without notice.\n"
        "• Premium plans do not guarantee 24/7 uptime.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Plans", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Contact", url=ADMIN_CONTACT)],
        ])
    )

@app.on_message(filters.command("plan") & filters.private)
async def plan(client, message):
    await message.reply(
        f"> 💎 **{BOT_NAME} — Premium Plans**\n\n"
        "Contact admin to get access and pricing:\n"
        f"{ADMIN_CONTACT}\n\n"
        "✅ **What you get:**\n"
        "• Unlimited batch extraction\n"
        "• Watermark on all files\n"
        "• Custom rename & caption\n"
        "• Private channel support\n"
        "• Priority support",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Contact Admin", url=ADMIN_CONTACT)],
        ])
    )

@app.on_callback_query(filters.regex("see_plan"))
async def cb_see_plan(client, cq):
    await plan(client, cq.message)
    await cq.answer()
