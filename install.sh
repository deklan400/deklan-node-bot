#!/usr/bin/env bash
set -e

echo ""
echo "====================================="
echo " ⚡ INSTALLING DEKLAN NODE BOT"
echo "====================================="
echo ""

# Update
sudo apt update && sudo apt install -y python3 python3-pip git

# Clone repo if not exists
if [ ! -d "/opt/deklan-node-bot" ]; then
    sudo git clone https://github.com/deklan400/deklan-node-bot /opt/deklan-node-bot
else
    echo "Repo already exists → /opt/deklan-node-bot"
fi

cd /opt/deklan-node-bot

# Install deps
sudo pip3 install -r requirements.txt

# Setup env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️ Edit /opt/deklan-node-bot/.env → isi BOT_TOKEN & CHAT_ID"
fi

# Install systemd
sudo cp bot.service /etc/systemd/system/bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now bot

echo ""
echo "✅ BOT INSTALLED!"
echo ""
echo "Check status:"
echo " systemctl status bot"
echo ""
echo "View logs:"
echo " journalctl -u bot -f"
