# Sc4nner

Sc4nner adalah tools pentest ringan berbasis Python untuk melakukan:

1. Scan subdomain

2. Scan directory

3. Detect CMS

4. Detect WAF

5. Cek SSL certificate

6. Mass Scan multi target


Dirancang untuk cepat, mudah digunakan, dan stealthy jika diperlukan.


---

## Features

### Subdomain enumeration

### Directory brute force

### CMS detection (WordPress, Joomla, Drupal, Magento, PrestaShop)

### WAF detection (Cloudflare, Sucuri, DDoS-Guard)

### SSL certificate expiration check

### Mass scan multiple target

### Support stealth mode (random delay, random user-agent)

### Auto save hasil ke folder /hasil/



---

## Installation

1. Clone repository:


git clone https://github.com/karranwang/sc4nner.git

cd sc4nner


2. Install dependencies:

pip install -r requirements.txt


---

## Usage

Jalankan tools:

python sc4nner.py

Ikuti menu interaktif yang tersedia.


---

## Configuration

File config.json untuk pengaturan:

{
  "threads": 30,
  "timeout": 5,
  "stealth_mode": false,
  "delay_min": 1,
  "delay_max": 3,
  "user_agents_rotate": true,
  "save_report": true
}

stealth_mode: Jika true, akan delay acak antar request untuk menghindari block.

user_agents_rotate: Randomize User-Agent header untuk tiap request.



---

Screenshot

Tampilan utama:

<p align="center">
  <img src="img.jpg" alt="Sc4nner Screenshot" width="700"/>
</p>
---

Project Structure

sc4nner/

├── hasil/                  # Folder hasil scan

├── wordlists/              # Wordlists default

│   ├── common_subdomains.txt

│   └── common_dirs.txt

├── img.jpg                 # Screenshot untuk README

├── sc4nner.py              # Source code utama

├── config.json             # Config file

├── requirements.txt        # Python dependencies

└── README.md               # Dokumentasi


---

Credits

Dibuat oleh @karranwangreal

Open Source Project — feel free to contribute!



---

License

This project is licensed under the MIT License - see the LICENSE file for details.
