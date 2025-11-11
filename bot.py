#!/usr/bin/env python3
import os
import time
import subprocess
import psutil
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
    MessageHandler,
    ContextTypes,
    filters,
)

# ======================================================
# ENV / CONFIG
# ======================================================
env = os.getenv

BOT_TOKEN = env("BOT_TOKEN", "")
CHAT_ID = str(env("CHAT_ID", ""))

NODE_NAME = env("NODE_NAME", "deklan-node")

SERVICE = env("SERVICE_NAME", "gensyn")
LOG_LINES = int(env("LOG_LINES", "80"))

RL_DIR = env("RL_DIR", "/root/rl_swarm")
KEY_DIR = env("KEY_DIR", "/root/deklan")

ROUND_GREP = env("ROUND_GREP_PATTERN", "Joining round:")

LOG_MAX = int(env("LOG_MAX_CHARS", "3500"))

MONITOR_TRY_REINSTALL = env("MONITOR_TRY_REINSTALL", "1") == "1"

ALLOWED_USER_IDS = [
    i.strip() for i in env("ALLOWED_USER_IDS", "").split(",") if i.strip()
]

ENABLE_DANGER = env("ENABLE_DANGER_ZONE", "0") == "1"
DANGER_PASS = env("DANGER_PASS", "")

AUTO_REPO = env(
    "AUTO_INSTALLER_GITHUB",
    "https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/"
)

if not BOT_TOKEN or not CHAT_ID:
    raise SystemExit("❌ BOT_TOKEN / CHAT_ID missing — set .env then restart bot")

# ======================================================
# HELPERS
# ======================================================
def _shell(cmd: str) -> str:
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip()


def _authorized(update: Update) -> bool:
    uid = str(update.effective_user.id)
    if str(update.effective_chat.id) != CHAT_ID:
        return False
    if not ALLOWED_USER_IDS:
        return uid == CHAT_ID
    return uid == CHAT_ID or uid in ALLOWED_USER_IDS


async def _send_long(update_or_query, text: str, parse_mode="Markdown"):
    CHUNK = 3800
    if len(text) <= CHUNK:
        if hasattr(update_or_query, "edit_message_text"):
            return await update_or_query.edit_message_text(text, parse_mode=parse_mode)
        return await update_or_query.message.reply_text(text, parse_mode=parse_mode)

    parts = [text[i:i + CHUNK] for i in range(0, len(text), CHUNK)]

    if hasattr(update_or_query, "edit_message_text"):
        await update_or_query.edit_message_text(parts[0], parse_mode=parse_mode)
    else:
        await update_or_query.message.reply_text(parts[0], parse_mode=parse_mode)

    for p in parts[1:]:
        await update_or_query.message.reply_text(p, parse_mode=parse_mode)


# ======================================================
# SYSTEMD OPS
# ======================================================
def _service_active() -> bool:
    return _shell(f"systemctl is-active {SERVICE}") == "active"


def _logs(n: int) -> str:
    return _shell(f"journalctl -u {SERVICE} -n {n} --no-pager")


def _restart():
    return _shell(f"systemctl restart {SERVICE}")


def _start():
    return _shell(f"systemctl start {SERVICE}")


def _stop():
    return _shell(f"systemctl stop {SERVICE}")


def _round():
    cmd = rf"journalctl -u {SERVICE} --no-pager | grep -E '{ROUND_GREP}' | tail -n1"
    return _shell(cmd) or "(round info not found)"


def _stats():
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        vm = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        uptime_sec = time.time() - psutil.boot_time()
        up = str(timedelta(seconds=int(uptime_sec)))

        return (
            f"CPU   : {cpu:.1f}%\n"
            f"RAM   : {vm.percent:.1f}% ({vm.used//(1024**3)}G/{vm.total//(1024**3)}G)\n"
            f"Disk  : {du.percent:.1f}% ({du.used//(1024**3)}G/{du.total//(1024**3)}G)\n"
            f"Uptime: {up}"
        )
    except:
        return "(system stats unavailable)"


