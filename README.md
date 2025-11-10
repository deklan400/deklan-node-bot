<!-- BANNER -->
<p align="center">
  <img src="https://i.ibb.co/3zxGBM4/GENSYN-BANNER.png" width="90%" />
</p>

<h1 align="center">🖤 Deklan Node Bot</h1>
<p align="center">
  Telegram Control & Auto-Monitor for Gensyn RL-Swarm Nodes
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Gensyn-Testnet-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Telegram-Bot-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Auto--Monitor-YES-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Systemd-Supported-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/Linux-Ubuntu%2022.04-purple?style=for-the-badge">
</p>

---

## 🧠 Overview

**Deklan Node Bot** memudahkan kontrol & monitoring node **Gensyn RL-Swarm**  
↪ lewat Telegram ✅  
↪ tanpa SSH ✅  
↪ otomatis pantau ✅  

Kamu bisa:
✅ Start / Stop / Restart node  
✅ Baca logs langsung di Telegram  
✅ Cek CPU, RAM, Disk & Round  
✅ Notifikasi otomatis kalau node mati  
✅ Auto-restart bila down  

> Semua cukup dari HP 📱

---

## ⚡ Features

✅ CPU / RAM / Disk / Uptime checker  
✅ Start / Stop / Restart node (systemd)  
✅ Cek round terbaru  
✅ Ambil log terakhir  
✅ Auto monitoring tiap X menit  
✅ Auto restart + auto notify  
✅ Telegram UI tombol  
✅ User Allowlist (AMAN)  
✅ systemd background  
✅ Zero-maintenance  

> FULL CONTROL — langsung dari Telegram 🚀  

---

## 🚀 Quick Install

> Jalankan ini di VPS 🔽

```bash
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

Bot otomatis:
✅ Install dependency  
✅ Setup folder  
✅ Install + enable services  

🎉 DONE

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
ALLOWED_USER_IDS=123456789
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

⚠ Minimal wajib → BOT_TOKEN + CHAT_ID  

---

## 🎛 Systemd Service

🔎 Check bot
```bash
systemctl status bot
```

♻ Restart bot
```bash
systemctl restart bot
```

📡 Logs
```bash
journalctl -u bot -f
```

▶ Run monitor now
```bash
systemctl start monitor.service
```

⏱ Timer check
```bash
systemctl status monitor.timer
```

---

## 💬 Telegram Menu

Ketik:

```
/start
```

Tombol muncul:

| Tombol | Fungsi |
|--------|--------|
| 📊 Status | CPU/RAM/Disk/Uptime |
| 🟢 Start | Start node |
| 🔴 Stop | Stop node |
| 🔁 Restart | Restart node |
| 📜 Logs | Logs |
| 🔢 Round | Round terbaru |

---

## 🔔 Sample Alerts

✅ Node OK
```
✅ Gensyn-01 OK
CPU 31% • RAM 67% • Disk 70%
Round: 18735
```

⛔ Node mati
```
🚨 Gensyn-01 DOWN
Attempting auto-restart…
```

🟢 Pulih
```
🟢 Node recovered
CPU 30% • RAM 63% • Disk 71%
```

❌ Gagal
```
❌ FAILED TO RECOVER
(last logs)
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

> Tambahkan folder `images/`

```
/images/menu.png
/images/status.png
/images/logs.png
```

---

## 🛣 Roadmap

- Multi-node support  
- Web dashboard  
- Auto update  
- Multi alert rules  
- Cluster support  

---

## ❤️ Credits  

Built with ❤️ by **Deklan**
