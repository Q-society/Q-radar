<div align="center">

```
   ___        ____      _    ___    _    ____  
  / _ \      |  _ \    / \  |  _ \ / \  |  _ \ 
 | | | |_____| |_) |  / _ \ | | | / _ \ | |_) |
 | |_| |_____|  _ <  / ___ \| |_| / ___ \|  _ < 
  \__\_\     |_| \_\/_/   \_\____/_/   \_\_| \_\
```

### 📡 Local Network Device Scanner

A fast, multi-threaded LAN/Wi-Fi scanner that finds **real devices** on your network — combining a ping sweep with the kernel's ARP table, reverse DNS, and NetBIOS lookups to show you IP, MAC, vendor, and device name in one clean table.

<p align="center">
  <a href="https://github.com/Q-society/Q-radar/stargazers">
    <img src="https://img.shields.io/github/stars/Q-society/Q-radar?style=for-the-badge&color=ffd700&label=STARS&logo=github" alt="Stars">
  </a>
  <a href="https://github.com/Q-society/Q-radar/network/members">
    <img src="https://img.shields.io/github/forks/Q-society/Q-radar?style=for-the-badge&color=4ec9b0&label=FORKS&logo=github" alt="Forks">
  </a>
  <a href="https://github.com/Q-society/Q-radar/issues">
    <img src="https://img.shields.io/github/issues/Q-society/Q-radar?style=for-the-badge&color=ff6b6b&label=ISSUES&logo=github" alt="Issues">
  </a>
  <a href="https://github.com/Q-society/Q-radar/commits/main">
    <img src="https://img.shields.io/github/last-commit/Q-society/Q-radar?style=for-the-badge&color=blueviolet&label=LAST%20COMMIT&logo=github" alt="Last Commit">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Kali%20Linux%20|%20Termux-1f6feb?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.7%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/root-not%20required-success?style=for-the-badge&logo=android&logoColor=white" alt="Root">
  <img src="https://img.shields.io/badge/dependencies-zero-orange?style=for-the-badge" alt="Dependencies">
  <img src="https://img.shields.io/badge/status-actively%20maintained-brightgreen?style=for-the-badge" alt="Status">
</p>

<p align="center">
  <a href="https://github.com/Q-society/Q-radar/stargazers">
    <img src="https://img.shields.io/badge/⭐-Star%20this%20repo-ffd700?style=for-the-badge&logoColor=black" alt="Star this repo">
  </a>
  <a href="https://github.com/Q-society/Q-radar/fork">
    <img src="https://img.shields.io/badge/🍴-Fork%20this%20repo-4ec9b0?style=for-the-badge&logoColor=black" alt="Fork this repo">
  </a>
  <a href="https://github.com/Q-society/Q-radar/issues/new">
    <img src="https://img.shields.io/badge/🐛-Report%20a%20bug-ff6b6b?style=for-the-badge&logoColor=black" alt="Report a bug">
  </a>
  <a href="https://github.com/Q-society">
    <img src="https://img.shields.io/badge/👥-Follow%20Q--society-8a2be2?style=for-the-badge&logoColor=white" alt="Follow Q-society">
  </a>
</p>

</div>

---

## ✨ Features

- 🚀 **Multi-threaded ping sweep** — scans an entire `/24` subnet in seconds (80 concurrent workers)
- 🧠 **ARP table cross-reference** — pulls MAC addresses straight from the kernel's neighbor cache (`/proc/net/arp`)
- 🏷️ **Vendor lookup** — identifies common device manufacturers from MAC OUI prefixes (Apple, Samsung, TP-Link, Raspberry Pi, etc.)
- 🔍 **Real device name resolution** — tries reverse DNS first, then falls back to a live NetBIOS (NBSTAT) query on UDP/137
- 🎨 **Clean terminal UI** — animated progress bar, 3D ASCII banner, color-coded results table
- 📱 **No root required** — works out of the box on Termux (Android) and any standard Linux distro
- 🪶 **Zero external dependencies** — pure Python 3 standard library

---

## 🖥️ Preview

