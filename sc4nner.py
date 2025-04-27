import requests
import threading
import queue
import os
import ssl
import socket
import time
import random
import json
import pyfiglet
from colorama import Fore, Style, init
from tqdm import tqdm
from fake_useragent import UserAgent

# Init
init(autoreset=True)

# Load Config
def load_config():
    default_config = {
        "threads": 30,
        "timeout": 5,
        "stealth_mode": False,
        "delay_min": 1,
        "delay_max": 3,
        "user_agents_rotate": True,
        "save_report": True
    }
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            print(Fore.RED + "[!] Gagal load config.json, pakai setting default.")
            return default_config
    else:
        return default_config

config = load_config()
ua = UserAgent()

# Utils
def random_ua():
    return ua.random if config["user_agents_rotate"] else "Mozilla/5.0 (Scanner)"

def stealth_delay():
    if config["stealth_mode"]:
        time.sleep(random.uniform(config["delay_min"], config["delay_max"]))

def save_result(filename, content):
    os.makedirs('hasil', exist_ok=True)
    with open(f"hasil/{filename}", "a", encoding="utf-8") as f:
        f.write(content + "\n")

def loading_animation(text="Loading"):
    for c in text + "...":
        print(Fore.YELLOW + c, end='', flush=True)
        time.sleep(0.05)
    print()

# Core Functions
def scan_subdomain(target, wordlist):
    loading_animation("Scanning Subdomains")
    q = queue.Queue()

    for sub in wordlist:
        q.put(sub.strip())

    def worker():
        while not q.empty():
            sub = q.get()
            url = f"http://{sub}.{target}"
            headers = {"User-Agent": random_ua()}
            try:
                r = requests.get(url, headers=headers, timeout=config["timeout"])
                if r.status_code in [200, 301, 302]:
                    print(Fore.GREEN + f"[FOUND] {url} ({r.status_code})")
                    save_result(f"subdomain_{target}.txt", url)
            except:
                pass
            stealth_delay()
            q.task_done()

    threads = []
    for _ in range(config["threads"]):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def scan_directory(target, wordlist):
    loading_animation("Scanning Directories")
    if not target.startswith("http"):
        target = "http://" + target

    q = queue.Queue()

    for path in wordlist:
        q.put(path.strip())

    def worker():
        while not q.empty():
            path = q.get()
            url = target.rstrip("/") + "/" + path
            headers = {"User-Agent": random_ua()}
            try:
                r = requests.get(url, headers=headers, timeout=config["timeout"])
                if r.status_code == 200:
                    print(Fore.GREEN + f"[FOUND] {url} ({r.status_code})")
                    save_result(f"directory_{target.replace('http://', '').replace('https://', '')}.txt", url)
                elif r.status_code in [301, 302]:
                    print(Fore.CYAN + f"[REDIRECT] {url} ({r.status_code})")
            except:
                pass
            stealth_delay()
            q.task_done()

    threads = []
    for _ in range(config["threads"]):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def detect_cms(target):
    loading_animation("Detecting CMS")
    cms_patterns = {
        "WordPress": ["wp-content", "wp-includes"],
        "Joomla": ["administrator", "components", "modules"],
        "Drupal": ["sites/all", "modules/system"],
        "Magento": ["static/frontend", "mage"],
        "Prestashop": ["modules", "themes"]
    }

    if not target.startswith("http"):
        target = "http://" + target

    found = False
    try:
        headers = {"User-Agent": random_ua()}
        r = requests.get(target, headers=headers, timeout=config["timeout"])
        html = r.text.lower()

        for cms, indicators in cms_patterns.items():
            for indicator in indicators:
                if indicator in html:
                    print(Fore.GREEN + f"[CMS DETECTED] {target} => {cms}")
                    save_result("cms_detected.txt", f"{target} => {cms}")
                    found = True
                    return

        if not found:
            print(Fore.RED + f"[CMS NOT DETECTED] {target}")

    except:
        print(Fore.MAGENTA + "[!] Tidak bisa mengakses target.")

