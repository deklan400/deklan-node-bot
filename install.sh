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
# Python deps
# ----------------------------------------------------
sudo pip3 install -r requirements.txt --break-system-packages || true

# ----------------------------------------------------
# ENV setup
# ----------------------------------------------------
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  Edit file env:"
    echo "   nano /opt/deklan-node-bot/.env"
    echo "   → isi BOT_TOKEN & CHAT_ID wajib"
fi

sudo chown root:root .env
sudo chmod 600 .env


# ----------------------------------------------------
# Install bot systemd
# ----------------------------------------------------
sudo cp bot.service /etc/systemd/system/bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now bot


# ----------------------------------------------------
# Create monitor.service
# ----------------------------------------------------
sudo tee /etc/systemd/system/monitor.service >/dev/null <<'EOF'
[Unit]
Description=Deklan Node Monitor (oneshot)

[Service]
Type=oneshot
EnvironmentFile=/opt/deklan-node-bot/.env
WorkingDirectory=/opt/deklan-node-bot
ExecStart=/usr/bin/python3 /opt/deklan-node-bot/monitor.py
EOF


# ----------------------------------------------------
# Create monitor.timer
# ----------------------------------------------------
sudo tee /etc/systemd/system/monitor.timer >/dev/null <<'EOF'
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
# Custom interval override
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
            echo "⏱  Custom monitor interval = ${INTERVAL}"
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
echo "- Logs bot:        journalctl -u bot -f"
echo ""
