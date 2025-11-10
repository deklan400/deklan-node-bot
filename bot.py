import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise Exception("❌ BOT_TOKEN belum di-set pada .env")

# --- Utility
def run(cmd):
    return os.popen(cmd).read()

# --- Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(CHAT_ID):
        await update.message.reply_text("❌ Unauthorized")
        return

    kb = [
        [InlineKeyboardButton("📊 Status Node", callback_data="status")],
        [
            InlineKeyboardButton("🟢 Start", callback_data="start"),
            InlineKeyboardButton("🔴 Stop", callback_data="stop")
        ],
        [InlineKeyboardButton("🔄 Restart", callback_data="restart")],
        [InlineKeyboardButton("📜 Logs", callback_data="logs")],
    ]

    await update.message.reply_text(
        "⚡ Deklan Node Bot — Control Panel",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action = q.data

    if action == "status":
        txt = run("systemctl status gensyn --no-pager")
        await q.edit_message_text(f"📊 *STATUS:*\n```\n{txt}\n```", parse_mode="Markdown")

    elif action == "start":
        run("systemctl start gensyn")
        await q.edit_message_text("🟢 Node started")

    elif action == "stop":
        run("systemctl stop gensyn")
        await q.edit_message_text("🔴 Node stopped")

    elif action == "restart":
        run("systemctl restart gensyn")
        await q.edit_message_text("🔄 Node restarted")

    elif action == "logs":
        txt = run("journalctl -u gensyn -n 30 --no-pager")
        await q.edit_message_text(f"📜 *LOGS:*\n```\n{txt}\n```", parse_mode="Markdown")


# --- Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    print("✅ BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
