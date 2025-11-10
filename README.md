# 🤖 Deklan Node Bot  
> Telegram Control & Auto-Monitor for Gensyn RL-Swarm Nodes 🚀  

Bot ini memungkinkan kamu memantau & mengontrol node Gensyn dari Telegram.  
Tanpa perlu login server → praktis, aman, otomatis ✅  

---

## ✨ Fitur Utama

✅ Cek CPU / RAM / Disk / Uptime  
✅ Start / Stop / Restart Node  
✅ Ambil Logs terbaru  
✅ Cek Round terakhir  
✅ UI tombol Telegram (bukan command)  
✅ Auto-monitor tiap X menit  
✅ Auto restart + notifikasi  
✅ Akses aman (whitelist user)  
✅ Systemd service → auto start  

---

## 🚀 Instalasi Cepat

> Jalankan perintah ini di VPS:

```bash
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

Bot otomatis:
✅ Install dependency  
✅ Clone repo  
✅ Setup systemd  
✅ Start bot  

---

## ⚙️ Konfigurasi `.env`

Edit:

```bash
nano /opt/deklan-node-bot/.env
```

Contoh:

```
BOT_TOKEN=123456:abcdefgxxxxxxxx
CHAT_ID=12345678
ALLOWED_USER_IDS=1234,5678
NODE_NAME=Gensyn-VPS-01
MONITOR_EVERY_MINUTES=180
LOG_LINES=50
```

| Key | Wajib | Fungsi |
|-----|:----:|--------|
| BOT_TOKEN | ✅ | Token bot |
| CHAT_ID | ✅ | ID admin |
| ALLOWED_USER_IDS | ❌ | Banyak user |
| NODE_NAME | ❌ | Nama VPS |
| MONITOR_EVERY_MINUTES | ❌ | Interval |
| LOG_LINES | ❌ | Baris log |

> Minimal wajib → BOT_TOKEN + CHAT_ID ✅  

---

## 🎛 Systemd

### Cek status bot
```bash
systemctl status bot
```

### Restart bot
```bash
systemctl restart bot
```

### Live logs
```bash
journalctl -u bot -f
```

### Jalankan monitor manual
```bash
systemctl start monitor.service
```

### Cek timer
```bash
systemctl status monitor.timer
```

---

## 💬 Telegram Control

Ketik:

```
/start
```

Bot menampilkan tombol menu:

| Tombol | Fungsi |
|--------|--------|
| 📊 Status | CPU/RAM/Disk/Uptime |
| 🟢 Start | Start service |
| 🔴 Stop | Stop service |
| 🔁 Restart | Restart |
| 📜 Logs | Logs |
| ℹ️ Round | Round |

---

## 🔔 Contoh Notifikasi

```
✅ Gensyn-01 OK @ 2025-01-01 10:33
CPU 35% • RAM 62% • Disk 70%
Joining round: 18735
```

Jika node mati:
```
🚨 Gensyn-01 DOWN @ 10:33
Attempting auto-restart…
```

Jika pulih:
```
🟢 Gensyn-01 recovered
CPU 35% • RAM 61% • Disk 71%
```

Jika gagal:
```
❌ FAILED TO RECOVER
(last 80 log lines)
```

---

## 📁 Struktur Repo

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

## 🔌 Service Target

Bot mengontrol service bernama:

```
gensyn
```

> Pastikan node jalan via systemd:
```
systemctl status gensyn
```

---

## 🛣 Roadmap

- Multi-server support  
- Web dashboard  
- Auto update node  
- Multi alert rules  
- Multi log collector  

---

## ❤️ Credits  

Built with ❤️ by **Deklan**

