# 🤖 Ruhvaan Bot

> Powerful Telegram bot to save restricted content with **watermark support**, user access control, and bulk extraction.

## ✨ Features
- 📦 Batch extract from restricted / private channels
- 💧 Auto watermark on images & videos (`@Ruhvaan`)
- 🔒 Access control — only allowed users can use the bot
- 👥 User tracking — see who is using your bot
- ⚙️ Custom settings — rename, caption, thumbnail, watermark text
- 🔑 Session login for private channels
- 📊 Stats & user management commands

## 🚀 Deploy

### Environment Variables
| Variable | Description |
|----------|-------------|
| `API_ID` | Telegram API ID |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Bot token from @BotFather |
| `MONGO_DB` | MongoDB connection URI |
| `OWNER_ID` | Your Telegram user ID (space-separated for multiple) |
| `STRING` | Optional Pyrogram session string |
| `LOG_GROUP` | Log group chat ID |
| `FORCE_SUB` | Force subscribe channel ID (0 to disable) |
| `WATERMARK_TEXT` | Watermark text (default: @Ruhvaan) |
| `ADMIN_CONTACT` | Your Telegram link for support |
| `JOIN_LINK` | Your channel link |

## 📋 Owner Commands
| Command | Description |
|---------|-------------|
| `/allow user_id` | Grant bot access to a user |
| `/revoke user_id` | Revoke access |
| `/users` | View all users + last active |
| `/allowed` | List all allowed users |
| `/stats` | Bot statistics |

## 📦 User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/batch` | Bulk extract files |
| `/login` | Login for private channels |
| `/settings` | Customize watermark, caption, etc. |
| `/help` | Help |

---
**Ruhvaan Bot** — Built with ❤️
