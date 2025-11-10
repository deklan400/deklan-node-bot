import os
import time
import psutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
NODE_NAME = os.getenv("NODE_NAME", "deklan-node")

LOG_LINES = int(os.getenv("LOG_LINES", "80"))
SERVICE = os.getenv("SERVICE_NAME", "gensyn")  # RL-Swarm Service


# =========================
# UTILS
# =========================
def shell(cmd: str) -> str:
    """Run shell cmd safely & return stdout."""
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()


def send(msg: str):
    """Send text message to Telegram."""
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


def clean_markdown(text: str) -> str:
    """Prevent Markdown injection from logs."""
    bad = ["`", "*", "_", "["]
    for ch in bad:
        text = text.replace(ch, "")
    return text


def is_active() -> bool:
    """Check RL service running."""
    return shell(f"systemctl is-active {SERVICE}") == "active"


def sys_brief() -> str:
    """Short CPU / RAM / Disk report."""
    try:
        cpu = psutil.cpu_percent(interval=0.4)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        return f"CPU {cpu:.0f}% • RAM {ram:.0f}% • Disk {disk:.0f}%"
    except:
        return "(sys info unavailable)"


def try_restart() -> bool:
    """Restart service & return success state."""
    shell(f"systemctl restart {SERVICE}")
    time.sleep(6)
    return is_active()


def last_round() -> str:
    """Parse round logs."""
    line = shell(
        rf"journalctl -u {SERVICE} --no-pager | grep -E 'Joining round:' | tail -n1"
    )
    return line if line else "(round info not found)"


# =========================
# MAIN
# =========================
def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ✅ Node running
    if is_active():
        send(f"✅ *{NODE_NAME}* OK @ {now}\n{sys_brief()}\n{last_round()}")
        return

    # ⚠️ Node DOWN
    send(f"🚨 *{NODE_NAME}* DOWN @ {now}\nAttempting auto-restart…")

    # Try restart
    if try_restart():
        send(f"🟢 *{NODE_NAME}* RECOVERED\n{sys_brief()}")
        return

    # ❌ Failed to recover — post short logs
    raw = shell(f"journalctl -u {SERVICE} -n {LOG_LINES} --no-pager")
    logs = clean_markdown(raw)
    if len(logs) > 3000:
        logs = logs[-3000:]

    send(
        f"❌ *{NODE_NAME}* FAILED TO RECOVER\n"
        f"Check logs:\n"
        f"```\n{logs}\n```"
    )


if __name__ == "__main__":
    main()
