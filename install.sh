#!/usr/bin/env bash
set -e

echo ""
echo "====================================="
echo " ⚡ INSTALLING DEKLAN NODE BOT"
echo "====================================="
echo ""

# ----------------------------------------------------
# Install deps
# ----------------------------------------------------
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# ----------------------------------------------------
# Clone repo
# ----------------------------------------------------
if [ ! -d "/opt/deklan-node-bot" ]; then
    sudo git clone https://github.com/deklan400/deklan-node-bot /opt/deklan-node-bot
else
    echo "✅ Repo already exists → /opt/deklan-node-bot"
fi

cd /opt/deklan-node-bot

# ----------------------------------------------------
# Python venv
# ----------------------------------------------------
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Created virtualenv"
fi

source .venv/bin/activate
pip install -r requirements.txt

# ----------------------------------------------------
# ENV setup
# ----------------------------------------------------
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  Edit env:"
    echo "   nano /opt/deklan-node-bot/.env"
    echo "   → isi BOT_TOKEN & CHAT_ID wajib"
fi

sudo chown root:root .env
sudo chmod 600 .env


# ----------------------------------------------------
# Install bot systemd
# ----------------------------------------------------
sudo tee /etc/systemd/system/bot.service >/dev/null <<EOF
[Unit]
Description=Deklan Node Bot
After=network.target

[Service]
User=root
WorkingDirectory=/opt/deklan-node-bot
EnvironmentFile=/opt/deklan-node-bot/.env
ExecStart=/opt/deklan-node-bot/.venv/bin/python /opt/deklan-node-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now bot

# ----------------------------------------------------
# monitor.service
# ----------------------------------------------------
sudo tee /etc/systemd/system/monitor.service >/dev/null <<EOF
[Unit]
Description=Deklan Node Monitor (oneshot)

[Service]
Type=oneshot
EnvironmentFile=/opt/deklan-node-bot/.env
WorkingDirectory=/opt/deklan-node-bot
ExecStart=/opt/deklan-node-bot/.venv/bin/python /opt/deklan-node-bot/monitor.py
EOF

# ----------------------------------------------------
# monitor.timer
# ----------------------------------------------------
sudo tee /etc/systemd/system/monitor.timer >/dev/null <<EOF
[Unit]
Description=Run Deklan Node Monitor every 3 hours

[Timer]
OnBootSec=5m
OnUnitActiveSec=3h
Persistent=true

[Install]
WantedBy=timers.target
EOF

# ----------------------------------------------------
# Custom monitor override
# ----------------------------------------------------
if grep -q '^MONITOR_EVERY_MINUTES=' .env; then
    MIN=$(grep '^MONITOR_EVERY_MINUTES=' .env | cut -d'=' -f2)

    if [[ "$MIN" =~ ^[0-9]+$ ]]; then
        HOURS=$(( MIN / 60 ))
        REM=$(( MIN % 60 ))

        INTERVAL=""
        if [ "$HOURS" -gt 0 ]; then INTERVAL="${HOURS}h"; fi
        if [ "$REM" -gt 0 ]; then INTERVAL="${INTERVAL}${REM}m"; fi

        if [ -n "$INTERVAL" ]; then
            sudo sed -i "s/^OnUnitActiveSec=.*/OnUnitActiveSec=${INTERVAL}/" /etc/systemd/system/monitor.timer
            echo "⏱ Custom monitor interval = ${INTERVAL}"
        fi
    fi
fi

# ----------------------------------------------------
# Enable services
# ----------------------------------------------------
sudo systemctl daemon-reload
sudo systemctl enable --now monitor.timer

echo ""
echo "✅ BOT & MONITOR INSTALLED!"
echo "------------------------------------"
echo "- Check bot:       systemctl status bot"
echo "- Check monitor:   systemctl status monitor.timer"
echo "- Run monitor now: systemctl start monitor.service"
echo "- Bot logs:        journalctl -u bot -f"
echo ""
