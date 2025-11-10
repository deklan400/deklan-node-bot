#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Deklan Smart Monitor — v3.1
  Auto • Detect • Restart • Reinstall
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

AUTO_REPO   = E("AUTO_INSTALLER_GITHUB",
    "https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/"
)

RL_DIR      = E("RL_DIR", "/root/rl_swarm")
KEY_DIR     = E("KEY_DIR", "/root/deklan")

FLAG_FILE   = "/tmp/.node_status.json"


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
# RL-SWARM SELF-HEAL
# ======================================================
def fix_keys():
    """Ensure RL_DIR/keys => KEY_DIR"""
    if not os.path.isdir(RL_DIR):
        return
    t = os.path.join(RL_DIR, "keys")
    if os.path.islink(t):
        return
    sh(f"rm -rf {t}")
    sh(f"ln -s {KEY_DIR} {t}")


# ======================================================
# CHECK
# ======================================================
def is_up():
    return sh(f"systemctl is-active {SERVICE}") == "active"


def sys_brief():
    try:
        cpu = psutil.cpu_percent(interval=0.6)
        vm  = psutil.virtual_memory()
        du  = psutil.disk_usage("/")
        up  = timedelta(seconds=int(time.time() - psutil.boot_time()))
        return f"CPU {cpu:.1f}% • RAM {vm.percent:.1f}% • Disk {du.percent:.1f}% • Up {up}"
    except:
        return "(stats unavailable)"


def last_round():
    s = rf"journalctl -u {SERVICE} --no-pager | grep -E 'Joining round:' | tail -n1"
    out = sh(s)
    return out if out else "(no round info)"


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

    # === UP ===
    if is_up():
        if flag["last"] != "up":
            tg(f"✅ *{NODE_NAME}* is UP @ {t}\n{sys_brief()}\n{last_round()}")
        flag_set("up", False)
        return

    # === DOWN ===
    if flag["last"] != "down":
        tg(f"🚨 *{NODE_NAME}* DOWN @ {t}\n↪ restarting…")

    # 1) restart
    if try_restart():
        tg(f"🟢 *{NODE_NAME}* RECOVERED @ {t}\n{sys_brief()}")
        flag_set("up", False)
        return

    # 2) reinstall once
    if not flag["once"]:
        tg("⚙ Restart failed → reinstalling…")
        try_reinstall()
        time.sleep(10)

        if is_up():
            tg(f"✅ *{NODE_NAME}* RECOVERED after REINSTALL @ {t}\n{sys_brief()}")
            flag_set("up", False)
            return
        else:
            flag_set("down", True)

    # 3) FAILED → dump logs
    raw = sh(f"journalctl -u {SERVICE} -n {LOG_LINES} --no-pager")
    logs = clean(raw)[-3500:]

    tg(
        f"❌ *{NODE_NAME}* FAIL RECOVER @ {t}\n"
        f"Manual fix needed.\n"
        f"```\n{logs}\n```"
    )

    flag_set("down", True)


if __name__ == "__main__":
    main()
