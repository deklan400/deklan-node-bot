#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═════════════════════════════════════════════════════════════════════════════
        ⚡ DEKLAN-SUITE BOT v3.5 EXTENDED CINEMATIC MODE ⚡
─────────────────────────────────────────────────────────────────────────────
 Unified Node Manager + Telegram Control + Auto Notify + Auto Update System
─────────────────────────────────────────────────────────────────────────────
   🧠  Developer : Deklan × GPT-5
   🧩  Project   : Deklan-Suite (All-in-One Smart Node Manager)
   ⚙️  Stack     : Python + Telegram Bot API + Linux Systemd + Docker
═════════════════════════════════════════════════════════════════════════════
"""

import os
import time
import subprocess
import psutil
from datetime import timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ╔════════════════════════════════════════════════════════════╗
# ║                    🧠 ENVIRONMENT SETUP                    ║
# ╚════════════════════════════════════════════════════════════╝

env = os.getenv
BOT_TOKEN = env("BOT_TOKEN", "")
CHAT_ID   = str(env("CHAT_ID", ""))
NODE_NAME = env("NODE_NAME", "deklan-node")
SERVICE_NODE = env("SERVICE_NAME", "gensyn")
LOG_LINES = int(env("LOG_LINES", "80"))
RL_DIR    = env("RL_DIR", "/root/rl-swarm")
KEY_DIR   = env("KEY_DIR", "/root/deklan")
AUTO_REPO = env("AUTO_INSTALLER_GITHUB", "https://raw.githubusercontent.com/deklan400/deklan-suite/main/")
LOG_MAX   = int(env("LOG_MAX_CHARS", "3500"))
ALLOWED_USER_IDS = [i.strip() for i in env("ALLOWED_USER_IDS", "").split(",") if i.strip()]
ENABLE_DANGER = env("ENABLE_DANGER_ZONE", "0") == "1"
DANGER_PASS   = env("DANGER_PASS", "")

if not BOT_TOKEN or not CHAT_ID:
    raise SystemExit("❌ BOT_TOKEN / CHAT_ID missing — edit .env and restart bot")

# ╔════════════════════════════════════════════════════════════╗
# ║                   ⚙️ UTILITY FUNCTIONS                    ║
# ╚════════════════════════════════════════════════════════════╝

def _shell(cmd: str) -> str:
    """Run shell command and return stdout"""
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True).strip()
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip()

def _authorized(update: Update) -> bool:
    """Check if user is allowed to control bot"""
    uid = str(update.effective_user.id)
    if str(update.effective_chat.id) != CHAT_ID:
        return False
    if not ALLOWED_USER_IDS:
        return uid == CHAT_ID
    return uid == CHAT_ID or uid in ALLOWED_USER_IDS

async def _send_long(upd_msg, text: str):
    """Send long text messages (split automatically to avoid Telegram error)"""
    CHUNK = 3800
    parts = [text[i:i+CHUNK] for i in range(0, len(text), CHUNK)]
    first = True
    for p in parts:
        if first and hasattr(upd_msg, "edit_message_text"):
            await upd_msg.edit_message_text(p, parse_mode="Markdown")
            first = False
        else:
            await upd_msg.message.reply_text(p, parse_mode="Markdown")

# ╔════════════════════════════════════════════════════════════╗
# ║                    🔧 SYSTEM OPERATIONS                    ║
# ╚════════════════════════════════════════════════════════════╝

def _stats() -> str:
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        vm = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        uptime = str(timedelta(seconds=int(time.time() - psutil.boot_time())))
        return f"CPU: {cpu:.1f}%\nRAM: {vm.percent:.1f}%\nDisk: {du.percent:.1f}%\nUptime: {uptime}"
    except Exception:
        return "(system stats unavailable)"

def _logs() -> str:
    return _shell(f"journalctl -u {SERVICE_NODE} -n {LOG_LINES} --no-pager")[:LOG_MAX]

def _round():
    cmd = f"journalctl -u {SERVICE_NODE} --no-pager | grep -E 'Joining round:' | tail -n1"
    return _shell(cmd) or "(round info not found)"

def _clean():
    cmds = [
        "docker image prune -f",
        "docker container prune -f",
        "apt autoremove -y",
        "apt clean",
        "journalctl --vacuum-size=200M",
        "rm -rf /tmp/*"
    ]
    for c in cmds: _shell(c)
    return "🧹 System cleaned successfully"

def _run_remote(fname: str) -> str:
    url = f"{AUTO_REPO}{fname}"
    tmp = f"/tmp/{fname}"
    try:
        subprocess.check_output(f"curl -s -o {tmp} {url}", shell=True)
        subprocess.check_output(f"chmod +x {tmp}", shell=True)
        return subprocess.check_output(f"bash {tmp}", shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        return e.output or "ERR"

def _notify(title: str, msg: str):
    """Send Telegram notify"""
    if not BOT_TOKEN or not CHAT_ID:
        return
    text = f"⚙️ *Deklan-Suite Auto Report*\n━━━━━━━━━━━━━━\n🖥 Host: `{os.uname().nodename}`\n🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}\n━━━━━━━━━━━━━━\n*{title}*\n```\n{msg[:1800]}\n```"
    _shell(f"curl -s -X POST 'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage' -d chat_id={CHAT_ID} -d parse_mode=Markdown -d text=\"{text}\" >/dev/null 2>&1 || true")

# ╔════════════════════════════════════════════════════════════╗
# ║                    🎛 CINEMATIC STATUS PANEL                ║
# ╚════════════════════════════════════════════════════════════╝

def _bar(v: str) -> str:
    try:
        val = float("".join(c for c in v if (c.isdigit() or c == ".")))
        filled = int(round(val / 10))
        filled = max(0, min(10, filled))
        return "◼" * filled + "◻" * (10 - filled)
    except:
        return "◻" * 10

def _panel(name: str, service: str, stats: str, rnd: str) -> str:
    d = {}
    for ln in stats.splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            d[k.strip()] = v.strip()
    cpu, ram, disk, up = d.get("CPU", "0%"), d.get("RAM", "0%"), d.get("Disk", "0%"), d.get("Uptime", "--")
    cpu_b, ram_b, disk_b = _bar(cpu), _bar(ram), _bar(disk)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    return f"""```
████  DEKLAN-SUITE STATUS DASHBOARD  ████

 Node       : {name}
 Service    : {service}
 Status     : ✅ RUNNING
 Round      : {rnd}
 Uptime     : {up}

 ── Resources ───────────────
 CPU        : {cpu:<8} {cpu_b}
 RAM        : {ram:<8} {ram_b}
 Disk       : {disk:<8} {disk_b}

 ── System ─────────────────
 Identity   : {'✅ Valid' if os.path.isdir(KEY_DIR) else '⚠ Missing'}
 Docker     : {'✅ OK' if 'docker' in _shell('which docker || echo') else '⚠ N/A'}

 Last Sync  : {ts}
```"""

# ╔════════════════════════════════════════════════════════════╗
# ║                        🕹️ MAIN MENU                        ║
# ╚════════════════════════════════════════════════════════════╝

def _main_menu():
    rows = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("🟢 Start", callback_data="start"),
         InlineKeyboardButton("🔴 Stop", callback_data="stop")],
        [InlineKeyboardButton("🔁 Restart", callback_data="restart")],
        [InlineKeyboardButton("📜 Logs", callback_data="logs")],
        [InlineKeyboardButton("🧩 Installer", callback_data="installer")],
        [InlineKeyboardButton("🧹 Clean", callback_data="clean")],
        [InlineKeyboardButton("⚙ Auto-Update", callback_data="update_check")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    if ENABLE_DANGER:
        rows.append([InlineKeyboardButton("⚠️ Danger Zone", callback_data="danger")])
    return InlineKeyboardMarkup(rows)

def _installer_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Install", callback_data="inst_install")],
        [InlineKeyboardButton("🔄 Reinstall", callback_data="inst_reinstall")],
        [InlineKeyboardButton("♻ Update", callback_data="inst_update")],
        [InlineKeyboardButton("🧹 Uninstall", callback_data="inst_uninstall")],
        [InlineKeyboardButton("⬅ Back", callback_data="back")]
    ])

def _danger_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Remove Node", callback_data="dz_rm_node")],
        [InlineKeyboardButton("🐋 Clean Docker", callback_data="dz_rm_docker")],
        [InlineKeyboardButton("💾 Remove Swap", callback_data="dz_rm_swap")],
        [InlineKeyboardButton("🧹 Full Clean", callback_data="dz_clean_all")],
        [InlineKeyboardButton("💣 Reboot VPS", callback_data="dz_reboot")],
        [InlineKeyboardButton("⬅ Back", callback_data="back")]
    ])

# ╔════════════════════════════════════════════════════════════╗
# ║                    🎯 CALLBACK HANDLER                     ║
# ╚════════════════════════════════════════════════════════════╝

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not _authorized(update):
        return await q.edit_message_text("❌ Unauthorized access.")
    a = q.data

    if a == "status":
        panel = _panel(NODE_NAME, SERVICE_NODE, _stats(), _round())
        return await q.edit_message_text(panel, parse_mode="Markdown", reply_markup=_main_menu())
    if a in ["start", "stop", "restart"]:
        _shell(f"systemctl {a} {SERVICE_NODE}")
        _notify(f"Node {a.title()}ed", f"{SERVICE_NODE} service {a} complete.")
        return await q.edit_message_text(f"✅ Node {a} executed.", reply_markup=_main_menu())
    if a == "logs":
        return await _send_long(q, f"📜 Logs\n```\n{_logs()}\n```")
    if a == "clean":
        res = _clean(); _notify("🧹 Clean Done", res)
        return await q.edit_message_text(res, reply_markup=_main_menu())
    if a == "installer":
        return await q.edit_message_text("🧩 *Smart Installer*", parse_mode="Markdown", reply_markup=_installer_menu())
    if a.startswith("inst_"):
        m = a.split("_", 1)[1]
        f = {"install":"install.sh","reinstall":"reinstall.sh","update":"update.sh","uninstall":"uninstall.sh"}.get(m)
        r = _run_remote(f); _notify(f"⚙️ {m.title()} Done", r[:800])
        return await _send_long(q, f"✅ {m.upper()} Completed\n```\n{r}\n```")
    if a == "update_check":
        r = _run_remote("autoupdate.sh")
        return await _send_long(q, f"🔎 *Auto-Update Check*\n```\n{r}\n```")
    if a == "danger":
        return await q.edit_message_text("⚠️ *Danger Zone*", parse_mode="Markdown", reply_markup=_danger_menu())
    if a.startswith("dz_"):
        context.user_data["awaiting_password"] = a
        return await q.edit_message_text(f"⚠️ `{a.replace('dz_','').upper()}` — Enter Danger Password:", parse_mode="Markdown")
    if a == "back":
        return await q.edit_message_text("⚡ Main Menu", reply_markup=_main_menu())

# ╔════════════════════════════════════════════════════════════╗
# ║                    💬 TEXT INPUT HANDLER                   ║
# ╚════════════════════════════════════════════════════════════╝

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if "awaiting_password" in context.user_data:
        act = context.user_data.pop("awaiting_password")
        if txt != DANGER_PASS:
            return await update.message.reply_text("❌ Wrong password")
        await update.message.reply_text("✅ Verified! Running…")
        if act == "dz_rm_node":
            r = _shell(f"systemctl stop {SERVICE_NODE}; rm -rf {RL_DIR}")
        elif act == "dz_rm_docker":
            r = _shell("docker system prune -af")
        elif act == "dz_rm_swap":
            r = _shell("swapoff -a; rm -f /swapfile; sed -i '/swapfile/d' /etc/fstab")
        elif act == "dz_clean_all":
            r = _shell(f"systemctl stop {SERVICE_NODE}; rm -rf {RL_DIR}; docker system prune -af; swapoff -a; rm -f /swapfile")
        elif act == "dz_reboot":
            r = "Rebooting VPS…"; _shell("reboot")
        else:
            r = "Unknown danger action"
        _notify("⚠️ Danger Executed", r)
        return await _send_long(update, f"✅ Done\n```\n{r}\n```")

# ╔════════════════════════════════════════════════════════════╗
# ║                      🚀 MAIN EXECUTION                     ║
# ╚════════════════════════════════════════════════════════════╝

def main():
    print("\n═══════════════════════════════════════════════════")
    print("🚀 DEKLAN-SUITE BOT v3.5 EXTENDED CINEMATIC MODE ON")
    print("═══════════════════════════════════════════════════\n")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
