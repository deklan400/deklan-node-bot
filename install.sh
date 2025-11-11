#!/usr/bin/env bash
set -euo pipefail

###################################################################
#   DEKLAN NODE BOT INSTALLER — v3.5 SMART
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
 ⚡ INSTALLING DEKLAN NODE BOT (v3.5)
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
# 4) ENV
###################################################################
msg "[4/7] Preparing ENV (.env)…"

if [[ ! -f ".env" ]]; then
  cp .env.example .env
  warn "⚠ Set BOT_TOKEN + CHAT_ID inside .env"
fi

grep -q '^SERVICE_NAME=' .env      || echo "SERVICE_NAME=gensyn" >> .env
grep -q '^AUTO_INSTALLER_GITHUB=' .env \
  || echo "AUTO_INSTALLER_GITHUB=https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/" >> .env
grep -q '^RL_DIR=' .env || echo "RL_DIR=${RL_DIR}" >> .env
grep -q '^KEY_DIR=' .env || echo "KEY_DIR=${KEY_DIR}" >> .env

chmod 600 .env
msg ".env OK ✅"


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
  warn "RL-Swarm NOT found — skipping"
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
  exec "$PYBIN" $BOT_DIR/bot.py
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
# 7) Monitor.timer + service
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
echo -e "
${GREEN}✅ BOT INSTALL COMPLETE
-------------------------------------
Check bot:         systemctl status bot
Monitor timer:     systemctl status monitor.timer
Force monitor:     systemctl start monitor.service
Logs:              journalctl -u bot -f
-------------------------------------${NC}
"
