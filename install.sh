#!/usr/bin/env bash
set -e

echo ""
echo "====================================="
echo " ⚡  Installing Deklan Node Bot"
echo "====================================="
echo ""

# Update system
sudo apt update && sudo apt install -y python3 python3-pip git

# Clone repo kalau belum ada
if [ ! -d "/opt/deklan-node-bot" ]; then
    sudo git clone https://github.com/deklan400/deklan-node-bot /opt/deklan-node-bot
else
    echo "Repo already exists → /opt/deklan-node-bot"
fi

cd /opt/deklan-node-bot
sudo pip3 install -r requirements.txt

if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️ File .env belum ada!"
    echo "Buat file .env dan isi BOT_TOKEN:"
    echo ""
    echo "BOT_TOKEN=your_token" > .env
    echo "Silakan edit .env dan isi token bot."
    echo ""
fi

echo ""
echo "✅ Installation complete!"
echo "Run bot via:"
echo "cd /opt/deklan-node-bot && python3 bot.py"
echo ""
