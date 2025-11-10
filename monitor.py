import os
import time
import psutil
import subprocess
from datetime import datetime
import urllib.parse
import urllib.request

# ======================================================
# ENV
# ======================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
NODE_NAME = os.getenv("NODE_NAME", "deklan-node")

LOG_LINES = int(os.getenv("LOG_LINES", "80"))
SERVICE = os.getenv("SERVICE_NAME", "gensyn")  # default RL swarm service name


# ======================================================
# SHELL
# ======================================================
def shell(cmd: str) -> str:
    """Execute shell cmd safely."""
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()


# ======================================================
# TELEGRAM
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
    except Exception:
        pass


def clean(text: str) -> str:
    """Prevent Markdown injection."""
    bad = ["`", "*", "_", "["]
    for ch in bad:
        text = text.replace(ch, "")
    return text


# ======================================================
# CHECKS
# ======================================================
def is_active() -> bool:
    """Check if systemd service is active."""
    return shell(f"systemctl is-active {SERVICE}") == "active"


def sys_brief() -> str:
    """CPU / RAM / Disk mini status."""
    try:
        cpu = psutil.cpu_percent(interval=0.4)
        vm = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        return f"CPU {cpu:.1f}% • RAM {vm.percent:.1f}% • Disk {du.percent:.1f}%"
    except:
        return "(sys info unavailable)"


def try_restart() -> bool:
    """Restart service → return success."""
    shell(f"systemctl restart {SERVICE}")
    time.sleep(6)
    return is_active()


def last_round() -> str:
    """Last round log line."""
    line = shell(
        rf"journalctl -u {SERVICE} --no-pager | grep -E 'Joining round:' | tail -n1"
    )
    return line if line else "(round info not found)"


# ======================================================
# MAIN
# ======================================================
def main():
    t = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ✅ Running
    if is_active():
        send(
            f"✅ *{NODE_NAME}* OK @ {t}\n"
            f"{sys_brief()}\n"
            f"{last_round()}"
        )
        return

    # 🚨 DOWN
    send(
        f"🚨 *{NODE_NAME}* DOWN @ {t}\n"
        f"↪ Trying restart…"
    )

    # 🔁 try auto-restart
    if try_restart():
        send(
            f"🟢 *{NODE_NAME}* RECOVERED*\n"
            f"{sys_brief()}"
        )
        return

    # ❌ FAILED RECOVER
    raw_logs = shell(f"journalctl -u {SERVICE} -n {LOG_LINES} --no-pager")
    logs = clean(raw_logs)

    if len(logs) > 3500:
        logs = logs[-3500:]

    send(
        f"❌ *{NODE_NAME}* FAILED RECOVER\n"
        f"🚨 Manual action needed.\n\n"
        f"```\n{logs}\n```"
    )


if __name__ == "__main__":
    main()
