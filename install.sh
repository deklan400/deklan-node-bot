#!/usr/bin/env bash
set -euo pipefail

###################################################################
#   DEKLAN NODE BOT INSTALLER — v2.7 (SMART)
#   Telegram control + Auto-monitor for RL-Swarm
#   Includes RL-Swarm auto-detect + validation
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
REPO="https://github.com/deklan400/deklan-node-bot"

# RL-Swarm autolocate
RL_DIR_DEFAULT="/root/rl_swarm"
KEY_DIR_DEFAULT="/root/deklan"


###################################################################
# 1) Install dependencies
###################################################################
echo -e "${YELLOW}[1/7] Installing dependencies...${NC}"
apt update -y
apt install -y python3 python3-venv python3-pip git curl jq >/dev/null 2>&1 || {
  err "Failed installing dependencies"
  exit 1
}
msg "Dependencies OK"


###################################################################
# 2) Clone / Update Repo
###################################################################
echo -e "${YELLOW}[2/7] Preparing bot repository...${NC}"

if [[ ! -d "$BOT_DIR" ]]; then
  git clone "$REPO" "$BOT_DIR"
  msg "Repo cloned → $BOT_DIR"
else
  warn "Repository exists → $BOT_DIR"
  if git -C "$BOT_DIR" pull --rebase --autostash >/dev/null 2>&1; then
    msg "Repo updated"
  else
    warn "Repo update failed — skipping"
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
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1
msg "Python deps installed"


###################################################################
# 4) Setup .env
###################################################################
echo -e "${YELLOW}[4/7] Preparing ENV...${NC}"

if [[ ! -f ".env" ]]; then
  cp .env.example .env
  warn "⚠️ Edit .env → set BOT_TOKEN & CHAT_ID"
fi

# ensure base keys exist
grep -q '^SERVICE_NAME=' .env      || echo "SERVICE_NAME=gensyn" >> .env
grep -q '^AUTO_INSTALLER_GITHUB=' .env \
  || echo "AUTO_INSTALLER_GITHUB=https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/" >> .env
grep -q '^RL_DIR=' .env      || echo "RL_DIR=$RL_DIR_DEFAULT" >> .env
grep -q '^KEY_DIR=' .env     || echo "KEY_DIR=$KEY_DIR_DEFAULT" >> .env

chmod 600 .env
msg ".env ready ✅"


###################################################################
# 5) RL-Swarm smart check
###################################################################
echo -e "${YELLOW}[5/7] Checking RL-Swarm...${NC}"

RL_DIR=$(grep '^RL_DIR=' .env | cut -d'=' -f2)
KEY_DIR=$(grep '^KEY_DIR=' .env | cut -d'=' -f2)

if [[ -d "$RL_DIR" ]]; then
    msg "RL-Swarm directory found → $RL_DIR"

    # ensure keys symlink OK
    if [[ ! -L "$RL_DIR/keys" ]]; then
      warn "keys/ missing → fixing"
      rm -rf "$RL_DIR/keys" >/dev/null 2>&1 || true
      ln -s "$KEY_DIR" "$RL_DIR/keys"
      msg "keys/ symlink linked ✅"
    fi
else
    warn "RL-Swarm folder NOT found"
    echo ""
    read -p "Clone RL-Swarm now? [Y/n] > " ans
    if [[ ! "$ans" =~ ^[Nn]$ ]]; then
      git clone https://github.com/gensyn-ai/rl-swarm "$RL_DIR"
      msg "RL-Swarm cloned ✅"

      rm -rf "$RL_DIR/keys" >/dev/null 2>&1
      ln -s "$KEY_DIR" "$RL_DIR/keys"
      msg "keys/ symlink created ✅"
    else
      warn "Skipping RL-Swarm clone"
    fi
fi


###################################################################
# 6) Create bot.service
###################################################################
echo -e "${YELLOW}[6/7] Installing bot.service...${NC}"

cat >/etc/systemd/system/bot.service <<EOF
[Unit]
Description=Deklan Node Bot
After=network-online.target docker.service
Wants=network-online.target

StartLimitIntervalSec=60
StartLimitBurst=20

[Service]
Type=simple
User=root
WorkingDirectory=$BOT_DIR
EnvironmentFile=-$BOT_DIR/.env

ExecStart=/bin/bash -c '
  if [ -x "$BOT_DIR/.venv/bin/python" ]; then
    exec $BOT_DIR/.venv/bin/python $BOT_DIR/bot.py;
  else
    exec python3 $BOT_DIR/bot.py;
  fi
'

Restart=always
RestartSec=3
KillMode=mixed
LimitNOFILE=65535

StandardOutput=journal
StandardError=journal
LogRateLimitIntervalSec=0
LogRateLimitBurst=0

Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONIOENCODING=UTF-8"

NoNewPrivileges=yes
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

TimeoutStopSec=25

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now bot
msg "bot.service installed & running ✅"


###################################################################
# 7) Monitor Timer
###################################################################
echo -e "${YELLOW}[7/7] Installing monitor timer...${NC}"

cat >/etc/systemd/system/monitor.service <<EOF
[Unit]
Description=Deklan Node Monitor (oneshot)

[Service]
Type=oneshot
WorkingDirectory=$BOT_DIR
EnvironmentFile=-$BOT_DIR/.env
ExecStart=$BOT_DIR/.venv/bin/python $BOT_DIR/monitor.py

StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"
EOF


cat >/etc/systemd/system/monitor.timer <<EOF
[Unit]
Description=Run Deklan Node Monitor

[Timer]
OnBootSec=2m
OnUnitActiveSec=3h
Persistent=true
Unit=monitor.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now monitor.timer
msg "monitor.timer installed ✅"


###################################################################
# DONE
###################################################################
echo -e "
${GREEN}✅ INSTALLATION COMPLETE
------------------------------------
Check bot:        systemctl status bot
Monitor timer:    systemctl status monitor.timer
Force monitor:    systemctl start monitor.service
Live logs:        journalctl -u bot -f
${NC}
"
