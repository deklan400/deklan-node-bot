# 🤖 Deklan Node Bot — Telegram Control & Monitoring

Bot Telegram untuk monitoring & mengendalikan **Gensyn RL-Swarm Node** langsung dari HP 📱  
Tanpa repot login server! Full otomatis.  

---

## ✨ Fitur Utama

✅ Cek status CPU / RAM / Disk / Uptime  
✅ Start / Stop / Restart Node  
✅ Lihat Logs  
✅ Cek Round terbaru  
✅ Akses aman (ALLOWLIST)  
✅ Auto-monitor tiap X menit  
✅ systemd background service  
✅ Menu tombol Telegram  

---

## 🚀 1) Instalasi Cepat

> Jalankan perintah ini:

```bash
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

Bot otomatis:
✅ Install dependensi  
✅ Setup folder  
✅ Install service  
✅ Auto-start  

---

## ⚙️ 2) Konfigurasi

Buka file konfigurasi:

```bash
nano /opt/deklan-node-bot/.env
```

Contoh isi:

```
BOT_TOKEN=123456:abcdefgxxxxxxxx
CHAT_ID=12345678
ALLOWED_USER_IDS=123456,987654
NODE_NAME=Gensyn-01
MONITOR_INTERVAL=10
```

| Key | Fungsi |
|-----|--------|
| BOT_TOKEN | Token Telegram Bot |
| CHAT_ID | ID Admin |
| ALLOWED_USER_IDS | (opsional) daftar user |
| NODE_NAME | Nama node |
| MONITOR_INTERVAL | Cek otomatis (menit) |

> Minimal wajib: **BOT_TOKEN + CHAT_ID**

---

## 🏃 3) Jalankan / Cek Status

Cek status bot:

```bash
systemctl status bot
```

Restart bot:

```bash
systemctl restart bot
```

Monitoring timer:

```bash
systemctl start monitor.timer
```

Cek timer:

```bash
systemctl status monitor.timer
```

Jalankan monitor manual:

```bash
systemctl start monitor.service
```

---

## 💬 4) Telegram Commands

Ketik:

```
/start
```

→ Bot akan tampilkan menu tombol ✅  

### Aksi:

| Menu | Fungsi |
|------|--------|
| ✅ Status | Info CPU / RAM / Disk / Up |
| ▶ Start | Start node |
| ⏹ Stop | Stop node |
| 🔄 Restart | Restart node |
| 📜 Logs | Tampilkan logs |
| 🔢 Round | Round terbaru |

---

## 📁 5) Lokasi File Penting

| Lokasi | Fungsi |
|--------|--------|
| `/opt/deklan-node-bot/` | Folder bot |
| `bot.py` | Main bot |
| `.env` | Config |
| `bot.service` | systemd bot |
| `monitor.*` | Monitoring service |

---

## ⏱ 6) Auto Monitoring

✅ Tiap X menit bot cek:
- Node berjalan atau mati
- Round naik / macet

Bila ada masalah = **notif Telegram otomatis** ✅  

---

## ❌ Uninstall

```
systemctl stop bot monitor.service monitor.timer
systemctl disable bot monitor.service monitor.timer
rm /etc/systemd/system/bot.service
rm /etc/systemd/system/monitor.*
rm -rf /opt/deklan-node-bot
```

---

## 🧩 Struktur Repo

```
deklan-node-bot
│── bot.py
│── install.sh
│── requirements.txt
│── .env.example
└── bot.service
```

---

## 📡 Contoh Output Telegram

```
🟢 NODE RUNNING
CPU: 35%
RAM: 62%
Disk: 70%
Uptime: 12h 21m
Round: 18735
```

atau:

```
🔴 NODE STOPPED
Last Round: 18735
```

---

## 🛣 Roadmap

- Multi-node
- Web UI
- Cluster manager
- Auto-update
- Auto backup

---

## ❤️ Credits

Built with ❤️ by **Deklan**

END OF README
