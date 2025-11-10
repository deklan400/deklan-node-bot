# 🚀 Deklan Node Bot
> Telegram Bot untuk **Monitoring & Control** Gensyn RL-Swarm Node

![Banner](https://i.imgur.com/VH3beOn.png)

Bot ini dibuat untuk mempermudah pengelolaan node Gensyn dari Telegram.
Semua fungsi utama node dapat dilakukan langsung dari UI Telegram:
start/stop/restart node, cek status CPU/RAM/Disk, lihat round, tail log, dan auto-monitoring.

---

## ✨ Fitur Utama

✅ UI tombol via Telegram  
✅ Notifikasi performa & status node  
✅ Start / Stop / Restart node  
✅ Cek status CPU / RAM / Disk / Uptime  
✅ Cek round terakhir  
✅ Ambil logs secara realtime  
✅ Auto-monitor setiap X menit (bisa diatur)  
✅ Auto-restart jika node mati  
✅ Access whitelist untuk keamanan  
✅ One-command install  
✅ Systemd service + timer  

---

## 📦 Struktur Repo

deklan-node-bot/
├── bot.py
├── monitor.py
├── .env.example
├── install.sh
├── requirements.txt
├── bot.service
├── monitor.service
├── monitor.timer
└── README.md

---

# ⚡ Instalasi Cepat

> Jalankan perintah berikut di VPS:

```bash
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)

Setelah selesai, file akan terpasang otomatis di:
/opt/deklan-node-bot

⚙️ Konfigurasi

Edit file .env:
nano /opt/deklan-node-bot/.env

Contoh isi:

BOT_TOKEN=123456:ABC-your-bot-token
CHAT_ID=123456789
NODE_NAME=deklan-node
ALLOWED_USER_IDS=123456,888888       # optional
MONITOR_EVERY_MINUTES=180
LOG_LINES=50

Simpan lalu restart:
sudo systemctl restart bot

✅ Cara Kerja

✅ bot.service
→ Handle Telegram bot (start/stop/status/logs/round)

✅ monitor.timer + monitor.service
→ Kirim status tiap X menit, auto-restart jika node mati

✅ Node utamanya wajib bernama:
gensyn

▶️ Jalankan / Cek Layanan
💠 Cek status bot
systemctl status bot

💠 Restart bot
systemctl restart bot

💠 Live logs
journalctl -u bot -f

🤖 Telegram Control Menu

Ketik:

/start

Akan muncul tombol UI:

Tombol	Fungsi
✅ Status	Cek CPU/RAM/Disk/Uptime
▶️ Start	Start node
⏹ Stop	Stop node
🔄 Restart	Restart node
📜 Logs	Tail logs
🔁 Round	Info round terakhir

UI sudah auto-inline + akses dibatasi ke CHAT_ID/ALLOWED_USER_IDS ✅

🔄 Auto Monitoring

Timer bawaan:

monitor.timer

Default → tiap 3 jam (180 min)

Fungsi:
✅ cek node aktif
✅ kirim ringkasan sistem
✅ auto-restart kalau mati
✅ kirim notifikasi Telegram

Manual jalankan monitor sekarang:

systemctl start monitor.service

🔥 Useful Commands

Bot
systemctl status bot
systemctl restart bot
journalctl -u bot -f

Node
systemctl status gensyn
systemctl restart gensyn
systemctl stop gensyn
systemctl start gensyn
journalctl -u gensyn -f

Monitoring
systemctl status monitor.timer
systemctl status monitor.service
journalctl -u monitor.service -f

🛠 Manual Install (opsional)

git clone https://github.com/deklan400/deklan-node-bot
cd deklan-node-bot
pip3 install -r requirements.txt
cp .env.example .env
nano .env
python3 bot.py

❌ Uninstall

sudo systemctl disable --now bot monitor.timer
sudo rm -rf /opt/deklan-node-bot
sudo rm /etc/systemd/system/{bot.service,monitor.service,monitor.timer}
sudo systemctl daemon-reload

🧠 Tips

✅ Simpan BOT_TOKEN & CHAT_ID baik-baik
✅ Bisa whitelist beberapa user
✅ Ubah MONITOR_EVERY_MINUTES sesuai kebutuhan
✅ Bisa ubah jumlah LOG_LINES

❓ Troubleshooting
Masalah	Solusi
Bot tidak respon	Cek .env, restart service
Tidak ada notifikasi	Pastikan CHAT_ID benar
Monitor tidak jalan	systemctl start monitor.service
Node mati	Monitor akan auto-restart

📜 License

MIT — bebas digunakan

💎 Credits

Developer: Deklan Labz

Enjoy full-power control dari Telegram!
Gak perlu login VPS lagi ✅
