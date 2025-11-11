#!/usr/bin/env bash
set -euo pipefail

###################################################################
#   DEKLAN NODE BOT INSTALLER — v3.6 SMART-PROMPT
#   Telegram control + Auto-monitor for RL-Swarm
#   Auto-install RL-Swarm keys & systemd
###################################################################

# ===== COLORS =====
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
CYAN="\e[36m"
NC="\e[0m"

msg()  { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }

banner() {
  echo -e "
${CYAN}===========================================
 ⚡ INSTALLING DEKLAN NODE BOT (v3.6)
===========================================${NC}
"
}
banner


# ===== PATHS =====
BOT_DIR="/opt/deklan-node-bot"
REPO="https://github.com/deklan400/deklan-node-bot"

RL_DIR="/root/rl_swarm"
KEY_DIR="/root/deklan"

SERVICE_NAME="bot"


###################################################################
# 1) Python deps
###################################################################
msg "[1/7] Installing dependencies…"
apt update -y >/dev/null
apt install -y python3 python3-venv python3-pip git curl jq >/dev/null
msg "Deps OK ✅"


###################################################################
# 2) Clone Repo
###################################################################
msg "[2/7] Fetching bot repository…"

if [[ ! -d "$BOT_DIR" ]]; then
  git clone "$REPO" "$BOT_DIR"
  msg "Repo cloned → $BOT_DIR"
else
  warn "Repo exists → pulling update…"
  if git -C "$BOT_DIR" pull --rebase --autostash >/dev/null 2>&1; then
    msg "Repo updated ✅"
  else
    warn "Repo update failed — using local copy"
  fi
fi


###################################################################
# 3) Python venv
###################################################################
msg "[3/7] Preparing Python venv…"

cd "$BOT_DIR"
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
  msg "Virtualenv created ✅"
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null
msg "Python requirements OK ✅"



###################################################################
# 4) ENV (AUTO PROMPT)
###################################################################
msg "[4/7] Creating .env (interactive)…"

echo ""
read -rp "🔑 Enter BOT TOKEN: " BOT_TOKEN
read -rp "👤 Enter Main Admin CHAT ID: " CHAT_ID
read -rp "➕ Extra allowed users? (comma separated) [optional]: " ALLOWED
read -rp "⚠ Enable Danger Zone? (y/N): " ENABLE_DZ

if [[ "$ENABLE_DZ" == "y" || "$ENABLE_DZ" == "Y" ]]; then
  read -rp "🔐 Set Danger Password: " DANGER_PASS
  ENABLE_DZ="1"
else
  DANGER_PASS=""
  ENABLE_DZ="0"
fi

cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
CHAT_ID=$CHAT_ID
ALLOWED_USER_IDS=$ALLOWED

# Node
SERVICE_NAME=gensyn
NODE_NAME=deklan-node

# Logs
LOG_LINES=80
MONITOR_EVERY_MINUTES=180
ROUND_GREP_PATTERN=Joining round:
LOG_MAX_CHARS=3500

# Danger
ENABLE_DANGER_ZONE=$ENABLE_DZ
DANGER_PASS=$DANGER_PASS

# Auto installer base
AUTO_INSTALLER_GITHUB=https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/

# RL-Swarm folders
RL_DIR=$RL_DIR
KEY_DIR=$KEY_DIR

# Smart options
FORCE_GIT_PULL=1
DOCKER_REBUILD=1
MONITOR_TRY_REINSTALL=1
EOF

chmod 600 .env
msg ".env generated ✅"


###################################################################
# 5) RL-Swarm keys link
###################################################################
msg "[5/7] Checking RL-Swarm folder…"

if [[ -d "$RL_DIR" ]]; then
  msg "RL-Swarm found → $RL_DIR"

  if [[ ! -L "$RL_DIR/keys" ]]; then
    warn "Missing keys symlink → fixing…"
    rm -rf "$RL_DIR/keys" >/dev/null 2>&1 || true
    ln -s "$KEY_DIR" "$RL_DIR/keys"
    msg "keys → symlinked ✅"
  else
    msg "keys → OK ✅"
  fi
else
  warn "RL-Swarm NOT found — skipping symlink"
fi



###################################################################
# 6) Install bot.service
###################################################################
msg "[6/7] Installing bot.service…"

cat >/etc/systemd/system/bot.service <<EOF
[Unit]
Description=Deklan Node Bot (Telegram)
After=network-online.target
Wants=network-online.target

StartLimitIntervalSec=60
StartLimitBurst=15

[Service]
Type=simple
User=root
Group=root

WorkingDirectory=$BOT_DIR
EnvironmentFile=-$BOT_DIR/.env

Environment="PATH=$BOT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"

ExecStart=/bin/bash -c '
  PYBIN="$BOT_DIR/.venv/bin/python";
  if [ ! -x "$PYBIN" ]; then
      PYBIN="$(command -v python3)";
  fi;
  exec "\$PYBIN" $BOT_DIR/bot.py
'

ExecReload=/bin/kill -HUP \$MAINPID

Restart=always
RestartSec=3

StandardOutput=journal
StandardError=journal

LimitNOFILE=65535
TimeoutStopSec=25
KillMode=mixed

# Security
NoNewPrivileges=yes
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
SystemCallFilter=@system-service
LockPersonality=yes
ProtectHostname=yes
ProtectKernelLogs=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
PrivateDevices=yes

Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONIOENCODING=UTF-8"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now bot
msg "bot.service installed ✅"



###################################################################
# 7) Install monitor.service + timer
###################################################################
msg "[7/7] Installing monitor.service + timer…"

cat >/etc/systemd/system/monitor.service <<EOF
[Unit]
Description=Deklan Node Monitor (oneshot)
After=network-online.target
Wants=network-online.target

ConditionPathExists=$BOT_DIR/monitor.py

[Service]
Type=oneshot
WorkingDirectory=$BOT_DIR
EnvironmentFile=-$BOT_DIR/.env

ExecStart=/bin/bash -c '
  PYBIN="$BOT_DIR/.venv/bin/python";
  if [ ! -x "$PYBIN" ]; then
      PYBIN="$(command -v python3)";
  fi;
  exec "\$PYBIN" monitor.py
'

StandardOutput=journal
StandardError=journal

Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONIOENCODING=UTF-8"

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

Restart=no

[Install]
WantedBy=multi-user.target
EOF


cat >/etc/systemd/system/monitor.timer <<EOF
[Unit]
Description=Run Deklan Node Monitor periodically
After=network-online.target
Wants=network-online.target

[Timer]
OnBootSec=2m
OnUnitActiveSec=3h
RandomizedDelaySec=45
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
systemctl restart bot

echo -e "
${GREEN}✅ BOT INSTALL COMPLETE
-------------------------------------
Check bot:         systemctl status bot
Monitor timer:     systemctl status monitor.timer
Force monitor:     systemctl start monitor.service
Logs:              journalctl -u bot -f
-------------------------------------${NC}
"
