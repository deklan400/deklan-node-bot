#!/usr/bin/env bash
set -e

###################################################################
#   DEKLAN NODE BOT INSTALLER — v2.1
#   Telegram control + Auto-monitor for RL-Swarm
###################################################################

# ===== COLORS =====
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
CYAN="\e[36m"
NC="\e[0m"

banner() {
  echo -e "
${CYAN}===========================================
 ⚡ INSTALLING DEKLAN NODE BOT
===========================================${NC}
"
}

msg()  { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }

banner

BOT_DIR="/opt/deklan-node-bot"


###################################################################
# 1) Install Base Dependencies
###################################################################
echo -e "${YELLOW}[1/7] Installing dependencies...${NC}"
apt update -y
apt install -y python3 python3-pip python3-venv git curl >/dev/null 2>&1 || {
  err "Failed installing dependencies"
  exit 1
}
msg "Dependencies OK"


###################################################################
# 2) Clone / Update Repo
###################################################################
echo -e "${YELLOW}[2/7] Preparing bot repository...${NC}"

if [[ ! -d "$BOT_DIR" ]]; then
  git clone https://github.com/deklan400/deklan-node-bot "$BOT_DIR"
  msg "Repo cloned → $BOT_DIR"
else
  warn "Repository already exists"
  read -p "Update repo now? [Y/n] > " ans
  if [[ ! "$ans" =~ ^[Nn]$ ]]; then
    cd "$BOT_DIR" && git pull
    msg "Repo updated"
  else
    msg "Skipping update"
  fi
fi

cd "$BOT_DIR"


###################################################################
# 3) Python Virtualenv
###################################################################
echo -e "${YELLOW}[3/7] Preparing Python venv...${NC}"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
  msg "Virtualenv created"
fi

source .venv/bin/activate
pip install -r requirements.txt >/dev/null 2>&1
msg "Python deps installed"


###################################################################
# 4) Setup .env
###################################################################
echo -e "${YELLOW}[4/7] Setting up ENV...${NC}"

if [[ ! -f ".env" ]]; then
  cp .env.example .env
  warn "Edit .env → set BOT_TOKEN & CHAT_ID"
  echo "nano $BOT_DIR/.env"
fi

chmod 600 .env
msg ".env ready"


###################################################################
# 5) Install bot.service
###################################################################
echo -e "${YELLOW}[5/7] Installing bot.service...${NC}"

cat >/etc/systemd/system/bot.service <<EOF
[Unit]
Description=Deklan Node Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
EnvironmentFile=$BOT_DIR/.env
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/.venv/bin/python $BOT_DIR/bot.py
Restart=always
RestartSec=5
LimitNOFILE=65535
KillMode=process
StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now bot
msg "bot.service installed & running"


###################################################################
# 6) Install monitor.service + monitor.timer
###################################################################
echo -e "${YELLOW}[6/7] Installing monitor timer...${NC}"

cat >/etc/systemd/system/monitor.service <<EOF
[Unit]
Description=Deklan Node Monitor (oneshot)

[Service]
Type=oneshot
EnvironmentFile=$BOT_DIR/.env
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/.venv/bin/python $BOT_DIR/monitor.py
StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"
EOF

cat >/etc/systemd/system/monitor.timer <<EOF
[Unit]
Description=Run Deklan Node Monitor every 3 hours
After=network-online.target
Wants=network-online.target

[Timer]
OnBootSec=5m
OnUnitActiveSec=3h
Persistent=true
Unit=monitor.service

[Install]
WantedBy=timers.target
EOF


# Auto customize interval if MONITOR_EVERY_MINUTES exists
if grep -q '^MONITOR_EVERY_MINUTES=' .env; then
  MIN=$(grep '^MONITOR_EVERY_MINUTES=' .env | cut -d'=' -f2)
  if [[ "$MIN" =~ ^[0-9]+$ ]]; then
    HOURS=$(( MIN / 60 ))
    REM=$(( MIN % 60 ))

    INTERVAL=""
    [[ $HOURS -gt 0 ]] && INTERVAL="${HOURS}h"
    [[ $REM -gt 0 ]] && INTERVAL="${INTERVAL}${REM}m"

    if [[ -n "$INTERVAL" ]]; then
      sed -i "s/^OnUnitActiveSec=.*/OnUnitActiveSec=$INTERVAL/" \
        /etc/systemd/system/monitor.timer
      msg "Monitor interval override → $INTERVAL"
    fi
  fi
fi

systemctl daemon-reload
systemctl enable --now monitor.timer
msg "monitor.timer installed & active"


###################################################################
# 7) DONE
###################################################################
echo -e "
${GREEN}✅ INSTALLATION COMPLETE!
------------------------------------
Check bot:       systemctl status bot
Check monitor:   systemctl status monitor.timer
Run monitor now: systemctl start monitor.service
Bot logs:        journalctl -u bot -f
${NC}
"
