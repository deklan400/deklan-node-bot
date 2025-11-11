#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Deklan Smart Monitor — v4.5 (FINAL FIXED)
  Auto-Heal • Reinstall • Health Alert • Safe Clean
  by Deklan × GPT-5
"""

import os, time, psutil, subprocess, json, urllib.parse, urllib.request
from datetime import datetime, timedelta


# ======================================================
# ENV
# ======================================================
E = os.getenv

BOT_TOKEN   = E("BOT_TOKEN", "")
CHAT_ID     = E("CHAT_ID", "")
NODE_NAME   = E("NODE_NAME", "deklan-node")

SERVICE     = E("SERVICE_NAME", "gensyn")
LOG_LINES   = int(E("LOG_LINES", "80"))

AUTO_REPO   = E(
    "AUTO_INSTALLER_GITHUB",
    "https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/"
)

# ✅ FIXED → rl-swarm (dash)
RL_DIR      = E("RL_DIR", "/root/rl-swarm")

# ✅ identity folder unchanged
KEY_DIR     = E("KEY_DIR", "/root/deklan")

FLAG_FILE   = "/tmp/.node_status.json"
HEALTH_FILE = "/tmp/.health_alert"

MAX_LOG   = int(E("LOG_MAX_CHARS", "3500"))
MONITOR_TRY_REINSTALL = E("MONITOR_TRY_REINSTALL", "1") == "1"


# ===== HEALTH THRESHOLDS =====
TH_CPU  = int(E("ALERT_CPU",  "85"))
TH_RAM  = int(E("ALERT_RAM",  "85"))
TH_DISK = int(E("ALERT_DISK", "85"))
ALERT_COOLDOWN = int(E("ALERT_COOLDOWN_HOURS", "6"))  # hours


# ======================================================
# SHELL
# ======================================================
def sh(cmd: str) -> str:
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip()


# ======================================================
# TG
# ======================================================
def tg(msg):
    if not (BOT_TOKEN and CHAT_ID):
        return
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    data = urllib.parse.urlencode(payload).encode()
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        urllib.request.urlopen(url, data=data, timeout=10)
    except:
        pass


def clean(txt: str):
    for c in ["`", "*", "_", "["]:
        txt = txt.replace(c, "")
    return txt


# ======================================================
# FLAG
# ======================================================
def flag_load():
    if not os.path.isfile(FLAG_FILE):
        return {"last": "unknown", "once": False}
    try:
        return json.load(open(FLAG_FILE))
    except:
        return {"last": "unknown", "once": False}


def flag_set(s, once=False):
    with open(FLAG_FILE, "w") as f:
        json.dump({"last": s, "once": once}, f)


# ======================================================
# SELF-HEAL
# ======================================================
def fix_keys():
    """Ensure RL_DIR/keys → KEY_DIR"""
    if not os.path.isdir(RL_DIR):
        return
    t = os.path.join(RL_DIR, "keys")
    if os.path.islink(t):
        return
    sh(f"rm -rf {t}")
    sh(f"ln -s {KEY_DIR} {t}")


# ======================================================
# SYSTEMD
# ======================================================
def is_up():
    return sh(f"systemctl is-active {SERVICE}") == "active"


# ======================================================
# SYS INFO
# ======================================================
def sys_brief():
    try:
        cpu = psutil.cpu_percent(interval=0.6)
        vm  = psutil.virtual_memory()
        du  = psutil.disk_usage("/")
        up  = timedelta(seconds=int(time.time() - psutil.boot_time()))
        return (
            f"CPU {cpu:.1f}%  "
            f"RAM {vm.percent:.1f}% "
            f"Disk {du.percent:.1f}% "
            f"UP {up}"
        )
    except:
        return "(stats unavailable)"


def last_round():
    s = r"journalctl -u %s --no-pager | grep -E 'Joining round:' | tail -n1" % SERVICE
    out = sh(s)
    return out if out else "(no round info)"


# ======================================================
# HEALTH ALERT
# ======================================================
def health_need():
    cpu = psutil.cpu_percent(interval=0.4)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    bad = []
    if cpu > TH_CPU:
        bad.append(f"CPU {cpu:.1f}% > {TH_CPU}%")
    if ram > TH_RAM:
        bad.append(f"RAM {ram:.1f}% > {TH_RAM}%")
    if disk > TH_DISK:
        bad.append(f"Disk {disk:.1f}% > {TH_DISK}%")

    return bad


def health_allowed():
    if not os.path.isfile(HEALTH_FILE):
        return True
    t = os.path.getmtime(HEALTH_FILE)
    diff = time.time() - t
    return diff > ALERT_COOLDOWN * 3600


def health_mark():
    with open(HEALTH_FILE, "w") as f:
        f.write("1")


# ======================================================
# SAFE CLEAN
# ======================================================
def safe_clean():
    sh("docker system prune -f >/dev/null 2>&1")
    sh("journalctl --vacuum-size=200M >/dev/null 2>&1")
    sh("apt autoremove -y >/dev/null 2>&1 || true")
    sh("apt clean >/dev/null 2>&1 || true")


# ======================================================
# ACTION
# ======================================================
def try_restart() -> bool:
    sh(f"systemctl restart {SERVICE}")
    time.sleep(5)
    return is_up()


def try_reinstall():
    tmp = "/tmp/reinstall.sh"
    url = f"{AUTO_REPO}reinstall.sh"
    sh(f"curl -s -o {tmp} {url}")
    sh(f"chmod +x {tmp}")
    return sh(f"bash {tmp}")


# ======================================================
# MAIN
# ======================================================
def main():
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    flag = flag_load()
    fix_keys()

    # ===== HEALTH CHECK =====
    bad = health_need()
    if bad and health_allowed():
        msg = "\n".join(bad)
        tg(f"⚠️ *{NODE_NAME}* HIGH USAGE\n{msg}\n{sys_brief()}")
        health_mark()

    safe_clean()

    # ===== NODE OK =====
    if is_up():
        if flag["last"] != "up":
            tg(f"✅ *{NODE_NAME}* UP @ {t}\n{sys_brief()}\n{last_round()}")
        flag_set("up", False)
        return

    # ===== DOWN =====
    if flag["last"] != "down":
        tg(f"🚨 *{NODE_NAME}* DOWN @ {t}\n↪ restarting…")

    # Restart
    if try_restart():
        tg(f"🟢 *{NODE_NAME}* RECOVERED @ {t}\n{sys_brief()}")
        flag_set("up", False)
        return

    # Reinstall once
    if MONITOR_TRY_REINSTALL and not flag["once"]:
        tg("⚙ Restart failed → reinstalling…")
        try_reinstall()
        time.sleep(10)

        if is_up():
            tg(f"✅ *{NODE_NAME}* REINSTALLED OK @ {t}\n{sys_brief()}")
            flag_set("up", False)
            return
        else:
            flag_set("down", True)

    # ===== FAIL =====
    raw = sh(f"journalctl -u {SERVICE} -n {LOG_LINES} --no-pager")
    logs = clean(raw)[-MAX_LOG:]

    tg(
        f"❌ *{NODE_NAME}* FAIL RECOVER @ {t}\n"
        f"Need manual fix.\n"
        f"```\n{logs}\n```"
    )

    flag_set("down", True)


if __name__ == "__main__":
    main()
