✅ Deklan Node Bot

Telegram Bot for monitoring & controlling Gensyn RL-Swarm Node

📦 Features
✅ Auto-start bot via systemd
✅ Show CPU / RAM / Disk / Uptime
✅ Start / Stop / Restart RL-Swarm
✅ Show node logs
✅ Show latest round
✅ Menu UI via Telegram
✅ Secure .env secrets
✅ Python lightweight

⚙️ Installation
1️⃣ Clone repo
git clone https://github.com/deklan400/deklan-node-bot
cd deklan-node-bot

2️⃣ Install Python deps
pip install -r requirements.txt

3️⃣ Create config .env

Copy template:

cp .env.example .env


Edit .env:

BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID=YOUR_TELEGRAM_CHAT_ID

🔥 Systemd install (auto-run)
sudo cp bot.service /etc/systemd/system/bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now bot


Check:

systemctl status bot


Logs:

journalctl -u bot -f


Stop:

systemctl stop bot


Restart:

systemctl restart bot

🤖 Telegram Commands

Command:
/start → open menu

Actions:

Status  → show CPU / RAM / Disk / uptime
Start   → start node
Stop    → stop node
Restart → restart node
Logs    → latest logs
Round   → show latest round

🧠 Node Control

Start node:

sudo systemctl start gensyn


Stop node:

sudo systemctl stop gensyn


Restart node:

sudo systemctl restart gensyn


Check logs:

journalctl -u gensyn -f

📂 Project Structure
deklan-node-bot/
│
├─ bot.py
├─ bot.service
├─ install.sh
├─ requirements.txt
├─ .env.example
└─ README.md

🛠 Troubleshooting

Bot not responding?

systemctl status bot
journalctl -u bot -f


Wrong token?
Edit .env:

nano .env


Node not detected?

systemctl status gensyn

✅ Auto-Install (coming)
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)

✅ Notes
• Bot must run on same machine as rl-swarm
• RL-Swarm service name must be: gensyn
• Telegram API must be configured

💎 Credits

Created by Deklan Labz
