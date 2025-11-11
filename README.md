# ⚡ Gensyn RL-Swarm + Deklan Node Bot
### ✅ One-Command Auto Install • Systemd • Telegram Control • Auto-Heal • Swap Manager

<p align="center">
  <img src="https://i.ibb.co/3zxGBM4/GENSYN-BANNER.png" width="90%">
</p>

<p align="center">
  RL-Swarm Node • Auto Installer • Telegram Control • Auto Monitor • Danger Zone
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Gensyn-Testnet-navy?style=for-the-badge">
  <img src="https://img.shields.io/badge/Telegram-Bot-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/AutoMonitor-YES-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Systemd-Supported-purple?style=for-the-badge">
  <img src="https://img.shields.io/badge/Linux-Ubuntu%2022.04-red?style=for-the-badge">
</p>

---

# ✅ Fitur Utama
## ✅ RL-Swarm Node (CPU)
✔ One-command installer  
✔ Auto identity (new user)  
✔ Auto symlink keys  
✔ Auto docker build + pull  
✔ Auto systemd  
✔ Auto restart  
✔ Reinstall / Update / Uninstall  
✔ Easy migrate server  
✔ Stable & lightweight  

## ✅ Telegram Bot
✔ Start / Stop / Restart  
✔ View Status & Uptime  
✔ Cek Round  
✔ View Logs  
✔ Installer: Install / Reinstall / Update / Uninstall  
✔ Swap Manager  
✔ Auto Monitor → Restart → Reinstall  
✔ Multi-Admin  
✔ Danger Zone (password)  
✔ Anti-spam UP/DOWN  

---

# ✅ Folder Struktur
```
/root/deklan/
│── swarm.pem
│── userApiKey.json
└── userData.json

/root/rl-swarm/
│── docker-compose.yaml
│── run_node.sh
│── .env
│── user/
│   └── keys → symlink → /root/deklan
└── ...
```

Telegram Bot:
```
/opt/deklan-node-bot
├── bot.py
├── monitor.py
├── install.sh
├── bot.service
├── monitor.service
├── monitor.timer
├── requirements.txt
└── .env
```

Symlink:
```
/root/rl-swarm/keys → /root/deklan
```

---

# 🚀 INSTALASI

## ✅ 1) Install RL-Swarm
```
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-autoinstall/main/install.sh)
```

## ✅ 2) Install Telegram Bot
```
bash <(curl -s https://raw.githubusercontent.com/deklan400/deklan-node-bot/main/install.sh)
```

---

# ✅ Identity Files
| File | Fungsi |
|------|--------|
| swarm.pem | Private key |
| userApiKey.json | API Auth |
| userData.json | Metadata |

Lokasi:
```
/root/deklan/
```

---

# ✅ Node Control
```
systemctl start gensyn
systemctl stop gensyn
systemctl restart gensyn
systemctl status gensyn --no-pager
journalctl -u gensyn -f
```

---

# ✅ Telegram Control
| Command | Fungsi |
|---------|--------|
| /start | Menu |
| /status | Resource & Round |
| /logs | Last logs |
| /restart | Restart node |
| /round | Last round |
| /help | Bantuan |

Menu:
📊 Status  
🟢 Start  
🔴 Stop  
🔁 Restart  
📜 Logs  
ℹ Round  
🧹 Safe Clean  
💾 Swap Manager  
🧩 Installer  
⚠ Danger Zone  

---

# ✅ Installer Menu
Melalui bot:
- Install
- Reinstall
- Update
- Uninstall

Flow:
1) Klik tombol  
2) Bot konfirmasi  
3) Reply “YES”  
4) Bot jalan script  

Base URL:
```
AUTO_INSTALLER_GITHUB
```

---

# ✅ Swap Manager
Preset:
- 16G
- 32G
- 64G
- Custom

Automasi:
- swapoff
- recreate /swapfile
- update /etc/fstab
- swapon

---

# ✅ Auto Monitor (Self Heal)
Systemd Timer: `monitor.timer`

Flow:
Check → Restart → Reinstall → Notify FAIL

Jika node DOWN → restart  
Gagal → reinstall  
Gagal → kirim log  

Status file:
```
/tmp/.node_status.json
```

---

# ✅ Service Files
```
/etc/systemd/system/gensyn.service
/etc/systemd/system/bot.service
/etc/systemd/system/monitor.service
/etc/systemd/system/monitor.timer
```

---

# ✅ Manual Uninstall
Node:
```
systemctl stop gensyn
systemctl disable gensyn
rm -f /etc/systemd/system/gensyn.service
rm -rf /root/rl-swarm
systemctl daemon-reload
```

Bot:
```
systemctl stop bot monitor.service monitor.timer
systemctl disable bot monitor.service monitor.timer
rm -f /etc/systemd/system/bot.service
rm -f /etc/systemd/system/monitor.*
rm -rf /opt/deklan-node-bot
systemctl daemon-reload
```

Identity tetap aman:
```
/root/deklan/
```

---

# ✅ Troubleshooting
| Masalah | Solusi |
|--------|--------|
| Node mati | systemctl restart gensyn |
| No logs | journalctl -u gensyn -f |
| Identity hilang | login WebUI ulang |
| Repo error | reinstall.sh |
| Disk full | Safe clean |
| Docker issue | docker system prune -af |
| Missing keys | check /root/deklan |

---

# ✅ Backup
```
/root/deklan/swarm.pem
/root/deklan/userApiKey.json
/root/deklan/userData.json
```

Jangan share!

---

# ✅ Next Features
- Multi-node DB
- Auto update bot
- Dashboard web
- Remote deploy
- Auto discovery

---

# ❤️ Credits
Built with ❤️ by **Deklan × GPT-5**