def detect_waf(target):
    loading_animation("Detecting WAF")
    try:
        headers = {"User-Agent": random_ua()}
        r = requests.get("http://" + target, headers=headers, timeout=config["timeout"])
        server = r.headers.get("Server", "")
        if "cloudflare" in server.lower():
            print(Fore.YELLOW + f"[WAF DETECTED] {target} menggunakan Cloudflare")
        elif "sucuri" in server.lower():
            print(Fore.YELLOW + f"[WAF DETECTED] {target} menggunakan Sucuri")
        elif "ddos-guard" in server.lower():
            print(Fore.YELLOW + f"[WAF DETECTED] {target} menggunakan DDoS-Guard")
        else:
            print(Fore.GREEN + "[NO WAF DETECTED]")
    except:
        print(Fore.MAGENTA + "[!] Tidak bisa mendeteksi WAF.")

def check_ssl(target):
    loading_animation("Checking SSL")
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=target) as s:
            s.settimeout(5)
            s.connect((target, 443))
            cert = s.getpeercert()
            expires = cert['notAfter']
            print(Fore.GREEN + f"[SSL INFO] {target} SSL Expire: {expires}")
    except Exception as e:
        print(Fore.RED + f"[SSL CHECK FAILED] {target} ({e})")

# Update Checker
def update_script():
    loading_animation("Checking for Updates")
    try:
        github_raw_url = "https://raw.githubusercontent.com/karranwang/sc4nner/main/sc4nner.py"
        r = requests.get(github_raw_url, timeout=10)
        if r.status_code == 200:
            with open(__file__, "w", encoding="utf-8") as f:
                f.write(r.text)
            print(Fore.LIGHTGREEN_EX + "[+] Update berhasil! Silakan jalankan ulang script.")
            exit()
        else:
            print(Fore.RED + "[!] Gagal mengambil update dari GitHub.")
    except Exception as e:
        print(Fore.RED + f"[!] Error saat update: {e}")

# Wordlist Loader
def load_wordlist(file_path):
    if not os.path.exists(file_path):
        print(Fore.RED + f"[ERROR] Wordlist '{file_path}' tidak ditemukan.")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# Main Menu
def main():
    banner = pyfiglet.figlet_format("Sc4nner")
    print(Fore.CYAN + banner)
    print(Fore.LIGHTWHITE_EX + "      Github: @karranwang\n")

    while True:
        print(Fore.LIGHTYELLOW_EX + "\n=== MENU ===")
        print("[1] Scan Subdomain")
        print("[2] Scan Directory")
        print("[3] Detect CMS")
        print("[4] Detect WAF")
        print("[5] SSL Checker")
        print("[6] Mass Scan (Multi Target)")
        print("[7] Update Script")
        print("[8] Exit")

        choice = input(Fore.CYAN + "\nPilih menu: ").strip()

        if choice == "1":
            target = input("Masukkan domain target (tanpa http): ").strip()
            subdomains = load_wordlist("common_subdomains.txt")
            if subdomains:
                scan_subdomain(target, subdomains)

        elif choice == "2":
            target = input("Masukkan URL target (example.com): ").strip()
            dirs = load_wordlist("common_dirs.txt")
            if dirs:
                scan_directory(target, dirs)

        elif choice == "3":
            target = input("Masukkan URL target (example.com): ").strip()
            detect_cms(target)

        elif choice == "4":
            target = input("Masukkan domain target (example.com): ").strip()
            detect_waf(target)

        elif choice == "5":
            target = input("Masukkan domain target (example.com): ").strip()
            check_ssl(target)

        elif choice == "6":
            targets = load_wordlist("targets.txt")
            if not targets:
                print(Fore.RED + "[!] Tidak ada target!")
                continue
            for target in tqdm(targets, desc="Mass Scanning", unit="target"):
                detect_cms(target)
                detect_waf(target)
                check_ssl(target)
                print("-" * 50)

        elif choice == "7":
            update_script()

        elif choice == "8":
            print(Fore.LIGHTGREEN_EX + "\nTerima kasih telah menggunakan tools ini!")
            break

        else:
            print(Fore.RED + "[!] Pilihan tidak valid!")

if __name__ == "__main__":
    main()
