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

SERVICE = os.getenv("SERVICE_NAME", "gensyn")   # Bisa pakai .env


# =========================
# UTILS
# =========================
def shell(cmd: str) -> str:
    try:
        out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        )
        return out.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()


def send(msg: str):
    """Send message to Telegram"""
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
    except Exception as e:
        print("Telegram send error:", e)


def is_active() -> bool:
    return shell(f"systemctl is-active {SERVICE}") == "active"


def sys_brief() -> str:
    try:
        cpu = psutil.cpu_percent(interval=0.4)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        return f"CPU {cpu:.0f}% • RAM {ram:.0f}% • Disk {disk:.0f}%"
    except Exception:
        return "(sys info unavailable)"


def try_restart() -> bool:
    shell(f"systemctl restart {SERVICE}")
    time.sleep(6)
    return is_active()


def last_round() -> str:
    line = shell(
        rf"journalctl -u {SERVICE} --no-pager | grep -E 'Joining round:' | tail -n1"
    )
    return line if line else "(round info not found)"


# =========================
# MAIN
# =========================
def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if is_active():
        msg = f"✅ *{NODE_NAME}* OK @ {now}\n{sys_brief()}\n{last_round()}"
        send(msg)
        return

    # If down
    send(f"🚨 *{NODE_NAME}* DOWN @ {now}\nAttempting auto-restart…")

    if try_restart():
        send(f"🟢 *{NODE_NAME}* RECOVERED\n{sys_brief()}")
        return

    # If restart failed
    logs = shell(f"journalctl -u {SERVICE} -n {LOG_LINES} --no-pager")
    logs = logs[-3500:] if len(logs) > 3500 else logs

    send(f"❌ *{NODE_NAME}* FAILED TO RECOVER\n"
         f"Check last logs:\n```\n{logs}\n```")


if __name__ == "__main__":
    main()
