#!/usr/bin/env python3
"""
Q-RADAR — Local Network Device Scanner
========================================
Discovers real devices connected to your current Wi-Fi/LAN by combining
a multi-threaded ping sweep with the kernel's ARP/neighbor table.

Works on:
  - Kali Linux (and any standard Linux distro)
  - Termux (Android) — no root required

Author: you :)  License: MIT
Only scan networks you own or have permission to scan.
"""

import os
import sys
import socket
import struct
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# --------------------------------------------------------------------------
# Colors
# --------------------------------------------------------------------------
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[1;36m"
    BLUE = "\033[2;34m"
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[1;31m"
    GRAY = "\033[2;37m"
    MAGENTA = "\033[1;35m"


def supports_color():
    return sys.stdout.isatty()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# --------------------------------------------------------------------------
# 3D ASCII banner (block font + offset drop-shadow for a "3D" look)
# --------------------------------------------------------------------------
_FONT = {
    "Q": [".XXX.", "X...X", "X...X", "X...X", "X.X.X", "X..X.", ".XXXX"],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "-": [".....", ".....", ".....", "XXXXX", ".....", ".....", "....."],
}
_FONT_ROWS = 7


def _build_text_grid(word):
    letters = [_FONT[ch] for ch in word]
    w = sum(len(l[0]) for l in letters) + (len(letters) - 1)
    grid = [[0] * w for _ in range(_FONT_ROWS)]
    col = 0
    for glyph in letters:
        for r in range(_FONT_ROWS):
            for i, ch in enumerate(glyph[r]):
                grid[r][col + i] = 1 if ch == "X" else 0
        col += len(glyph[0]) + 1
    return grid, _FONT_ROWS, w


def big_banner():
    """Builds a clean 3D-look banner using an edge-following bevel shadow
    (shadow only traces the bottom/right edge of each stroke) instead of a
    diffuse duplicate offset — this keeps every letter sharp and readable
    even without color (e.g. piped output, low-color terminals)."""
    grid, h, w = _build_text_grid("Q-RADAR")
    H, W = h + 1, w + 1
    main = [[0] * W for _ in range(H)]
    shadow = [[0] * W for _ in range(H)]
    for r in range(h):
        for c in range(w):
            if grid[r][c]:
                main[r][c] = 1
    for r in range(h):
        for c in range(w):
            if grid[r][c]:
                if c + 1 >= w or not grid[r][c + 1]:
                    shadow[r][c + 1] = 1
                if r + 1 >= h or not grid[r + 1][c]:
                    shadow[r + 1][c] = 1
    lines = []
    for r in range(H):
        out = []
        for c in range(W):
            if main[r][c]:
                out.append(f"{C.CYAN}█{C.RESET}")
            elif shadow[r][c]:
                out.append(f"{C.BLUE}▒{C.RESET}")
            else:
                out.append(" ")
        lines.append("".join(out))
    return lines, W


def small_banner():
    line = f"{C.CYAN}{C.BOLD} Q-RADAR {C.RESET}"
    border = "─" * 10
    return [f"{C.BLUE}┌{border}┐{C.RESET}",
            f"{C.BLUE}│{C.RESET}{line}{C.BLUE}│{C.RESET}",
            f"{C.BLUE}└{border}┘{C.RESET}"]


def print_banner():
    term_w = shutil.get_terminal_size(fallback=(80, 24)).columns
    lines, needed_w = big_banner()
    if term_w >= needed_w + 2:
        for l in lines:
            print(l)
        sub = "L O C A L   N E T W O R K   D E V I C E   S C A N N E R"
        print(f"{C.GRAY}{sub.center(needed_w)}{C.RESET}")
    else:
        for l in small_banner():
            print(l)
        print(f"{C.GRAY}Network Device Scanner{C.RESET}")
    print(f"{C.BLUE}{'═' * min(term_w - 1, max(needed_w, 30))}{C.RESET}")


# --------------------------------------------------------------------------
# Networking helpers
# --------------------------------------------------------------------------
def get_local_ip():
    """Get the local IP address used to reach the internet/router, without
    actually sending traffic anywhere (UDP socket trick)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def ip_to_int(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]


def int_to_ip(n):
    return socket.inet_ntoa(struct.pack("!I", n))


def hosts_in_subnet(local_ip, prefix=24):
    """Return list of host IPs in the /prefix network containing local_ip."""
    ip_int = ip_to_int(local_ip)
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    network = ip_int & mask
    broadcast = network | (~mask & 0xFFFFFFFF)
    return [int_to_ip(i) for i in range(network + 1, broadcast)]


def ping(ip, timeout=1.0):
    """Returns True if host responds to a single ICMP echo."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 0.5,
        )
        return result.returncode == 0
    except Exception:
        return False


def read_arp_table():
    """Read the kernel ARP/neighbor cache. Works on Linux and Termux
    (Android kernel) via /proc/net/arp. Returns {ip: mac}."""
    table = {}
    try:
        with open("/proc/net/arp") as f:
            lines = f.readlines()[1:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                ip, mac = parts[0], parts[3]
                if mac != "00:00:00:00:00:00":
                    table[ip] = mac
    except Exception:
        pass
    return table


def get_hostname(ip, timeout=0.8):
    socket.setdefaulttimeout(timeout)
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None
    finally:
        socket.setdefaulttimeout(None)


def get_netbios_name(ip, timeout=0.6):
    """Sends a standard NBSTAT (NetBIOS Node Status) query directly to the
    device on UDP/137 and parses the device's own advertised name out of
    the reply. Works for Windows machines, many NAS boxes, and printers
    that speak NetBIOS — a real on-the-wire query, not a guess.
    Returns None if the device doesn't answer (e.g. most phones/IoT)."""
    transaction_id = b"\x82\x28"
    flags = b"\x00\x00"
    qdcount = b"\x00\x01"
    counts = b"\x00\x00\x00\x00\x00\x00"
    # Fixed, standard wildcard NBSTAT query name ("*" + 15 null bytes,
    # NetBIOS first-level-encoded) — identical to what `nbtscan`/`nmblookup` send.
    encoded_wildcard = b"CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    name_field = bytes([0x20]) + encoded_wildcard + b"\x00"
    qtype = b"\x00\x21"   # NBSTAT
    qclass = b"\x00\x01"  # IN
    packet = transaction_id + flags + qdcount + counts + name_field + qtype + qclass

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(packet, (ip, 137))
        data, _ = sock.recvfrom(2048)
    except Exception:
        return None
    finally:
        sock.close()

    try:
        offset = 12
        if data[offset] & 0xC0 == 0xC0:
            offset += 2
        else:
            name_len = data[offset]
            offset += 1 + name_len + 1
        offset += 2 + 2 + 4  # type + class + ttl
        rdlength = struct.unpack("!H", data[offset:offset + 2])[0]
        offset += 2
        rdata = data[offset:offset + rdlength]
        num_names = rdata[0]
        pos = 1
        for _ in range(num_names):
            raw_name = rdata[pos:pos + 15]
            suffix = rdata[pos + 15]
            pos += 18
            name = raw_name.decode("ascii", errors="ignore").strip()
            # suffix 0x00 = the device's own "workstation" name (its host name)
            if name and suffix == 0x00:
                return name
        return None
    except Exception:
        return None


def get_device_name(ip):
    """Best-effort real device name: tries reverse DNS first, then NetBIOS.
    Returns a clean string, or '-' if nothing answered (honest, not faked)."""
    name = get_hostname(ip)
    if name:
        return name.split(".")[0]
    nb = get_netbios_name(ip)
    if nb:
        return nb
    return "-"


# Small offline OUI prefix table — common vendors only (best-effort, optional)
_OUI = {
    "00:1A:11": "Google", "F4:F5:D8": "Google", "DC:A6:32": "Raspberry Pi",
    "B8:27:EB": "Raspberry Pi", "00:50:56": "VMware", "00:0C:29": "VMware",
    "3C:5A:B4": "Apple", "A4:5E:60": "Apple", "AC:DE:48": "Apple",
    "00:1D:D8": "Apple", "F0:18:98": "Apple", "DC:2B:2A": "Samsung",
    "8C:79:67": "Samsung", "5C:0A:5B": "Samsung", "E8:50:8B": "Xiaomi",
    "F8:A4:5F": "Xiaomi", "64:09:80": "Huawei", "00:E0:FC": "Huawei",
    "00:14:78": "TP-Link", "50:C7:BF": "TP-Link", "AC:84:C6": "TP-Link",
    "00:26:F2": "D-Link", "00:1F:33": "D-Link",
}


def vendor_lookup(mac):
    prefix = mac.upper()[0:8]
    return _OUI.get(prefix, "Unknown")


# --------------------------------------------------------------------------
# Scan
# --------------------------------------------------------------------------
def scan_network():
    local_ip = get_local_ip()
    targets = hosts_in_subnet(local_ip, prefix=24)
    network_str = ".".join(local_ip.split(".")[:3]) + ".0/24"

    print(f"\n{C.YELLOW}[*] Local IP:{C.RESET} {local_ip}")
    print(f"{C.YELLOW}[*] Scanning network:{C.RESET} {network_str}")
    print(f"{C.YELLOW}[*] Targets:{C.RESET} {len(targets)} hosts\n")

    alive = []
    done_count = [0]
    lock = threading.Lock()
    total = len(targets)

    def worker(ip):
        is_up = ping(ip)
        with lock:
            done_count[0] += 1
            pct = int(done_count[0] / total * 100)
            bar_len = 30
            filled = int(bar_len * pct / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            sys.stdout.write(
                f"\r{C.CYAN}[{bar}] {pct:3d}%{C.RESET} "
                f"({done_count[0]}/{total})"
            )
            sys.stdout.flush()
        if is_up:
            alive.append(ip)

    start = time.time()
    with ThreadPoolExecutor(max_workers=80) as pool:
        futures = [pool.submit(worker, ip) for ip in targets]
        for _ in as_completed(futures):
            pass
    elapsed = time.time() - start

    print(f"\n\n{C.GREEN}[+] Scan finished in {elapsed:.1f}s — "
          f"{len(alive)} device(s) responded.{C.RESET}\n")

    if not alive:
        print(f"{C.RED}[!] No devices found. Some networks block ICMP, "
              f"or you may need to run with elevated privileges.{C.RESET}")
        return

    arp = read_arp_table()
    alive.sort(key=ip_to_int)

    print(f"{C.YELLOW}[*] Resolving device names & MAC addresses...{C.RESET}\n")

    names = {}
    with ThreadPoolExecutor(max_workers=40) as pool:
        future_to_ip = {pool.submit(get_device_name, ip): ip for ip in alive}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                names[ip] = future.result()
            except Exception:
                names[ip] = "-"

    rows = []
    for ip in alive:
        mac = arp.get(ip, "Unknown")
        vendor = vendor_lookup(mac) if mac != "Unknown" else "Unknown"
        device_name = names.get(ip, "-")
        is_self = " (you)" if ip == local_ip else ""
        rows.append((ip + is_self, mac, vendor, device_name))

    print_table(rows)


def print_table(rows):
    headers = ["IP ADDRESS", "MAC ADDRESS", "VENDOR", "DEVICE NAME"]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))
    widths = [w + 2 for w in widths]

    def hline(char_l, char_m, char_r):
        return char_l + char_m.join("─" * w for w in widths) + char_r

    def fmt_row(vals, color=""):
        cells = []
        for v, w in zip(vals, widths):
            cells.append(f" {v}".ljust(w))
        return f"{color}│" + "│".join(cells) + f"│{C.RESET}"

    print(f"{C.BLUE}{hline('┌', '┬', '┐')}{C.RESET}")
    print(fmt_row(headers, color=C.BOLD + C.CYAN))
    print(f"{C.BLUE}{hline('├', '┼', '┤')}{C.RESET}")
    for row in rows:
        print(fmt_row(row, color=C.GREEN))
    print(f"{C.BLUE}{hline('└', '┴', '┘')}{C.RESET}")


# --------------------------------------------------------------------------
# Menu
# --------------------------------------------------------------------------
def main_menu():
    while True:
        clear_screen()
        print_banner()
        print(f"\n {C.BOLD}[1]{C.RESET} Start Searching")
        print(f" {C.BOLD}[2]{C.RESET} Exit\n")
        choice = input(f"{C.MAGENTA} q-radar> {C.RESET}").strip()

        if choice == "1":
            scan_network()
            input(f"\n{C.GRAY}Press ENTER to return to the menu...{C.RESET}")
        elif choice == "2":
            print(f"\n{C.CYAN}Goodbye.{C.RESET}\n")
            sys.exit(0)
        else:
            print(f"{C.RED}Invalid choice.{C.RESET}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{C.CYAN}Interrupted. Goodbye.{C.RESET}")
        sys.exit(0)