# ======================================================
# REMOTE SCRIPT EXEC
# ======================================================
def _run_remote(fname: str) -> str:
    url = f"{AUTO_REPO}{fname}"
    tmp = f"/tmp/{fname}"
    try:
        subprocess.check_output(f"curl -s -o {tmp} {url}", shell=True)
        subprocess.check_output(f"chmod +x {tmp}", shell=True)
        return subprocess.check_output(
            f"bash {tmp}",
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        )
    except subprocess.CalledProcessError as e:
        return e.output or "ERR"


# ======================================================
# MENUS
# ======================================================
def _installer_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Install Node",   callback_data="inst_install")],
        [InlineKeyboardButton("🔄 Reinstall Node", callback_data="inst_reinstall")],
        [InlineKeyboardButton("♻ Update Node",     callback_data="inst_update")],
        [InlineKeyboardButton("🧹 Uninstall Node", callback_data="inst_uninstall")],
        [InlineKeyboardButton("⬅ Back",            callback_data="back")],
    ])


def _main_menu():
    rows = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [
            InlineKeyboardButton("🟢 Start", callback_data="start"),
            InlineKeyboardButton("🔴 Stop",  callback_data="stop"),
        ],
        [InlineKeyboardButton("🔁 Restart",   callback_data="restart")],
        [InlineKeyboardButton("📜 Logs",      callback_data="logs")],
        [InlineKeyboardButton("ℹ️ Round",     callback_data="round")],
        [InlineKeyboardButton("🧩 Installer", callback_data="installer")],
        [InlineKeyboardButton("❓ Help",      callback_data="help")],
    ]

    if ENABLE_DANGER:
        rows.append([InlineKeyboardButton("⚠️ Danger Zone", callback_data="dz")])

    return InlineKeyboardMarkup(rows)


def _danger_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Remove RL-Swarm", callback_data="dz_rm_node")],
        [InlineKeyboardButton("🐋 Clean Docker",    callback_data="dz_rm_docker")],
        [InlineKeyboardButton("💾 Remove Swap",     callback_data="dz_rm_swap")],
        [InlineKeyboardButton("🧹 Full Clean",      callback_data="dz_clean_all")],
        [InlineKeyboardButton("🔁 Reboot VPS",      callback_data="dz_reboot")],
        [InlineKeyboardButton("⬅ Back",             callback_data="back")],
    ])


