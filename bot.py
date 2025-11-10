import os
import psutil
import time
import subprocess
from datetime import timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
ALLOWED_USER_IDS = [i.strip() for i in os.getenv("ALLOWED_USER_IDS", "").split(",") if i.strip()]
NODE_NAME = os.getenv("NODE_NAME", "deklan-node")

LOG_LINES = int(os.getenv("LOG_LINES", "50"))

if not BOT_TOKEN or not CHAT_ID:
    raise SystemExit("❌ BOT_TOKEN/CHAT_ID belum di-set. Isi .env lalu restart service.")

def _shell(cmd: str) -> str:
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

def _authorized(update: Update) -> bool:
    uid = str(update.effective_user.id)
    if str(update.effective_chat.id) != str(CHAT_ID):
        return False
    # jika ALLOWED_USER_IDS kosong, pakai CHAT_ID saja
    return (not ALLOWED_USER_IDS) or (uid in ALLOWED_USER_IDS) or (uid == str(CHAT_ID))

def _service_active(service: str) -> bool:
    return _shell(f"systemctl is-active {service}") == "active"

def _service_status(service: str) -> str:
    return _shell(f"systemctl status {service} --no-pager")

def _service_logs(service: str, n: int) -> str:
    return _shell(f"journalctl -u {service} -n {n} --no-pager")

def _round_info() -> str:
    # coba ambil round terakhir dari log
    line = _shell(r"journalctl -u gensyn --no-pager | grep -E 'Joining round:' | tail -n1")
    return line if line else "(round info not found)"

def _sys_stats() -> str:
    cpu = psutil.cpu_percent(interval=0.6)
    vm = psutil.virtual_memory()
    du = psutil.disk_usage("/")
    uptime_sec = time.time() - psutil.boot_time()
    up = str(timedelta(seconds=int(uptime_sec)))
    return (f"CPU  : {cpu:.1f}%\n"
            f"RAM  : {vm.percent:.1f}% (used {vm.used//(1024**3)}G / {vm.total//(1024**3)}G)\n"
            f"Disk : {du.percent:.1f}% (used {du.used//(1024**3)}G / {du.total//(1024**3)}G)\n"
            f"Uptime: {up}")

def _main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("🟢 Start",  callback_data="start"),
         InlineKeyboardButton("🔴 Stop",   callback_data="stop")],
        [InlineKeyboardButton("🔁 Restart", callback_data="restart")],
        [InlineKeyboardButton("📜 Logs",   callback_data="logs")],
        [InlineKeyboardButton("ℹ️ Round",  callback_data="round")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")
    await update.message.reply_text(f"⚡ *{NODE_NAME}* — Control Panel", parse_mode="Markdown", reply_markup=_main_menu())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not _authorized(update):
        return await q.edit_message_text("❌ Unauthorized.")

    action = q.data
    if action == "status":
        active = _service_active("gensyn")
        badge = "✅ RUNNING" if active else "⛔ STOPPED"
        stats = _sys_stats()
        msg = f"📟 *{NODE_NAME}*\nStatus: *{badge}*\n\n{stats}"
        await q.edit_message_text(msg, parse_mode="Markdown", reply_markup=_main_menu())

    elif action == "start":
        _shell("systemctl start gensyn")
        await q.edit_message_text("🟢 Starting…", reply_markup=_main_menu())

    elif action == "stop":
        _shell("systemctl stop gensyn")
        await q.edit_message_text("🔴 Stopping…", reply_markup=_main_menu())

    elif action == "restart":
        _shell("systemctl restart gensyn")
        await q.edit_message_text("🔁 Restarting…", reply_markup=_main_menu())

    elif action == "logs":
        logs = _service_logs("gensyn", LOG_LINES)
        # potong bila terlalu panjang
        if len(logs) > 3600:
            logs = logs[-3600:]
        await q.edit_message_text(f"📜 *Last {LOG_LINES} lines*\n```\n{logs}\n```",
                                  parse_mode="Markdown", reply_markup=_main_menu())

    elif action == "round":
        info = _round_info()
        await q.edit_message_text(f"ℹ️ *Round Info*\n```\n{info}\n```",
                                  parse_mode="Markdown", reply_markup=_main_menu())

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")
    active = _service_active("gensyn")
    badge = "✅ RUNNING" if active else "⛔ STOPPED"
    stats = _sys_stats()
    await update.message.reply_text(f"📟 *{NODE_NAME}*\nStatus: *{badge}*\n\n{stats}",
                                    parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("✅ Bot running…")
    app.run_polling()

if __name__ == "__main__":
    main()
