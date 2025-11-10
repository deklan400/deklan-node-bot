<!-- BANNER -->
<p align="center">
  <img src="https://i.ibb.co/3zxGBM4/GENSYN-BANNER.png" width="90%" />
</p>

<h1 align="center">🖤 Deklan Node Bot v2</h1>
<p align="center">
  Telegram Control + Auto-Monitor + One-Click Installer for Gensyn RL-Swarm Nodes
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

**Deklan Node Bot** adalah Telegram bot untuk mengontrol & monitor  
node **Gensyn RL-Swarm** — TANPA SSH ✅

Fitur:
✅ Start / Stop / Restart node  
✅ Cek CPU, RAM, Disk, Uptime  
✅ Cek latest round  
✅ Ambil log langsung via Telegram  
✅ Auto-monitor + auto-restart + alert  
✅ Install / Reinstall / Update / Uninstall node dari Telegram  
✅ Danger Zone (password protected)  
✅ Multiple allowed users  

> 📱 Semua cukup dari HP

---

## ⚡ Features

✅ Telegram UI  
✅ Live resource usage  
✅ Log viewer  
✅ Auto-monitor  
✅ Auto-install node  
✅ Reinstall / update  
✅ Danger zone (secured)  
✅ systemd integration  

---

## 🚀 Quick Install — BOT

> Jalankan di VPS

```bash
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

Akan otomatis:
✅ Install dependencies  
✅ Clone repo  
✅ Setup virtualenv  
✅ Setup + start bot service  
✅ Setup + start monitoring timer  

---

## ⚙️ Konfigurasi `.env`

```bash
nano /opt/deklan-node-bot/.env
```

Isi:

```
BOT_TOKEN=YOUR_TOKEN
CHAT_ID=123456

ALLOWED_USER_IDS=123456,54321

SERVICE_NAME=gensyn
NODE_NAME=Gensyn-VPS

LOG_LINES=50
MONITOR_EVERY_MINUTES=180

ENABLE_DANGER_ZONE=1
DANGER_PASS=12345

AUTO_INSTALLER_GITHUB=https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/
```

> Minimal wajib → BOT_TOKEN + CHAT_ID

---

### 🧩 ENV Table

| Key | Wajib | Fungsi |
|-----:|:----:|--------|
| BOT_TOKEN | ✅ | Token Telegram |
| CHAT_ID | ✅ | Admin |
| ALLOWED_USER_IDS | ❌ | User tambahan |
| SERVICE_NAME | ❌ | Nama node service |
| NODE_NAME | ❌ | Label VPS |
| LOG_LINES | ❌ | Jumlah log |
| MONITOR_EVERY_MINUTES | ❌ | Monitoring interval |
| ENABLE_DANGER_ZONE | ❌ | Aktifkan fitur |
| DANGER_PASS | ❌ | Password Danger |
| AUTO_INSTALLER_GITHUB | ✅ | Source installer |

---

## 📡 Telegram Commands

| Command | Fungsi |
|--------|--------|
| /start | Tampilkan menu |
| /status | CPU/RAM/Disk/Uptime |
| /logs | Show logs |
| /restart | Restart node |
| /round | Show last round |
| /help | Help |

---

## 🧩 Telegram Menu

| Tombol | Fungsi |
|--------|--------|
| 📊 Status | Resource |
| 🟢 Start | Start node |
| 🔴 Stop | Stop node |
| 🔁 Restart | Restart node |
| 📜 Logs | Show logs |
| ℹ️ Round | Last round |
| 🧩 Installer | Menu installer |
| ⚠ Danger Zone | Tools khusus |

---

## 🔧 Installer Menu

Tombol:
✅ Install  
✅ Reinstall  
✅ Update  
✅ Uninstall  

Konfirmasi:  
Ketik **YES** / **NO**

Bot akan ambil script dari:
```
https://github.com/deklan400/deklan-autoinstall
```

---

## ⚠ Danger Zone

> Wajib ENABLE + isi DANGER_PASS

Aksi:

| Fungsi |
|--------|
| Remove RL-Swarm |
| Clean Docker |
| Remove Swap |
| Full Clean |
| Reboot VPS |

---

## 🛰 Auto Monitor

- Cek node berkala
- Auto restart
- Kirim alert
- Dump logs jika fail

Cek timer:
```
systemctl status monitor.timer
```

---

## 🔥 Systemd

### Bot
```
systemctl status bot
journalctl -u bot -f
```

### Monitor
```
systemctl status monitor.service
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
└── .env.example
```

---

## 📦 Auto-Installer Remote

Script remote diambil dari:

```
https://github.com/deklan400/deklan-autoinstall
```

File:
- install.sh
- reinstall.sh
- uninstall.sh

> Bisa update script tanpa update bot ✅

---

## ✅ Example Alerts

✅ Node OK
```
✅ Gensyn-01 OK
CPU 32% • RAM 71% • Disk 62%
Last round: xxx
```

🚨 Node mati
```
🚨 DOWN — auto-restart
```

🟢 Recovered
```
🟢 RECOVERED
```

❌ Still Down
```
❌ FAILED — check logs
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

- Multi-node
- Web dashboard
- Auto update bot
- CPU/RAM alert rules
- Gensyn identity mgmt
- Install multi service

---

## ❤️ Credits
Built with ❤️ by **Deklan + GPT-5**
