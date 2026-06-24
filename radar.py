#!/usr/bin/env python3
import os
import sys
import socket
from colorama import Fore, Style, init

# Colorama-nı rənglər üçün aktivləşdiririk
init(autoreset=True)

# Pro 3D ASCII Art və Qarşılama Ekranı
def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""
{Fore.CYAN}  ________          _______                _                 
{Fore.CYAN} |_   __  |        |_   __ \              | |                
{Fore.BLUE}   | |_ \_| ______   | |__) |   ,--.   ---| |   ,--.   _ .--.  
{Fore.BLUE}   |  _|  _|_   __|  |  __ /   `'_\ : / .`` |  `'_\ : [ `/'`\] 
{Fore.MAGENTA}  _| |_//_ | |       | |  \ \_ // | |,| \_( | // | |, | |     
{Fore.MAGENTA} |________||_|      |_|   [___]\'-;__/'\___.' \'-;__/[___]    
                                                              
        {Fore.YELLOW}>> Network Scanner for Kali & Termux <<
        {Fore.GREEN}Created for GitHub | Authorized Personnel Only
    """
    print(banner)

# Şəbəkə tapan və cihazları siyahılayan funksiya
def start_searching():
    # Gecikməli idxal (Scapy işə düşəndə lazımsız xəbərdarlıqları gizlətmək üçün)
    try:
        import logging
        logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
        from scapy.all import ARP, Ether, srp
    except ImportError:
        print(f"\n{Fore.RED}[!] Səhv: 'scapy' kitabxanası tapılmadı. Zəhmət olmasa pip install scapy yazın.")
        return

    print(f"\n{Fore.YELLOW}[*] Yerli şəbəkə məlumatları analiz edilir...")
    
    # Avtomatik olaraq local IP və Subnet-i təyin etmək
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        # Məsələn: 192.168.1.5 -> IP diapazonunu 192.168.1.0/24 edirik
        ip_range = ".".join(local_ip.split(".")[:-1]) + ".0/24"
    except Exception:
        print(f"{Fore.RED}[!] Local IP təyin edilə bilmədi. Standart olaraq 192.168.1.0/24 yoxlanılır.")
        ip_range = "192.168.1.0/24"

    print(f"{Fore.GREEN}[+] Hədəf Şəbəkə: {ip_range}")
    print(f"{Fore.CYAN}[*] Skan başlayır, bir az vaxt ala bilər...\n")

    # ARP Paketinin hazırlanması
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp = ARP(pdst=ip_range)
    probe = ether / arp

    # Paketlərin göndərilməsi və cavabların alınması (Real-time scan)
    try:
        result = srp(probe, timeout=3, verbose=False)[0]
    except PermissionError:
        print(f"{Fore.RED}[!] Səhv: Bu skan üçün administrator (ROOT/SUDO) icazəsi lazımdır!")
        input(f"\n{Fore.YELLOW}Davam etmək üçün Enter sıxın...")
        return

    # Nəticələrin ekrana çıxarılması
    print(f"{Fore.BLUE}" + "="*50)
    print(f"{Fore.GREEN}{'IP Ünvanı':<20}{'MAC Ünvanı':<20}")
    print(f"{Fore.BLUE}" + "="*50)

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
        print(f"{Fore.WHITE}{received.psrc:<20}{Fore.LIGHTBLACK_EX}{received.hwsrc:<20}")

    print(f"{Fore.BLUE}" + "="*50)
    print(f"{Fore.GREEN}[+] Skan bitdi. Toplam tapılan cihaz sayı: {len(devices)}")
    input(f"\n{Fore.YELLOW}Əsas menyuya qayıtmaq üçün Enter sıxın...")

# Əsas Menyu Məntiqi
def main():
    while True:
        show_banner()
        print(f"{Fore.WHITE}[1] Start Searching")
        print(f"{Fore.WHITE}[2] Exit")
        
        choice = input(f"\n{Fore.CYAN}Q-Radar > {Style.RESET_ALL}").strip()
        
        if choice == '1':
            start_searching()
        elif choice == '2':
            print(f"\n{Fore.RED}[*] Q-Radar bağlanır. Çıxış edildi.")
            sys.exit()
        else:
            print(f"\n{Fore.RED}[!] Səhv seçim! Zəhmət olmasa 1 və ya 2 daxil edin.")
            import time
            time.sleep(1.5)

if __name__ == "__main__":
    main()
