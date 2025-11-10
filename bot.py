import os
import time
import psutil
import subprocess
from datetime import timedelta
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)


# =========================
# LOAD ENV
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
NODE_NAME = os.getenv("NODE_NAME", "deklan-node")

SERVICE = os.getenv("SERVICE_NAME", "gensyn")   # Bisa ganti via .env
LOG_LINES = int(os.getenv("LOG_LINES", "80"))

ALLOWED_USER_IDS = [
    i.strip() for i in os.getenv("ALLOWED_USER_IDS", "").split(",") if i.strip()
]


# =========================
# VALIDATION
# =========================
if not BOT_TOKEN or not CHAT_ID:
    raise SystemExit("❌ BOT_TOKEN / CHAT_ID belum di-set. Edit .env lalu restart bot.")


# =========================
# HELPERS
# =========================
def _shell(cmd: str) -> str:
    """Run shell cmd safely & return string."""
    try:
        out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        )
        return out.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()


def _authorized(update: Update) -> bool:
    """Validate user access."""
    uid = str(update.effective_user.id)
    if str(update.effective_chat.id) != str(CHAT_ID):
        return False
    return (not ALLOWED_USER_IDS) or (uid in ALLOWED_USER_IDS) or (uid == str(CHAT_ID))


def _service_active() -> bool:
    return _shell(f"systemctl is-active {SERVICE}") == "active"


def _service_logs(n: int) -> str:
    return _shell(f"journalctl -u {SERVICE} -n {n} --no-pager")


def _service_restart():
    return _shell(f"systemctl restart {SERVICE}")


def _service_start():
    return _shell(f"systemctl start {SERVICE}")


def _service_stop():
    return _shell(f"systemctl stop {SERVICE}")


def _round_info() -> str:
    line = _shell(
        rf"journalctl -u {SERVICE} --no-pager | grep -E 'Joining round:' | tail -n1"
    )
    return line if line else "(round info not found)"


def _sys_stats() -> str:
    """Hardware stats & uptime"""
    try:
        cpu = psutil.cpu_percent(interval=0.6)
        vm = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        uptime_sec = time.time() - psutil.boot_time()
        up = str(timedelta(seconds=int(uptime_sec)))
        return (
            f"CPU  : {cpu:.1f}%\n"
            f"RAM  : {vm.percent:.1f}% ({vm.used//(1024**3)}G / {vm.total//(1024**3)}G)\n"
            f"Disk : {du.percent:.1f}% ({du.used//(1024**3)}G / {du.total//(1024**3)}G)\n"
            f"Uptime: {up}"
        )
    except:
        return "(System stats unavailable)"


# =========================
# MENU
# =========================
def _main_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📊 Status", callback_data="status")],
            [
                InlineKeyboardButton("🟢 Start", callback_data="start"),
                InlineKeyboardButton("🔴 Stop", callback_data="stop"),
            ],
            [InlineKeyboardButton("🔁 Restart", callback_data="restart")],
            [InlineKeyboardButton("📜 Logs", callback_data="logs")],
            [InlineKeyboardButton("ℹ️ Round", callback_data="round")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
        ]
    )


# =========================
# HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")
    await update.message.reply_text(
        f"⚡ *{NODE_NAME}* — Control Panel",
        parse_mode="Markdown",
        reply_markup=_main_menu(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")
    msg = (
        "✅ *Commands:*\n"
        "/start → menu\n"
        "/status → stats\n"
        "/logs → last logs\n"
        "/restart → restart node\n"
        "/round → last round info\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not _authorized(update):
        return await q.edit_message_text("❌ Unauthorized.")

    action = q.data

    # Status
    if action == "status":
        active = _service_active()
        badge = "✅ RUNNING" if active else "⛔ STOPPED"
        msg = f"📟 *{NODE_NAME}*\nStatus: *{badge}*\n\n{_sys_stats()}"
        return await q.edit_message_text(msg, parse_mode="Markdown", reply_markup=_main_menu())

    # Start
    if action == "start":
        _service_start()
        return await q.edit_message_text("🟢 Starting…", reply_markup=_main_menu())

    # Stop
    if action == "stop":
        _service_stop()
        return await q.edit_message_text("🔴 Stopping…", reply_markup=_main_menu())

    # Restart
    if action == "restart":
        _service_restart()
        return await q.edit_message_text("🔁 Restarting…", reply_markup=_main_menu())

    # Logs
    if action == "logs":
        logs = _service_logs(LOG_LINES)
        if len(logs) > 3600:
            logs = logs[-3600:]
        return await q.edit_message_text(
            f"📜 *Last {LOG_LINES} lines*\n```\n{logs}\n```",
            parse_mode="Markdown",
            reply_markup=_main_menu(),
        )

    # Round
    if action == "round":
        info = _round_info()
        return await q.edit_message_text(
            f"ℹ️ *Round Info*\n```\n{info}\n```",
            parse_mode="Markdown",
            reply_markup=_main_menu(),
        )

    # Help
    if action == "help":
        return await q.edit_message_text(
            "✅ *Commands:*\n"
            "/start → menu\n"
            "/status → stats\n"
            "/logs → last logs\n"
            "/restart → restart node\n"
            "/round → last round info\n",
            parse_mode="Markdown",
            reply_markup=_main_menu(),
        )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")
    active = _service_active()
    badge = "✅ RUNNING" if active else "⛔ STOPPED"
    await update.message.reply_text(
        f"📟 *{NODE_NAME}*\nStatus: *{badge}*\n\n{_sys_stats()}",
        parse_mode="Markdown",
    )


# =========================
# CORE
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("✅ Bot running…")
    app.run_polling()


if __name__ == "__main__":
    main()
