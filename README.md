<START>

<!-- BANNER -->
<p align="center">
  <img src="https://i.ibb.co/3zxGBM4/GENSYN-BANNER.png" width="90%" />
</p>

<h1 align="center">🖤 Deklan Node Bot v2.4</h1>
<p align="center">
  Telegram Control Panel + Auto-Monitor + One-Click Installer<br>
  for Gensyn RL-Swarm Nodes
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Gensyn-Testnet-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Telegram-Bot-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Auto--Install-YES-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Systemd-Supported-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/Linux-Ubuntu%2022.04-purple?style=for-the-badge">
</p>

---

## 🧠 Overview

**Deklan Node Bot** adalah Telegram Bot untuk mengontrol & monitoring  
**Gensyn RL-Swarm Node tanpa SSH!**

✅ Start / Stop / Restart  
✅ CPU / RAM / Disk / Uptime  
✅ Logs → Telegram  
✅ Latest Round  
✅ Auto-Monitor + Auto-Restart  
✅ Auto-Reinstall  
✅ One-Click Installer  
✅ Danger Zone (Password)  
✅ Multi admin  
✅ AUTO_INSTALLER → update installer tanpa update bot  
✅ Anti-Spam Alert (status cache)  

> Semua control bisa dari HP 📱

---

## ⚡ Features

- Telegram menu
- Systemd integration
- Log viewer (journalctl)
- CPU / RAM / Disk Monitoring
- Round detection
- Auto-monitor
- Auto-restart
- Auto-reinstall
- UP/DOWN notification
- Anti-Spam (no spam repeat UP/DOWN)
- Remote installer script
- Multiple admin
- Danger Zone (secure)

---

## 🚀 Quick Install

> Jalankan di VPS Ubuntu

```bash
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

Installer akan:
✅ Install dependencies  
✅ Clone repo  
✅ Setup virtualenv  
✅ Generate `.env`  
✅ Install + start bot.service  
✅ Install + start monitor.timer  

---

## ⚙️ Konfigurasi `.env`

```bash
nano /opt/deklan-node-bot/.env
```

Isi minimal:

```
BOT_TOKEN=YOUR_TOKEN
CHAT_ID=123456
```

Opsional:

```
ALLOWED_USER_IDS=12345,98765
SERVICE_NAME=gensyn
NODE_NAME=Gensyn-VPS
LOG_LINES=80
MONITOR_EVERY_MINUTES=180
ENABLE_DANGER_ZONE=1
DANGER_PASS=12345
AUTO_INSTALLER_GITHUB=https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/
```

---

### 🧩 ENV Table

| Key | Wajib | Fungsi |
|------|-------|--------|
| BOT_TOKEN | ✅ | Token bot Telegram |
| CHAT_ID | ✅ | Admin |
| ALLOWED_USER_IDS | ❌ | Extra admins |
| SERVICE_NAME | ❌ | Target service |
| NODE_NAME | ❌ | Nama VPS |
| LOG_LINES | ❌ | Baris logs |
| MONITOR_EVERY_MINUTES | ❌ | Interval monitor |
| ENABLE_DANGER_ZONE | ❌ | Aktifkan menu danger |
| DANGER_PASS | ❌ | Password Danger |
| AUTO_INSTALLER_GITHUB | ✅ | Source auto installer |

---

## 📡 Telegram Commands

| Command | Fungsi |
|--------|--------|
| /start | Menu |
| /status | Show resource |
| /logs | Show logs |
| /restart | Restart node |
| /round | Show last round |
| /help | Help |

---

## 🧩 Telegram Menu

| Button | Fungsi |
|--------|--------|
| 📊 Status | Info VPS |
| 🟢 Start | Start node |
| 🔴 Stop | Stop node |
| 🔁 Restart | Restart |
| 📜 Logs | Lihat logs |
| ℹ️ Round | Last round |
| 🧩 Installer | Menu installer |
| ⚠ Danger Zone | Tools berbahaya |

---

## 🔧 Installer Menu

Remote script via:
```
AUTO_INSTALLER_GITHUB
```

Fitur:
- Install
- Reinstall
- Update
- Uninstall

Flow:
1) Klik tombol
2) Bot konfirmasi
3) Ketik `YES`

---

## ⚙️ Auto Installer (AUTO_REPO)

All installer diambil dari:

```
https://github.com/deklan400/deklan-autoinstall
```

Supports:
- install.sh
- reinstall.sh
- update.sh
- uninstall.sh

---

## 🛰 Auto Monitor

Systemd timer akan:
- Cek status node
- Auto-restart
- Kalau gagal → auto-reinstall
- Kalau gagal → kirim logs

```
systemctl status monitor.timer
```

---

### 🔁 Auto-Recovery Logic

1) Cek service  
2) Restart  
3) Kalau masih DOWN → reinstall  
4) Kalau masih DOWN → notif + logs  

```mermaid
flowchart TD
A(Check Node) -->|UP| B(OK)
A -->|DOWN| C(Restart)
C -->|Success| B
C -->|Fail| D(Reinstall)
D -->|Success| B
D -->|Fail| E(Notify + Logs)
```

---

## 🔥 Danger Zone

> ENABLE_DANGER_ZONE=1 + DANGER_PASS wajib

| Fungsi |
|--------|
| Remove RL-Swarm |
| Clean Docker |
| Remove Swap |
| Full Clean |
| Reboot VPS |

---

## 🔥 Systemd Reference

### Bot
```
systemctl status bot
journalctl -u bot -f
```

### Monitor
```
systemctl status monitor.timer
systemctl start monitor.service
```

---

## 📁 Repo Structure

```
/opt/deklan-node-bot
├── bot.py
├── monitor.py
├── install.sh
├── requirements.txt
├── bot.service
├── monitor.service
├── monitor.timer
├── .env
├── .env.example
└── /tmp/.node_status.json   ← auto generated
```

---

## ✅ Sample Alerts

✅ UP
```
✅ Gensyn-01 is UP
CPU 32% • RAM 71% • Disk 62%
Last round: xxx
```

🚨 DOWN
```
🚨 Gensyn-01 DOWN — Restarting…
```

🟢 Recovered
```
🟢 Recovered after restart
```

🔁 Recovered after reinstall
```
✅ Recovered after reinstall
```

❌ FAILED
```
❌ FAILED — manual fix required
<logs>
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

## 🛣 Roadmap

- Multi-node support
- Web dashboard
- Auto update bot
- Resource alert
- Gensyn identity tools

---

## ❤️ Credits
Built with ❤️ by **Deklan × GPT-5**

<END>