```
[*] Local IP: 192.168.1.42
[*] Scanning network: 192.168.1.0/24
[*] Targets: 253 hosts

[██████████████████████████████] 100% (253/253)

[+] Scan finished in 4.2s — 6 device(s) responded.

┌──────────────────────┬───────────────────┬─────────────┬─────────────────┐
│ IP ADDRESS           │ MAC ADDRESS       │ VENDOR      │ DEVICE NAME     │
├──────────────────────┼───────────────────┼─────────────┼─────────────────┤
│ 192.168.1.1          │ AC:84:C6:11:22:33 │ TP-Link     │ router          │
│ 192.168.1.42 (you)   │ 3C:5A:B4:44:55:66 │ Apple       │ macbook-pro     │
│ 192.168.1.50         │ DC:A6:32:77:88:99 │ Raspberry Pi│ raspberrypi     │
└──────────────────────┴───────────────────┴─────────────┴─────────────────┘
```

---

## 📦 Requirements

| Requirement | Notes |
|---|---|
| Python 3.7+ | Uses only standard library modules |
| `ping` binary | Comes preinstalled on Linux & Termux |
| Network access | Must be connected to the Wi-Fi/LAN you want to scan |

---

## ⚙️ Installation

### 🐉 Kali Linux

```bash
sudo apt update && sudo apt install -y python3 iputils-ping
git clone https://github.com/Q-society/Q-radar.git
cd Q-radar
chmod +x q-radar.py
python3 q-radar.py
```

### 📱 Termux (Android — no root required)

```bash
pkg update && pkg upgrade -y
pkg install -y python git
git clone https://github.com/Q-society/Q-radar.git
cd Q-radar
python q-radar.py
```

> ⚠️ On Termux, grant local network permission if prompted, and make sure Wi-Fi is connected (not mobile data) so the scan covers the right subnet.

---

## ▶️ Usage

Run the script and pick an option from the menu:

```bash
python3 q-radar.py
```

```
[1] Start Searching
[2] Exit
```

Selecting **[1]** scans your current `/24` subnet, resolves device names/vendors, and prints a results table.

---

## 🛠️ How It Works

1. **Detects your local IP** via a UDP socket trick (no packets actually sent)
2. **Builds the target list** for the full `/24` subnet around your IP
3. **Ping-sweeps** all hosts concurrently with a thread pool
4. **Reads the ARP cache** (`/proc/net/arp`) to map IPs → MAC addresses
5. **Resolves names** using reverse DNS, falling back to a raw NetBIOS NBSTAT query
6. **Looks up vendors** from a local MAC OUI prefix table
7. **Renders everything** into a color-coded table

---

## 📊 Star History

<div align="center">

<a href="https://star-history.com/#Q-society/Q-radar&Date">
  <img src="https://api.star-history.com/svg?repos=Q-society/Q-radar&type=Date" alt="Star History Chart" width="700">
</a>

</div>

---

## 🤝 Contributing

Pull requests are welcome! If you've got an idea for a feature, found a bug, or want to improve detection accuracy:

1. Fork the repo
2. Create a branch (`git checkout -b feature/your-idea`)
3. Commit your changes
4. Open a pull request

<p align="center">
  <a href="https://github.com/Q-society/Q-radar/fork">
    <img src="https://img.shields.io/badge/🍴-Fork%20%26%20Contribute-4ec9b0?style=for-the-badge" alt="Fork & Contribute">
  </a>
  <a href="https://github.com/Q-society/Q-radar/pulls">
    <img src="https://img.shields.io/badge/🔧-Open%20a%20Pull%20Request-1f6feb?style=for-the-badge" alt="Open a PR">
  </a>
</p>

---

## ⚠️ Disclaimer

This tool is intended for scanning networks **you own or have explicit permission to test**. Unauthorized scanning of networks you do not control may violate local laws or terms of service. Use responsibly.

---

<div align="center">

### 💎 Made by [Q-society](https://github.com/Q-society)

Made with 🐍 and way too much terminal coffee ☕

<p align="center">
  <a href="https://github.com/Q-society/Q-radar/stargazers">
    <img src="https://img.shields.io/badge/⭐_If_this_saved_you_time,_drop_a_star-ffd700?style=for-the-badge&logoColor=black" alt="Star this repo">
  </a>
</p>

<sub>© 2026 Q-society — Built for sysadmins, pentesters, and the terminally curious.</sub>

</div>
