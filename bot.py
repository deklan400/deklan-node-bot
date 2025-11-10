#!/usr/bin/env python3
import os
import time
import psutil
import subprocess
from datetime import timedelta

# load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

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
BOT_TOKEN   = os.getenv("BOT_TOKEN", "")
CHAT_ID     = str(os.getenv("CHAT_ID", ""))  # numeric string
NODE_NAME   = os.getenv("NODE_NAME", "deklan-node")

SERVICE     = os.getenv("SERVICE_NAME", "gensyn")
LOG_LINES   = int(os.getenv("LOG_LINES", "80"))

RL_DIR      = os.getenv("RL_DIR", "/root/rl_swarm")
KEY_DIR     = os.getenv("KEY_DIR", "/root/deklan")

ALLOWED_USER_IDS = [
    i.strip() for i in os.getenv("ALLOWED_USER_IDS", "").split(",") if i.strip()
]

ENABLE_DANGER = os.getenv("ENABLE_DANGER_ZONE", "0") == "1"
DANGER_PASS   = os.getenv("DANGER_PASS", "")

AUTO_REPO = os.getenv(
    "AUTO_INSTALLER_GITHUB",
    "https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/"
)

if not BOT_TOKEN or not CHAT_ID:
    raise SystemExit("❌ BOT_TOKEN / CHAT_ID missing — set in .env then restart bot")

# ======================================================
# HELPERS
# ======================================================
def _shell(cmd: str) -> str:
    """Run shell command & capture output safely."""
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip()

def _authorized(update: Update) -> bool:
    """Require messages from the configured chat AND allowed users."""
    uid = str(update.effective_user.id)
    if str(update.effective_chat.id) != CHAT_ID:
        return False
    if not ALLOWED_USER_IDS:
        return uid == CHAT_ID
    return uid == CHAT_ID or uid in ALLOWED_USER_IDS

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

def _round() -> str:
    line = _shell(
        rf"journalctl -u {SERVICE} --no-pager | grep -E 'Joining round:' | tail -n1"
    )
    return line if line else "(round info not found)"

def _stats() -> str:
    """CPU / RAM / Disk / Uptime summary."""
    try:
        cpu = psutil.cpu_percent(interval=0.6)
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
    except Exception:
        return "(system stats unavailable)"

# ======================================================
# REMOTE INSTALLER EXECUTION
# ======================================================
def _run_remote(name: str) -> str:
    """Download + execute remote script from autoinstall repo."""
    url = f"{AUTO_REPO}{name}"
    tmp = f"/tmp/{name}"
    try:
        subprocess.check_output(f"curl -s -o {tmp} {url}", shell=True)
        subprocess.check_output(f"chmod +x {tmp}", shell=True)
        out = subprocess.check_output(
            f"bash {tmp}",
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        )
        return out
    except subprocess.CalledProcessError as e:
        return e.output or "error"

# ======================================================
# DANGER ZONE — SAFE VERSIONS (scope only this node)
# ======================================================
def _rm_node():
    cmds = [
        f"systemctl stop {SERVICE} || true",
        f"systemctl disable {SERVICE} || true",
        f"rm -f /etc/systemd/system/{SERVICE}.service",
        "systemctl daemon-reload",
        f"rm -rf {RL_DIR}",
    ]
    return "\n".join(_shell(c) for c in cmds)

def _rm_docker():
    # Only touch images/containers named swarm-cpu
    cmds = [
        "docker ps -a --filter name=swarm-cpu -q | xargs -r docker rm -f",
        "docker images | grep swarm-cpu | awk '{print $3}' | xargs -r docker rmi -f",
    ]
    return "\n".join(_shell(c) for c in cmds)

def _rm_swap():
    cmds = [
        "swapoff -a || true",
        "rm -f /swapfile || true",
        "sed -i '/swapfile/d' /etc/fstab",
    ]
    return "\n".join(_shell(c) for c in cmds)

