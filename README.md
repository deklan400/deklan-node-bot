# Deklan Node Bot

Telegram Bot for monitoring & controlling Gensyn RL-Swarm Node.

---

## ✅ INSTALL (1 Command)

bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh
)


---

## ✅ Setup

Edit `.env`

cd /opt/deklan-node-bot
nano .env


Isi:
BOT_TOKEN=xxxx
CHAT_ID=xxxx


Restart bot:


---

## ✅ Commands Telegram

| Command | Function |
|--------|---------|
| /start | Open menu |

---

## ✅ Menu UI

| Button | Function |
|--------|---------|
| 📊 Status Node | systemctl status gensyn |
| 🟢 Start | start node |
| 🔴 Stop | stop node |
| 🔄 Restart | restart node |
| 📜 Logs | view logs |

---

## ✅ Manage bot

systemctl start bot
systemctl stop bot
systemctl restart bot
systemctl status bot
journalctl -u bot -f


---