# ======================================================
# HANDLERS
# ======================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")

    await update.message.reply_text(
        f"⚡ *{NODE_NAME}* Control Panel",
        parse_mode="Markdown",
        reply_markup=_main_menu(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")

    await update.message.reply_text(
        "✅ *Commands:*\n"
        "/start → menu\n"
        "/status → stats\n"
        "/logs → last logs\n"
        "/restart → restart node\n"
        "/round → last round info\n",
        parse_mode="Markdown"
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")

    badge = "✅ RUNNING" if _service_active() else "⛔ STOPPED"

    await update.message.reply_text(
        f"📟 *{NODE_NAME}*\nStatus: *{badge}*\n\n{_stats()}",
        parse_mode="Markdown",
        reply_markup=_main_menu(),
    )


async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")

    logs = _logs(LOG_LINES)
    logs = logs[-LOG_MAX:] if len(logs) > LOG_MAX else logs
    await _send_long(update, f"📜 *Last {LOG_LINES} lines*\n```\n{logs}\n```", parse_mode="Markdown")


async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")

    _restart()
    await update.message.reply_text("🔁 Restarting…", reply_markup=_main_menu())


async def cmd_round(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")

    info = _round()
    await update.message.reply_text(
        f"ℹ️ *Last Round*\n```\n{info}\n```",
        parse_mode="Markdown",
        reply_markup=_main_menu(),
    )


# ======================================================
# BUTTON HANDLER
# ======================================================
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not _authorized(update):
        return await q.edit_message_text("❌ Unauthorized.")

    action = q.data

    if action == "installer":
        return await q.edit_message_text(
            "🧩 *Installer Menu*",
            parse_mode="Markdown",
            reply_markup=_installer_menu()
        )

    # INSTALL FLOW
    if action.startswith("inst_"):
        mode = action.split("_")[1]
        context.user_data["pending_inst"] = mode
        return await q.edit_message_text(
            f"⚠ Confirm `{mode.upper()}`?\n\nType *YES* or NO.",
            parse_mode="Markdown"
        )

    # Danger Zone main
    if action == "dz":
        return await q.edit_message_text(
            "⚠️ *Danger Zone — Password Required*",
            parse_mode="Markdown",
            reply_markup=_danger_menu()
        )

    # Danger Zone password
    if action.startswith("dz_"):
        context.user_data["awaiting_password"] = action
        return await q.edit_message_text(
            f"⚠️ `{action.replace('dz_', '').upper()}` — Enter Password:",
            parse_mode="Markdown"
        )

    if action == "back":
        return await q.edit_message_text(
            "⚡ Main Menu",
            reply_markup=_main_menu()
        )

    # Node Ops
    if action == "status":
        badge = "✅ RUNNING" if _service_active() else "⛔ STOPPED"
        return await q.edit_message_text(
            f"📟 *{NODE_NAME}*\nStatus: *{badge}*\n\n{_stats()}",
            parse_mode="Markdown",
            reply_markup=_main_menu()
        )

    if action == "start":
        _start()
        return await q.edit_message_text("🟢 Starting…", reply_markup=_main_menu())

    if action == "stop":
        _stop()
        return await q.edit_message_text("🔴 Stopping…", reply_markup=_main_menu())

    if action == "restart":
        _restart()
        return await q.edit_message_text("🔁 Restarting…", reply_markup=_main_menu())

    if action == "logs":
        logs = _logs(LOG_LINES)
        logs = logs[-LOG_MAX:] if len(logs) > LOG_MAX else logs
        return await _send_long(
            q, f"📜 *Last {LOG_LINES} lines*\n```\n{logs}\n```",
            parse_mode="Markdown"
        )

    if action == "round":
        info = _round()
        return await q.edit_message_text(
            f"ℹ️ *Last Round*\n```\n{info}\n```",
            parse_mode="Markdown",
            reply_markup=_main_menu(),
        )

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


# ======================================================
# TEXT (for Installer & Danger validation)
# ======================================================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # INSTALL CONFIRM
    if "pending_inst" in context.user_data:
        mode = context.user_data.pop("pending_inst")

        if text.upper() != "YES":
            return await update.message.reply_text("❌ Cancelled.")

        await update.message.reply_text(f"⚙ Running {mode.upper()}…")

        script_map = {
            "install":   "install.sh",
            "reinstall": "reinstall.sh",
            "update":    "update.sh",
            "uninstall": "uninstall.sh",
        }

        fname = script_map.get(mode, "install.sh")
        result = _run_remote(fname)

        if len(result) > LOG_MAX:
            result = result[-LOG_MAX:]

        return await _send_long(update, f"✅ Done\n```\n{result}\n```", parse_mode="Markdown")

    # Danger Zone
    if "awaiting_password" in context.user_data:
        action = context.user_data.pop("awaiting_password")

        if text != DANGER_PASS:
            return await update.message.reply_text("❌ Wrong password")

        await update.message.reply_text("✅ Verified! Running...")

        if action == "dz_rm_node":
            _shell(f"systemctl stop {SERVICE}; systemctl disable {SERVICE}; rm -f /etc/systemd/system/{SERVICE}.service; systemctl daemon-reload; rm -rf {RL_DIR}")
            res = "Node removed"

        elif action == "dz_rm_docker":
            res = _shell("docker ps -aq | xargs -r docker rm -f; docker system prune -af")

        elif action == "dz_rm_swap":
            res = _shell("swapoff -a; rm -f /swapfile; sed -i '/swapfile/d' /etc/fstab")

        elif action == "dz_clean_all":
            res = _shell(f"systemctl stop {SERVICE}; rm -rf {RL_DIR}; docker system prune -af; swapoff -a; rm -f /swapfile")

        elif action == "dz_reboot":
            _shell("reboot")
            res = "Rebooting…"

        else:
            res = "Unknown action"

        return await _send_long(update, f"✅ Done\n```\n{res}\n```", parse_mode="Markdown")

    return


# ======================================================
# MAIN
# ======================================================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("help",     cmd_help))
    app.add_handler(CommandHandler("status",   cmd_status))
    app.add_handler(CommandHandler("logs",     cmd_logs))
    app.add_handler(CommandHandler("restart",  cmd_restart))
    app.add_handler(CommandHandler("round",    cmd_round))

    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Bot running…")
    app.run_polling()


if __name__ == "__main__":
    main()
