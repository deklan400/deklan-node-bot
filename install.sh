#!/usr/bin/env bash
set -e

GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
CYAN="\e[36m"
NC="\e[0m"

echo -e "
${CYAN}=====================================
 ⚡ INSTALLING DEKLAN NODE BOT
=====================================${NC}
"

# ----------------------------------------------------
# Install dependencies
# ----------------------------------------------------
echo -e "${YELLOW}[1/7] Installing dependencies...${NC}"
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv git >/dev/null 2>&1 || {
  echo -e "${RED}❌ Failed installing dependencies${NC}"
  exit 1
}

# ----------------------------------------------------
# Clone repo
# ----------------------------------------------------
echo -e "${YELLOW}[2/7] Cloning repo...${NC}"

if [ ! -d "/opt/deklan-node-bot" ]; then
    sudo git clone https://github.com/deklan400/deklan-node-bot /opt/deklan-node-bot
    echo -e "${GREEN}✅ Repo cloned${NC}"
else
    echo -e "${GREEN}✅ Repo already exists → /opt/deklan-node-bot${NC}"
fi

cd /opt/deklan-node-bot

# ----------------------------------------------------
# Python virtual env
# ----------------------------------------------------
echo -e "${YELLOW}[3/7] Preparing Python venv...${NC}"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtualenv created${NC}"
fi

source .venv/bin/activate
pip install -r requirements.txt >/dev/null 2>&1
echo -e "${GREEN}✅ Python deps installed${NC}"

# ----------------------------------------------------
# ENV setup
# ----------------------------------------------------
echo -e "${YELLOW}[4/7] Setting up ENV...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Edit ENV → Set BOT_TOKEN & CHAT_ID${NC}"
    echo "nano /opt/deklan-node-bot/.env"
fi

sudo chown root:root .env
sudo chmod 600 .env


# ----------------------------------------------------
# Create bot.service
# ----------------------------------------------------
echo -e "${YELLOW}[5/7] Installing bot.service...${NC}"

sudo tee /etc/systemd/system/bot.service >/dev/null <<EOF
[Unit]
Description=Deklan Node Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
EnvironmentFile=/opt/deklan-node-bot/.env
WorkingDirectory=/opt/deklan-node-bot
ExecStart=/opt/deklan-node-bot/.venv/bin/python /opt/deklan-node-bot/bot.py
Restart=always
RestartSec=5
LimitNOFILE=65535
KillMode=process
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now bot
echo -e "${GREEN}✅ bot.service installed & started${NC}"

# ----------------------------------------------------
# monitor.service + monitor.timer
# ----------------------------------------------------
echo -e "${YELLOW}[6/7] Installing monitor.timer...${NC}"

sudo tee /etc/systemd/system/monitor.service >/dev/null <<EOF
[Unit]
Description=Deklan Node Monitor (oneshot)

[Service]
Type=oneshot
EnvironmentFile=/opt/deklan-node-bot/.env
WorkingDirectory=/opt/deklan-node-bot
ExecStart=/opt/deklan-node-bot/.venv/bin/python /opt/deklan-node-bot/monitor.py
StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"
EOF

sudo tee /etc/systemd/system/monitor.timer >/dev/null <<EOF
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

# ----------------------------------------------------
# Override interval if MONITOR_EVERY_MINUTES exists
# ----------------------------------------------------
if grep -q '^MONITOR_EVERY_MINUTES=' .env; then
    MIN=$(grep '^MONITOR_EVERY_MINUTES=' .env | cut -d'=' -f2)
    if [[ "$MIN" =~ ^[0-9]+$ ]]; then
        HOURS=$(( MIN / 60 ))
        REM=$(( MIN % 60 ))

        INTERVAL=""
        [[ $HOURS -gt 0 ]] && INTERVAL="${HOURS}h"
        [[ $REM -gt 0 ]] && INTERVAL="${INTERVAL}${REM}m"

        if [ -n "$INTERVAL" ]; then
            sudo sed -i "s/^OnUnitActiveSec=.*/OnUnitActiveSec=${INTERVAL}/" \
              /etc/systemd/system/monitor.timer
            echo -e "${GREEN}⏱ Custom interval = ${INTERVAL}${NC}"
        fi
    fi
fi

sudo systemctl daemon-reload
sudo systemctl enable --now monitor.timer


# ----------------------------------------------------
# Done
# ----------------------------------------------------
echo -e "
${GREEN}✅ INSTALLATION COMPLETE!
------------------------------------
Check bot:       systemctl status bot
Check monitor:   systemctl status monitor.timer
Run monitor now: systemctl start monitor.service
Bot logs:        journalctl -u bot -f
${NC}
"
