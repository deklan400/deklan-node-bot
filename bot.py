import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN belum di-set.")
    print("Silakan export dulu:")
    print('export BOT_TOKEN="TOKEN_BOT_KAMU"')
    exit(1)

MENU_BUTTONS = [
    [InlineKeyboardButton("📊 Status Node", callback_data="status")],
    [InlineKeyboardButton("▶️ Start Node", callback_data="start")],
    [InlineKeyboardButton("⏹ Stop Node", callback_data="stop")],
    [InlineKeyboardButton("🔄 Restart Node", callback_data="restart")],
    [InlineKeyboardButton("📋 Logs", callback_data="logs")],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
    await update.message.reply_text("Selamat datang di *Gensyn Node Bot* ⚡", parse_mode="Markdown", reply_markup=keyboard)

async def button_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data

    if action == "status":
        await query.edit_message_text("📊 Status Node: *ONLINE*", parse_mode="Markdown")

    elif action == "start":
        await query.edit_message_text("▶️ Starting node...")

    elif action == "stop":
        await query.edit_message_text("⏹ Stopping node...")

    elif action == "restart":
        await query.edit_message_text("🔄 Restarting node...")

    elif action == "logs":
        await query.edit_message_text("📋 Fetching logs...")

    else:
        await query.edit_message_text("Tidak dikenal.")

def main():
    print("✅ Bot running...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_action))

    app.run_polling()

if __name__ == "__main__":
    main()