def _clean_all():
    return "\n".join([_rm_node(), _rm_docker(), _rm_swap()])

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
        [InlineKeyboardButton("📊 Status",  callback_data="status")],
        [InlineKeyboardButton("🟢 Start",   callback_data="start"),
         InlineKeyboardButton("🔴 Stop",    callback_data="stop")],
        [InlineKeyboardButton("🔁 Restart", callback_data="restart")],
        [InlineKeyboardButton("📜 Logs",    callback_data="logs")],
        [InlineKeyboardButton("ℹ️ Round",   callback_data="round")],
        [InlineKeyboardButton("🧩 Installer", callback_data="installer")],
        [InlineKeyboardButton("❓ Help",    callback_data="help")],
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
        "/round → last round info\n"
        "/ping → quick check\n",
        parse_mode="Markdown"
    )

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")
    badge = "✅ RUNNING" if _service_active() else "⛔ STOPPED"
    await update.message.reply_text(
        f"📟 *{NODE_NAME}*\nStatus: *{badge}*\n\n{_stats()}",
        parse_mode="Markdown",
        reply_markup=_main_menu()
    )

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _authorized(update):
        return await update.message.reply_text("❌ Unauthorized.")
    await update.message.reply_text("🏓 pong")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not _authorized(update):
        return await q.edit_message_text("❌ Unauthorized.")

    action = q.data

    # ---------------- INSTALLER ----------------
    if action == "installer":
        return await q.edit_message_text(
            "🧩 *Installer Menu*",
            parse_mode="Markdown",
            reply_markup=_installer_menu()
        )

    if action.startswith("inst_"):
        mode = action.split("_")[1]
        context.user_data["pending_inst"] = mode
        return await q.edit_message_text(
            f"⚠ Confirm `{mode.upper()}`?\n\nType *YES* or NO.",
            parse_mode="Markdown"
        )

    # ---------------- DANGER ZONE -------------
    if action == "dz":
        return await q.edit_message_text(
            "⚠️ *Danger Zone — Password Required*",
            parse_mode="Markdown",
            reply_markup=_danger_menu()
        )

    if action == "back":
        return await q.edit_message_text(
            "⚡ Main Menu",
            reply_markup=_main_menu()
        )

    if action.startswith("dz_"):
        if not DANGER_PASS:
            return await q.edit_message_text("❌ Danger Zone disabled (no password).")
        await q.edit_message_text("Send password:")
        context.user_data["awaiting_password"] = action
        return

    # ---------------- BASIC OPS ---------------
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
        # hard cap to avoid Telegram 4096 char limit
        logs = logs[-3500:] if len(logs) > 3500 else logs
        return await q.edit_message_text(
            f"📜 *Last {LOG_LINES} lines*\n```\n{logs}\n```",
            parse_mode="Markdown",
            reply_markup=_main_menu(),
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
            "/round → last round info\n"
            "/ping → quick check\n",
            parse_mode="Markdown",
            reply_markup=_main_menu(),
        )

# ======================================================
# PASS + INSTALL CONFIRM
# ======================================================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # ===== INSTALLER CONFIRM =====
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

        name = script_map.get(mode, "install.sh")
        result = _run_remote(name)

        if len(result) > 3500:
            result = result[-3500:]

        return await update.message.reply_text(
            f"✅ Done\n```\n{result}\n```",
            parse_mode="Markdown"
        )

    # ===== DANGER ZONE =====
    if "awaiting_password" not in context.user_data:
        return

    action = context.user_data.pop("awaiting_password")

    if text != DANGER_PASS:
        return await update.message.reply_text("❌ Wrong password")

    await update.message.reply_text("✅ Verified! Running...")

    if action == "dz_rm_node":
        res = _rm_node()
    elif action == "dz_rm_docker":
        res = _rm_docker()
    elif action == "dz_rm_swap":
        res = _rm_swap()
    elif action == "dz_clean_all":
        res = _clean_all()
    elif action == "dz_reboot":
        _shell("reboot")
        res = "Rebooting…"
    else:
        res = "Unknown action"

    if len(res) > 3500:
        res = res[-3500:]

    await update.message.reply_text(
        f"✅ Done\n```\n{res}\n```", parse_mode="Markdown"
    )

# ======================================================
# CORE
# ======================================================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("help",    cmd_help))
    app.add_handler(CommandHandler("status",  cmd_status))
    app.add_handler(CommandHandler("ping",    cmd_ping))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Bot running…")
    app.run_polling()

if __name__ == "__main__":
    main()
