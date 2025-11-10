#!/usr/bin/env python3
import os
import time
import psutil
import subprocess
from datetime import datetime, timedelta
import urllib.parse
import urllib.request
import json


# ======================================================
# ENV
# ======================================================
BOT_TOKEN   = os.getenv("BOT_TOKEN", "")
CHAT_ID     = os.getenv("CHAT_ID", "")
NODE_NAME   = os.getenv("NODE_NAME", "deklan-node")

SERVICE     = os.getenv("SERVICE_NAME", "gensyn")
LOG_LINES   = int(os.getenv("LOG_LINES", "80"))

AUTO_REPO = os.getenv(
    "AUTO_INSTALLER_GITHUB",
    "https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/"
)

RL_DIR  = os.getenv("RL_DIR", "/root/rl_swarm")
KEY_DIR = os.getenv("KEY_DIR", "/root/deklan")

FLAG_FILE = "/tmp/.node_status.json"


# ======================================================
# EXEC / SHELL
# ======================================================
def shell(cmd: str) -> str:
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip()


# ======================================================
# TG SEND
# ======================================================
def send(msg: str):
    """Send Telegram text message."""
    if not (BOT_TOKEN and CHAT_ID):
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    data = urllib.parse.urlencode(payload).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=10)
    except:
        pass


def clean(text: str) -> str:
    for ch in ["`", "*", "_", "["]:
        text = text.replace(ch, "")
    return text


# ======================================================
# STATUS CACHE
# ======================================================
def load_flag():
    if not os.path.isfile(FLAG_FILE):
        return {"last_status": "unknown", "reinstalled": False}
    try:
        return json.load(open(FLAG_FILE))
    except:
        return {"last_status": "unknown", "reinstalled": False}


def save_flag(status: str, reinstalled=False):
    with open(FLAG_FILE, "w") as f:
        json.dump({"last_status": status, "reinstalled": reinstalled}, f)


# ======================================================
# RL-SWARM AUTO FIX
# ======================================================
def fix_keys_symlink():
    """Ensure keys dir inside RL-Swarm points to KEY_DIR."""
    if not os.path.isdir(RL_DIR):
        return

    k = os.path.join(RL_DIR, "keys")
    if os.path.islink(k):
        return

    # try fix
    shell(f"rm -rf {k}")
    shell(f"ln -s {KEY_DIR} {k}")


# ======================================================
# CHECKS
# ======================================================
def is_active() -> bool:
    return shell(f"systemctl is-active {SERVICE}") == "active"


def sys_brief() -> str:
    """CPU / RAM / Disk + uptime."""
    try:
        cpu = psutil.cpu_percent(interval=0.6)
        vm  = psutil.virtual_memory()
        du  = psutil.disk_usage("/")
        uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))

        return (
            f"CPU {cpu:.1f}% • "
            f"RAM {vm.percent:.1f}% • "
            f"Disk {du.percent:.1f}% • "
            f"Up {uptime}"
        )
    except:
        return "(sys info unavailable)"


def last_round() -> str:
    line = shell(
        rf"journalctl -u {SERVICE} --no-pager | grep -E 'Joining round:' | tail -n1"
    )
    return line if line else "(round info not found)"


def try_restart() -> bool:
    shell(f"systemctl restart {SERVICE}")
    time.sleep(6)
    return is_active()


# ======================================================
# AUTO REPAIR
# ======================================================
def try_reinstall():
    tmp = "/tmp/reinstall.sh"
    url = f"{AUTO_REPO}reinstall.sh"

    shell(f"curl -s -o {tmp} {url}")
    shell(f"chmod +x {tmp}")

    return shell(f"bash {tmp}")


# ======================================================
# MAIN
# ======================================================
def main():
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    state = load_flag()

    # fix symlink before checks
    fix_keys_symlink()

    # ✅ Node running
    if is_active():
        if state.get("last_status") != "up":
            send(
                f"✅ *{NODE_NAME}* is UP @ {t}\n"
                f"{sys_brief()}\n"
                f"{last_round()}"
            )
        save_flag("up", False)
        return

    # 🚨 DOWN
    if state.get("last_status") != "down":
        send(
            f"🚨 *{NODE_NAME}* DOWN @ {t}\n"
            f"↪ Trying restart…"
        )

    # 🔁 Try restart
    if try_restart():
        send(
            f"🟢 *{NODE_NAME}* RECOVERED @ {t}\n"
            f"{sys_brief()}"
        )
        save_flag("up", False)
        return

    # 🔧 Try reinstall once only
    if not state.get("reinstalled", False):
        send("⚙️ Restart failed… trying auto reinstall…")
        try_reinstall()
        time.sleep(10)

        if is_active():
            send(
                f"✅ *{NODE_NAME}* RECOVERED AFTER REINSTALL @ {t}\n"
                f"{sys_brief()}"
            )
            save_flag("up", False)
            return
        else:
            save_flag("down", True)

    # ❌ FAILED — fallback, dump logs
    raw_logs = shell(f"journalctl -u {SERVICE} -n {LOG_LINES} --no-pager")
    logs = clean(raw_logs)

    if len(logs) > 3500:
        logs = logs[-3500:]

    send(
        f"❌ *{NODE_NAME}* FAILED RECOVER @ {t}\n"
        f"Manual action required.\n\n"
        f"```\n{logs}\n```"
    )

    save_flag("down", True)


if __name__ == "__main__":
    main()
