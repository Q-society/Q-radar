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

[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Termux-1f6feb?style=for-the-badge&logo=linux&logoColor=white)](#-installation)
[![Python](https://img.shields.io/badge/python-3.7%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](#-requirements)
[![License](https://img.shields.io/badge/license-MIT-success?style=for-the-badge)](#-license)
[![Root](https://img.shields.io/badge/root-not%20required-orange?style=for-the-badge)](#-installation)
[![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen?style=for-the-badge)](#-installation)

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
cd q-radar
chmod +x q-radar.py
python3 q-radar.py
```

### 📱 Termux (Android — no root required)

```bash
pkg update && pkg upgrade -y
pkg install -y python git
git clone https://github.com/Q-society/Q-radar.git
cd q-radar
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

## ⚠️ Disclaimer

This tool is intended for scanning networks **you own or have explicit permission to test**. Unauthorized scanning of networks you do not control may violate local laws or terms of service. Use responsibly.

---

## 📄 License

Released under the [MIT License](LICENSE) — free to use, modify, and distribute.

---

<div align="center">

Made with 🐍 and way too much terminal coffee ☕

⭐ If this saved you time, consider starring the repo!

</div>
