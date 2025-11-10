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
langsung dari Telegram.

✔ Tanpa SSH  
✔ Otomatis pantau node  
✔ Auto-restart jika mati  

📱 Cukup dari HP!

---

## ⚡ Features

✅ Start / Stop / Restart node  
✅ Show logs dari Telegram  
✅ CPU, RAM, Disk, Uptime monitor  
✅ Cek Round terakhir  
✅ Auto-monitor tiap X menit  
✅ Auto Restart + Notifikasi  
✅ Telegram Inline Keyboard  
✅ User Allowlist (AMAN)  
✅ Systemd background  

> FULL CONTROL — langsung dari Telegram 🚀

---

## 🚀 Quick Install

> Jalankan di VPS (Ubuntu 22.04+)

```bash
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

✅ Install dependencies  
✅ Setup venv + env  
✅ Install services  
✅ Start bot & monitoring  

🎉 DONE

---

## ⚙️ Konfigurasi `.env`

Edit config:

```bash
nano /opt/deklan-node-bot/.env
```

Contoh:

```
BOT_TOKEN=YOUR_TELEGRAM_TOKEN
CHAT_ID=123456789
ALLOWED_USER_IDS=123456789
NODE_NAME=Gensyn-VPS-01
SERVICE_NAME=gensyn
MONITOR_EVERY_MINUTES=180
LOG_LINES=60
ENABLE_DANGER_ZONE=0
DANGER_PASS=CHANGEME
```

| Key | Wajib | Deskripsi |
|-----|:----:|-----------|
| BOT_TOKEN | ✅ | Token Telegram |
| CHAT_ID | ✅ | ID admin |
| ALLOWED_USER_IDS | ❌ | Multi-user whitelist |
| SERVICE_NAME | ❌ | systemd service |
| NODE_NAME | ❌ | Label VPS |
| MONITOR_EVERY_MINUTES | ❌ | Interval monitor |
| LOG_LINES | ❌ | Log count |
| ENABLE_DANGER_ZONE | ❌ | Show menu berbahaya |
| DANGER_PASS | ❌ | Password Danger-Zone |

> ⚠ Minimal wajib → BOT_TOKEN + CHAT_ID

---

## 🎛 Systemd Commands

🔎 Status bot
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

| Tombol | Fungsi |
|--------|--------|
| 📊 Status | CPU/RAM/Disk/Uptime |
| 🟢 Start | Start node |
| 🔴 Stop | Stop node |
| 🔁 Restart | Restart node |
| 📜 Logs | Logs terakhir |
| ℹ️ Round | Info round |

---

## ⚠️ DANGER ZONE

> Default → **OFF**

Aktifkan via `.env`:

```
ENABLE_DANGER_ZONE=1
DANGER_PASS=SANDIKU
```

Menu Tambahan:

| Tombol | Aksi |
|--------|------|
| 🔥 Remove RL-Swarm | Hapus node |
| 🐋 Clean Docker | Remove Docker |
| 💾 Remove Swap | Hapus swapfile |
| 🧹 Full Clean | Bersih total |
| 🔁 Reboot VPS | Restart server |

> ⚠ PASSWORD WAJIB  
> ⚠ Pastikan paham sebelum eksekusi

---

## 🔔 Contoh Notifikasi

✅ Node OK
```
✅ Gensyn-01 OK @ 20:31
CPU 31% • RAM 67% • Disk 70%
Round: 18735
```

⛔ Node Down
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
├── monitor.service
├── monitor.timer
├── .env
└── .env.example
```

---

## 🔄 Update Bot

```bash
cd /opt/deklan-node-bot
git pull
systemctl restart bot
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

## ❗ Troubleshooting

| Issue | Solusi |
|-------|--------|
| Bot tidak respon | restart bot |
| Timer tidak jalan | cek monitor.timer |
| Node STOPPED | cek `SERVICE_NAME` |
| Logs kosong | tambah `LOG_LINES` |
| Danger zone hilang | ENABLE_DANGER_ZONE=1 |

---

## 🛣 Roadmap

- Multi-Node support  
- Web dashboard  
- Auto update  
- Multi alert rules  
- Cluster support  

---

## ❤️ Credits

Built with ❤️ by **Deklan**
