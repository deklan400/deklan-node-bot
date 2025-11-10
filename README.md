<h1 align="center">🖤 Deklan Node Bot</h1>

<p align="center">
  Control & Auto-Monitor Gensyn RL-Swarm Nodes via Telegram
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Gensyn-Testnet-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Telegram-Bot-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Auto--Monitor-YES-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Systemd-Supported-yellow?style=for-the-badge">
</p>

---

## 🧠 Overview

**Deklan Node Bot** = cara termudah untuk mengontrol & memonitor node **Gensyn RL-Swarm**  
→ Cukup lewat Telegram ✅  

Tanpa SSH, tanpa ribet.  
Start / Stop / Restart / Logs, semua di tombol Telegram.

---

## ⚡ Features

✅ CPU / RAM / Disk / Uptime checker  
✅ Start/Stop/Restart node  
✅ Cek round terakhir  
✅ Display logs langsung di Telegram  
✅ Auto monitoring per X menit  
✅ Auto-restart kalau node mati  
✅ Notif Telegram otomatis  
✅ systemd daemon → auto start  
✅ Allowlist user → aman  

---

## 🚀 Install

> Jalankan perintah ini:

```bash
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

Bot:
✔ install dependensi  
✔ copy service  
✔ auto start  

---

## ⚙️ Konfigurasi `.env`

Edit file:

```bash
nano /opt/deklan-node-bot/.env
```

Contoh:

```
BOT_TOKEN=YOUR_BOT_TOKEN
CHAT_ID=123456789
ALLOWED_USER_IDS=1234,5678
NODE_NAME=Gensyn-VPS-01
MONITOR_EVERY_MINUTES=180
LOG_LINES=50
```

| Key | Wajib | Deskripsi |
|-----|:----:|-----------|
| BOT_TOKEN | ✅ | Token Telegram |
| CHAT_ID | ✅ | ID admin |
| ALLOWED_USER_IDS | ❌ | Daftar allowed user |
| NODE_NAME | ❌ | Nama VPS |
| MONITOR_EVERY_MINUTES | ❌ | Interval |
| LOG_LINES | ❌ | Baris log |

> Minimal wajib → BOT_TOKEN & CHAT_ID

---

## 🎛 Systemd Usage

Cek status bot:

```bash
systemctl status bot
```

Restart bot:

```bash
systemctl restart bot
```

Logs:

```bash
journalctl -u bot -f
```

Monitor now:

```bash
systemctl start monitor.service
```

Cek timer:

```bash
systemctl status monitor.timer
```

---

## 💬 Telegram UI

👉 Ketik:

```
/start
```

📌 Akan muncul tombol:

| Tombol | Fungsi |
|--------|--------|
| 📊 Status | CPU/RAM/Disk/Uptime |
| 🟢 Start | Start node |
| 🔴 Stop | Stop node |
| 🔁 Restart | Restart node |
| 📜 Logs | Logs |
| 🔢 Round | Round |

---

## 🔔 Sample Alerts

✅ Node OK
```
✅ Gensyn-01 OK
CPU 31% • RAM 67% • Disk 70%
Round: 18735
```

⚠ Node Mati
```
🚨 Gensyn-01 DOWN
Auto-restart…
```

Recovered
```
🟢 Node recovered
CPU 30% • RAM 63% • Disk 71%
```

Failed
```
❌ FAILED TO RECOVER
(last logs)
```

---

## 📁 Struktur

```
/opt/deklan-node-bot
├── bot.py
├── monitor.py
├── install.sh
├── requirements.txt
├── bot.service
├── .env
└── .env.example
```

---

## 🗑 Uninstall

```bash
systemctl stop bot monitor.service monitor.timer
systemctl disable bot monitor.service monitor.timer
rm -f /etc/systemd/system/bot.service
rm -f /etc/systemd/system/monitor.*
rm -rf /opt/deklan-node-bot
systemctl daemon-reload
```

---

## 🌙 Screenshots

> Tambahkan folder `images/` di repo

```
/images/menu.png
/images/status.png
/images/logs.png
```

---

## 🛣 Roadmap

- Multi-node sync  
- Web UI dashboard  
- Auto update  
- More Alert types  
- Cluster support  

---

## ❤️ Credits

Built with ❤️ by **Deklan**

