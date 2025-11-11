# ⚡ Deklan Node Bot — Gensyn RL-Swarm Control

<p align="center">
  <img src="https://i.ibb.co/3zxGBM4/GENSYN-BANNER.png" width="90%">
</p>

<p align="center">
  Telegram Control • Auto-Monitor • Auto-Installer • Swap Manager • Danger Zone
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Gensyn-Testnet-navy?style=for-the-badge">
  <img src="https://img.shields.io/badge/Telegram-Bot-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/AutoMonitor-YES-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Systemd-Supported-purple?style=for-the-badge">
  <img src="https://img.shields.io/badge/Linux-Ubuntu%2022.04-red?style=for-the-badge">
</p>

---

## 🧠 Overview
Deklan Node Bot adalah panel Telegram untuk mengontrol & memonitor node **Gensyn RL-Swarm** tanpa SSH.

✅ Start / Stop / Restart  
✅ CPU/RAM/Disk/Uptime  
✅ Logs → Telegram  
✅ Show Last Round  
✅ Auto-Monitor → Auto-Restart → Auto-Reinstall  
✅ One-Click Remote Installer  
✅ Multi-Admin  
✅ Swap Manager (16G/32G/64G/Custom)  
✅ Danger Zone (Password)  
✅ Systemd Native  
✅ Anti-Spam UP/DOWN  
✅ Modular multi-project  

---

## 🚀 Install
```
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

Installer:
- Clone repo → `/opt/deklan-node-bot`
- Buat `.env` (prompt)
- Install bot.service
- Install monitor.timer
- Start bot

---

## 🔧 Konfigurasi `.env`
```
nano /opt/deklan-node-bot/.env
```

Minimal:
```
BOT_TOKEN=xxxx
CHAT_ID=1111
```

Lengkap:
```
BOT_TOKEN=
CHAT_ID=
ALLOWED_USER_IDS=

SERVICE_NAME=gensyn
NODE_NAME=deklan-node
RL_DIR=/root/rl_swarm
KEY_DIR=/root/deklan

LOG_LINES=80
ROUND_GREP_PATTERN=Joining round:
LOG_MAX_CHARS=3500
MONITOR_TRY_REINSTALL=1
MONITOR_EVERY_MINUTES=180

AUTO_INSTALLER_GITHUB=https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/

ENABLE_DANGER_ZONE=0
DANGER_PASS=
```

---

## 📁 Struktur
```
/opt/deklan-node-bot
├── bot.py
├── monitor.py
├── requirements.txt
├── install.sh
├── bot.service
├── monitor.service
├── monitor.timer
├── .env
└── .env.example
```

Node keys:
```
/root/deklan/
│── swarm.pem
│── userApiKey.json
└── userData.json
```

Symlink:
```
/root/rl_swarm/keys → /root/deklan/
```

---

## 📱 Telegram
Perintah:
| Command   | Fungsi |
|-----------|--------|
| /start    | Menu |
| /status   | Resource |
| /logs     | Last logs |
| /restart  | Restart node |
| /round    | Last round |
| /help     | Help |

Menu:
- 📊 Status
- 🟢 Start
- 🔴 Stop
- 🔁 Restart
- 📜 Logs
- ℹ Round
- 💾 Swap Manager
- 🧩 Installer
- ⚠ Danger Zone

---

## 🧩 Installer Menu
Runtime script:
- install.sh
- reinstall.sh
- update.sh
- uninstall.sh

Flow:
1) Klik tombol  
2) Bot konfirmasi  
3) Balas "YES"  
4) Bot eksekusi  

Source:
```
AUTO_INSTALLER_GITHUB
```

---

## 💾 Swap Manager
Preset:
- 16G
- 32G
- 64G
- Custom (input GB)

Automasi:
- swapoff
- recreate /swapfile
- update /etc/fstab
- swapon

---

## 🛰 Auto Monitor
- Cek node  
- Up → no spam  
- Down → restart  
- Restart gagal → reinstall  
- Reinstall gagal → kirim logs  

```
systemctl status monitor.timer
systemctl start monitor.service
```

Flow:
```
Check → Restart → Reinstall → Notify FAIL
```

State file:
```
/tmp/.node_status.json
```

---

## ⚠ Danger Zone
ENABLE_DANGER_ZONE=1 + DANGER_PASS wajib

Fitur:
- Remove RL-Swarm
- Clean Docker
- Remove Swap
- Full Clean
- Reboot VPS

Require password via chat ✅

---

## 📦 Multi-Project
Bot terpisah dari installer repo.  
Bisa dipakai:
- Project lain
- RL-Swarm update
- Layanan lain

Cukup ganti:
```
AUTO_INSTALLER_GITHUB
```

---

## 🛠 System
Check bot:
```
systemctl status bot
journalctl -u bot -f
```

Check monitor:
```
systemctl status monitor.timer
systemctl start monitor.service
```

---

## 🗑 Uninstall
```
systemctl stop bot monitor.service monitor.timer
systemctl disable bot monitor.service monitor.timer
rm -f /etc/systemd/system/bot.service
rm -f /etc/systemd/system/monitor.*
rm -rf /opt/deklan-node-bot
systemctl daemon-reload
```

---

## ✅ Screenshot (dummy)

<p align="center">
  <img src="assets/menu_dark.png" width="420">
</p>

<p align="center">
  <img src="assets/logs_dark.png" width="420">
</p>

<p align="center">
  <img src="assets/swap_dark.png" width="420">
</p>

---

## ✅ Next
- Multi-node DB
- Auto update bot
- Dashboard web
- Remote deploy
- Auto discovery

---

## ❤️ Credits
Built with ❤️ by **Deklan × GPT-5**
