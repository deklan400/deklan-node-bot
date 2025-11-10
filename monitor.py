import os, psutil, time, subprocess
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
NODE_NAME = os.getenv("NODE_NAME", "deklan-node")
LOG_LINES = int(os.getenv("LOG_LINES", "50"))

def shell(cmd: str) -> str:
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

def send(msg: str):
    if not (BOT_TOKEN and CHAT_ID):
        return
    import urllib.parse, urllib.request
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}).encode()
    urllib.request.urlopen(url, data=data, timeout=15).read()

def is_active() -> bool:
    return shell("systemctl is-active gensyn") == "active"

def sys_brief() -> str:
    cpu = psutil.cpu_percent(interval=0.4)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return f"CPU {cpu:.0f}% • RAM {ram:.0f}% • Disk {disk:.0f}%"

def try_restart() -> bool:
    shell("systemctl restart gensyn")
    time.sleep(6)
    return is_active()

def last_round() -> str:
    line = shell(r"journalctl -u gensyn --no-pager | grep -E 'Joining round:' | tail -n1")
    return line if line else "(round info not found)"

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if is_active():
        send(f"✅ *{NODE_NAME}* OK @ {now}\n{sys_brief()}\n{last_round()}")
    else:
        send(f"🚨 *{NODE_NAME}* DOWN @ {now}\nAttempting auto-restart…")
        if try_restart():
            send(f"🟢 *{NODE_NAME}* recovered.\n{sys_brief()}")
        else:
            logs = shell(f"journalctl -u gensyn -n {LOG_LINES} --no-pager")
            if len(logs) > 3500: logs = logs[-3500:]
            send(f"❌ *{NODE_NAME}* FAILED TO RECOVER.\nCheck logs:\n```\n{logs}\n```")

if __name__ == "__main__":
    main()
