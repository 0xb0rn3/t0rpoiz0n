#!/usr/bin/env python3
"""
t0rpoiz0n - Advanced Tor Transparent Proxy + MAC Spoofing Tool
Author: 0xb0rn3 | oxbv1
Version: 1.1.3 - Fixed nftables compatibility
Built for Arch Linux
"""

import os
import sys
import time
import subprocess
import random
import json
import argparse
from pathlib import Path
from typing import Optional

# Color codes
class Color:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Configuration paths
DATA_DIR = Path("/usr/share/t0rpoiz0n")
BACKUP_DIR = Path("/var/lib/t0rpoiz0n/backups")
CONFIG_FILE = Path("/etc/t0rpoiz0n/config.json")

# MAC vendor prefixes for spoofing
MAC_VENDORS = {
    'samsung': '94:51:03',
    'apple': '00:03:93',
    'huawei': '00:18:82',
    'nokia': '00:19:2D',
    'google': '00:1A:11',
    'dell': '00:06:5B',
    'hp': '00:0B:CD',
    'asus': '9C:5C:8E',
    'lenovo': '00:21:5C',
    'motorola': '00:0A:28'
}

def banner():
    """Display tool banner"""
    banner_text = r"""
   /$$      /$$$$$$                                /$$            /$$$$$$           
  | $$     /$$$_  $$                              |__/           /$$$_  $$          
 /$$$$$$  | $$$$\ $$  /$$$$$$   /$$$$$$   /$$$$$$  /$$ /$$$$$$$$| $$$$\ $$ /$$$$$$$ 
|_  $$_/  | $$ $$ $$ /$$__  $$ /$$__  $$ /$$__  $$| $$|____ /$$/| $$ $$ $$| $$__  $$
  | $$    | $$\ $$$$| $$  \__/| $$  \ $$| $$  \ $$| $$   /$$$$/ | $$\ $$$$| $$  \ $$
  | $$ /$$| $$ \ $$$| $$      | $$  | $$| $$  | $$| $$  /$$__/  | $$ \ $$$| $$  | $$
  |  $$$$/|  $$$$$$/| $$      | $$$$$$$/|  $$$$$$/| $$ /$$$$$$$$|  $$$$$$/| $$  | $$
   \___/   \______/ |__/      | $$____/  \______/ |__/|________/ \______/ |__/  |__/
                              | $$                                                  
                              | $$                                                  
                              |__/                                                  

            TOR PROXY & MAC SPOOFING FRAMEWORK
                 Engineered by: oxbv1
                    Version: 1.1.3
"""
    print(f"{Color.CYAN}{Color.BOLD}{banner_text}{Color.RESET}")

def check_root():
    """Ensure script is run as root"""
    if os.geteuid() != 0:
        print(f"{Color.RED}[✗] This tool must be run as root{Color.RESET}")
        sys.exit(1)

def run_cmd(cmd: str, shell: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """Execute shell command with error handling"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print(f"{Color.RED}[✗] Command failed: {cmd}{Color.RESET}")
            print(f"{Color.RED}    Error: {e.stderr}{Color.RESET}")
        raise

# Global variables for iptables backend
IPTABLES_CMD = "iptables"
IPTABLES_RESTORE_CMD = "iptables-restore"
IPTABLES_SAVE_CMD = "iptables-save"
USING_NFT_BACKEND = False

def detect_iptables_backend():
    """Detect and set the correct iptables backend (legacy vs nft)"""
    global IPTABLES_CMD, IPTABLES_RESTORE_CMD, IPTABLES_SAVE_CMD, USING_NFT_BACKEND
    
    print(f"{Color.CYAN}[*] Detecting iptables backend...{Color.RESET}")
    
    # Try iptables-nft first (modern Arch default)
    test_nft = run_cmd("iptables-nft -L -n 2>/dev/null", check=False)
    if test_nft.returncode == 0:
        IPTABLES_CMD = "iptables-nft"
        IPTABLES_RESTORE_CMD = "iptables-nft-restore"
        IPTABLES_SAVE_CMD = "iptables-nft-save"
        USING_NFT_BACKEND = True
        print(f"{Color.GREEN}[✓] Using iptables-nft (nftables backend){Color.RESET}")
        return True
    
    # Try legacy iptables
    test_legacy = run_cmd("iptables-legacy -L -n 2>/dev/null", check=False)
    if test_legacy.returncode == 0:
        IPTABLES_CMD = "iptables-legacy"
        IPTABLES_RESTORE_CMD = "iptables-legacy-restore"
        IPTABLES_SAVE_CMD = "iptables-legacy-save"
        USING_NFT_BACKEND = False
        print(f"{Color.GREEN}[✓] Using iptables-legacy (legacy backend){Color.RESET}")
        return True
    
    # Try generic iptables
    test_generic = run_cmd("iptables -L -n 2>/dev/null", check=False)
    if test_generic.returncode == 0:
        USING_NFT_BACKEND = False
        print(f"{Color.GREEN}[✓] Using iptables (generic){Color.RESET}")
        return True
    
    print(f"{Color.YELLOW}[!] Could not detect working iptables backend{Color.RESET}")
    IPTABLES_CMD = "iptables-nft"
    IPTABLES_RESTORE_CMD = "iptables-nft-restore"
    IPTABLES_SAVE_CMD = "iptables-nft-save"
    USING_NFT_BACKEND = True
    return False

def check_dependencies() -> bool:
    """Check if required packages are installed"""
    required = ['tor', 'iptables', 'macchanger']
    missing = []
    
    for pkg in required:
        if run_cmd(f"which {pkg}", check=False).returncode != 0:
            missing.append(pkg)
    
    if missing:
        print(f"{Color.RED}[✗] Missing dependencies: {', '.join(missing)}{Color.RESET}")
        print(f"{Color.YELLOW}[*] Install with: sudo pacman -S {' '.join(missing)}{Color.RESET}")
        return False
    
    return True

def get_default_interface() -> Optional[str]:
    """Get default network interface"""
    result = run_cmd("ip route | grep default | awk '{print $5}'", check=False)
    
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    
    result = run_cmd("ip link show | grep -v 'lo:' | grep 'state UP' | awk '{print $2}' | tr -d ':' | head -1", check=False)
    
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    
    return None

def generate_random_mac(vendor: Optional[str] = None) -> str:
    """Generate random MAC address with optional vendor prefix"""
    if vendor and vendor.lower() in MAC_VENDORS:
        prefix = MAC_VENDORS[vendor.lower()]
        suffix = ':'.join(['%02x' % random.randint(0, 255) for _ in range(3)])
        return f"{prefix}:{suffix}"
    else:
        return ':'.join(['%02x' % random.randint(0, 255) for _ in range(6)])

def change_mac(interface: str, vendor: Optional[str] = None) -> bool:
    """Change MAC address of network interface"""
    print(f"{Color.CYAN}[*] Changing MAC address for {interface}...{Color.RESET}")
    
    run_cmd(f"ip link set {interface} down", check=False)
    new_mac = generate_random_mac(vendor)
    result = run_cmd(f"macchanger -m {new_mac} {interface}", check=False)
    run_cmd(f"ip link set {interface} up", check=False)
    
    if result.returncode == 0:
        print(f"{Color.GREEN}[✓] MAC changed to: {new_mac}{Color.RESET}")
        return True
    else:
        print(f"{Color.RED}[✗] Failed to change MAC address{Color.RESET}")
        return False

def create_iptables_rules_nft():
    """Create nftables-compatible iptables rules"""
    print(f"{Color.CYAN}[*] Creating nftables-compatible rules...{Color.RESET}")
    
    rules = """# t0rpoiz0n iptables rules (nftables backend compatible)
# Generated for transparent Tor proxy

*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]

# Redirect DNS to Tor DNSPort
-A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 53
-A OUTPUT -p tcp --dport 53 -j REDIRECT --to-ports 53

# Block DNS-over-TLS
-A OUTPUT -p tcp --dport 853 -j REJECT
-A OUTPUT -p udp --dport 853 -j REJECT

# Block QUIC/HTTP3
-A OUTPUT -p udp --dport 443 -j REJECT

# Don't redirect local traffic
-A OUTPUT -d 127.0.0.0/8 -j RETURN
-A OUTPUT -d 192.168.0.0/16 -j RETURN
-A OUTPUT -d 10.0.0.0/8 -j RETURN
-A OUTPUT -d 172.16.0.0/12 -j RETURN

# Redirect all other TCP traffic to Tor TransPort
-A OUTPUT -p tcp -j REDIRECT --to-ports 9040

COMMIT

*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]

# Allow loopback
-A INPUT -i lo -j ACCEPT
-A OUTPUT -o lo -j ACCEPT

# Allow established connections
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
-A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow DNS to localhost
-A OUTPUT -p udp --dport 53 -d 127.0.0.1 -j ACCEPT
-A OUTPUT -p tcp --dport 53 -d 127.0.0.1 -j ACCEPT

# Allow traffic to Tor ports
-A OUTPUT -p tcp --dport 9040 -j ACCEPT
-A OUTPUT -p tcp --dport 9050 -j ACCEPT

# Block remaining UDP (prevent leaks)
-A OUTPUT -p udp -j REJECT

COMMIT
"""
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rules_file = DATA_DIR / "iptables.rules"
    
    # Force write new rules
    with open(rules_file, 'w') as f:
        f.write(rules)
    
    print(f"{Color.GREEN}[✓] nftables-compatible rules written to {rules_file}{Color.RESET}")
    
    return rules_file

def create_iptables_rules_legacy():
    """Create legacy iptables rules with owner matching"""
    print(f"{Color.CYAN}[*] Creating legacy iptables rules...{Color.RESET}")
    
    rules = """# t0rpoiz0n iptables rules (legacy backend)
# Generated for transparent Tor proxy

*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]

# Redirect DNS to Tor DNSPort
-A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 53
-A OUTPUT -p tcp --dport 53 -j REDIRECT --to-ports 53

# Block DNS-over-TLS
-A OUTPUT -p tcp --dport 853 -j REJECT
-A OUTPUT -p udp --dport 853 -j REJECT

# Block QUIC/HTTP3
-A OUTPUT -p udp --dport 443 -j REJECT

# Don't redirect traffic from Tor itself
-A OUTPUT -m owner --uid-owner tor -j RETURN

# Don't redirect local traffic
-A OUTPUT -d 127.0.0.0/8 -j RETURN
-A OUTPUT -d 192.168.0.0/16 -j RETURN
-A OUTPUT -d 10.0.0.0/8 -j RETURN
-A OUTPUT -d 172.16.0.0/12 -j RETURN

# Redirect all other TCP traffic to Tor TransPort
-A OUTPUT -p tcp -j REDIRECT --to-ports 9040

COMMIT

*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]

# Block IPv6-ICMP
-A INPUT -p ipv6-icmp -j DROP
-A OUTPUT -p ipv6-icmp -j DROP
-A FORWARD -p ipv6-icmp -j DROP

# Allow loopback
-A INPUT -i lo -j ACCEPT
-A OUTPUT -o lo -j ACCEPT

# Allow established connections
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
-A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow Tor user
-A OUTPUT -m owner --uid-owner tor -j ACCEPT

# Allow DNS to localhost
-A OUTPUT -p udp --dport 53 -d 127.0.0.1 -j ACCEPT
-A OUTPUT -p tcp --dport 53 -d 127.0.0.1 -j ACCEPT

# Allow traffic to Tor ports
-A OUTPUT -p tcp --dport 9040 -j ACCEPT
-A OUTPUT -p tcp --dport 9050 -j ACCEPT

# Block remaining UDP
-A OUTPUT -p udp -j REJECT

COMMIT
"""
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rules_file = DATA_DIR / "iptables.rules"
    
    # Force write new rules
    with open(rules_file, 'w') as f:
        f.write(rules)
    
    print(f"{Color.GREEN}[✓] Legacy iptables rules written to {rules_file}{Color.RESET}")
    
    return rules_file

def create_iptables_rules():
    """Create appropriate iptables rules based on detected backend"""
    global USING_NFT_BACKEND
    
    if USING_NFT_BACKEND:
        print(f"{Color.YELLOW}[DEBUG] Backend is NFT, creating nft rules{Color.RESET}")
        return create_iptables_rules_nft()
    else:
        print(f"{Color.YELLOW}[DEBUG] Backend is LEGACY, creating legacy rules{Color.RESET}")
        return create_iptables_rules_legacy()

def create_torrc():
    """Create Tor configuration file"""
    torrc = """# t0rpoiz0n Tor configuration
# Auto-generated - Do not edit manually

# Ports
SocksPort 9050
TransPort 9040 IsolateClientAddr IsolateClientProtocol IsolateDestAddr IsolateDestPort
DNSPort 53

# Directories
DataDirectory /var/lib/tor
CacheDirectory /var/cache/tor

# Logging
Log notice syslog

# Security
AvoidDiskWrites 1
HardwareAccel 1

# Don't be a relay
ORPort 0
BandwidthRate 1 MB
BandwidthBurst 2 MB
"""
    
    torrc_path = Path("/etc/tor/torrc")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    if torrc_path.exists():
        run_cmd(f"cp {torrc_path} {BACKUP_DIR}/torrc.backup", check=False)
    
    torrc_path.write_text(torrc)
    os.chmod(torrc_path, 0o644)
    
    return torrc_path

def create_systemd_service():
    """Create systemd service file for Tor"""
    service = """[Unit]
Description=t0rpoiz0n - Tor Transparent Proxy Service
After=network.target
Documentation=https://github.com/0xb0rn3/t0rpoiz0n

[Service]
Type=simple
ExecStart=/usr/bin/tor -f /etc/tor/torrc
ExecReload=/bin/kill -HUP $MAINPID
KillSignal=SIGINT
TimeoutSec=60
Restart=on-failure
RestartSec=5

# Security capabilities
AmbientCapabilities=CAP_NET_BIND_SERVICE CAP_NET_ADMIN CAP_NET_RAW
NoNewPrivileges=yes

# Process management
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
"""
    
    service_path = Path("/etc/systemd/system/tor-t0rpoiz0n.service")
    service_path.write_text(service)
    os.chmod(service_path, 0o644)
    
    run_cmd("systemctl daemon-reload")
    run_cmd("setcap 'cap_net_bind_service=+ep' /usr/bin/tor")
    
    return service_path

def setup_directories():
    """Create necessary directories"""
    dirs = [DATA_DIR, BACKUP_DIR, Path("/etc/t0rpoiz0n")]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        os.chmod(d, 0o755)

def first_time_setup():
    """Perform first-time setup"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] Running First-Time Setup{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    print(f"{Color.CYAN}[*] Checking dependencies...{Color.RESET}")
    if not check_dependencies():
        return False
    print(f"{Color.GREEN}[✓] Dependencies OK{Color.RESET}")
    
    print(f"{Color.CYAN}[*] Creating directories...{Color.RESET}")
    setup_directories()
    print(f"{Color.GREEN}[✓] Directories created{Color.RESET}")
    
    # Detect backend BEFORE creating rules
    print(f"{Color.CYAN}[*] Detecting iptables backend...{Color.RESET}")
    detect_iptables_backend()
    
    # Create appropriate rules based on detected backend
    print(f"{Color.CYAN}[*] Creating iptables rules...{Color.RESET}")
    create_iptables_rules()
    print(f"{Color.GREEN}[✓] iptables rules created{Color.RESET}")
    
    print(f"{Color.CYAN}[*] Creating Tor configuration...{Color.RESET}")
    create_torrc()
    print(f"{Color.GREEN}[✓] Tor config created{Color.RESET}")
    
    print(f"{Color.CYAN}[*] Creating systemd service...{Color.RESET}")
    create_systemd_service()
    print(f"{Color.GREEN}[✓] Service created{Color.RESET}")
    
    print(f"\n{Color.GREEN}[✓] Setup complete!{Color.RESET}")
    return True

def apply_ipv6_blocks_nft():
    """Apply IPv6 blocks using nft directly for nftables backend"""
    print(f"{Color.CYAN}[*] Applying IPv6 blocks via nft...{Color.RESET}")
    
    # Check if table exists, create if not
    run_cmd("nft list table inet filter 2>/dev/null || nft add table inet filter", check=False)
    
    # Add chain if not exists
    run_cmd("nft add chain inet filter output { type filter hook output priority 0 \\; }", check=False)
    
    # Block IPv6
    run_cmd("nft add rule inet filter output meta l4proto ipv6-icmp drop", check=False)
    run_cmd("nft add rule inet filter output ip6 version 6 drop", check=False)
    
    print(f"{Color.GREEN}[✓] IPv6 blocked via nft{Color.RESET}")

def start_transparent_proxy():
    """Start Tor transparent proxy"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] Starting Transparent Proxy{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    # Detect backend FIRST before anything else
    detect_iptables_backend()
    
    # Stop existing Tor
    run_cmd("systemctl stop tor.service tor-t0rpoiz0n.service", check=False)
    run_cmd("killall tor", check=False)
    time.sleep(2)
    
    # Disable IPv6
    print(f"{Color.CYAN}[*] Disabling IPv6...{Color.RESET}")
    run_cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1 >/dev/null 2>&1")
    run_cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1 >/dev/null 2>&1")
    print(f"{Color.GREEN}[✓] IPv6 disabled{Color.RESET}")
    
    # Backup and set DNS
    if Path("/etc/resolv.conf").exists():
        run_cmd(f"cp /etc/resolv.conf {BACKUP_DIR}/resolv.conf.backup", check=False)
    
    Path("/etc/resolv.conf").write_text("nameserver 127.0.0.1\n")
    print(f"{Color.GREEN}[✓] DNS configured{Color.RESET}")
    
    # Start Tor
    print(f"{Color.CYAN}[*] Starting Tor service...{Color.RESET}")
    result = run_cmd("systemctl start tor-t0rpoiz0n.service", check=False)
    
    if result.returncode != 0:
        print(f"{Color.RED}[✗] Failed to start Tor service{Color.RESET}")
        run_cmd("journalctl -u tor-t0rpoiz0n.service -n 20 --no-pager")
        return False
    
    time.sleep(3)
    print(f"{Color.GREEN}[✓] Tor service started{Color.RESET}")
    
    # Apply iptables rules
    print(f"{Color.CYAN}[*] Applying iptables rules...{Color.RESET}")
    
    # Flush existing
    try:
        run_cmd(f"{IPTABLES_CMD} -F")
        run_cmd(f"{IPTABLES_CMD} -X")
        run_cmd(f"{IPTABLES_CMD} -t nat -F")
        run_cmd(f"{IPTABLES_CMD} -t nat -X")
    except:
        pass
    
    # Regenerate rules for current backend (THIS is the key fix!)
    print(f"{Color.CYAN}[*] Regenerating rules for {IPTABLES_CMD}...{Color.RESET}")
    rules_path = create_iptables_rules()
    
    # Debug: Verify file was written correctly
    if rules_path.exists():
        with open(rules_path, 'r') as f:
            first_line = f.readline().strip()
            print(f"{Color.YELLOW}[DEBUG] Rules file first line: {first_line}{Color.RESET}")
            if USING_NFT_BACKEND and "nftables backend compatible" not in first_line:
                print(f"{Color.RED}[ERROR] Rules file has wrong content for nft backend!{Color.RESET}")
            elif not USING_NFT_BACKEND and "legacy backend" not in first_line:
                print(f"{Color.RED}[ERROR] Rules file has wrong content for legacy backend!{Color.RESET}")
    else:
        print(f"{Color.RED}[ERROR] Rules file was not created!{Color.RESET}")
        return False
    
    print(f"{Color.GREEN}[✓] Rules generated and verified{Color.RESET}")
    
    # Apply rules
    try:
        run_cmd(f"{IPTABLES_RESTORE_CMD} < {rules_path}")
        print(f"{Color.GREEN}[✓] iptables rules applied using {IPTABLES_CMD}{Color.RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{Color.RED}[✗] Failed to apply iptables rules{Color.RESET}")
        print(f"{Color.YELLOW}[!] Backend: {IPTABLES_CMD}{Color.RESET}")
        print(f"{Color.YELLOW}[!] Dumping rules file for inspection:{Color.RESET}")
        run_cmd(f"cat {rules_path} | head -20", check=False)
        return False
    
    # Additional IPv6 blocking for nft
    if USING_NFT_BACKEND:
        apply_ipv6_blocks_nft()
    
    # Wait for bootstrap
    print(f"{Color.CYAN}[*] Waiting for Tor to bootstrap...{Color.RESET}")
    
    for i in range(30):
        result = run_cmd("systemctl is-active tor-t0rpoiz0n.service", check=False)
        if result.stdout.strip() == "active":
            time.sleep(2)
            break
        time.sleep(1)
    
    print(f"{Color.GREEN}[✓] Transparent proxy activated{Color.RESET}")
    
    # Browser warning
    print(f"\n{Color.YELLOW}{'='*60}{Color.RESET}")
    print(f"{Color.YELLOW}{Color.BOLD}[!] IMPORTANT: Browser Configuration{Color.RESET}")
    print(f"{Color.YELLOW}{'='*60}{Color.RESET}")
    print(f"{Color.GREEN}RECOMMENDED: Use Tor Browser{Color.RESET}")
    print(f"  Download: https://www.torproject.org/download/\n")
    print(f"{Color.YELLOW}OR configure Firefox:{Color.RESET}")
    print(f"  1. about:config → network.trr.mode = 5")
    print(f"  2. about:config → network.http.http3.enabled = false")
    print(f"  3. about:config → media.peerconnection.enabled = false")
    print(f"{Color.YELLOW}{'='*60}{Color.RESET}\n")
    
    return True

def stop_transparent_proxy():
    """Stop Tor transparent proxy and restore system"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] Stopping Transparent Proxy{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    detect_iptables_backend()
    
    print(f"{Color.CYAN}[*] Stopping Tor service...{Color.RESET}")
    run_cmd("systemctl stop tor-t0rpoiz0n.service", check=False)
    print(f"{Color.GREEN}[✓] Tor stopped{Color.RESET}")
    
    print(f"{Color.CYAN}[*] Flushing iptables rules...{Color.RESET}")
    try:
        run_cmd(f"{IPTABLES_CMD} -F")
        run_cmd(f"{IPTABLES_CMD} -X")
        run_cmd(f"{IPTABLES_CMD} -t nat -F")
        run_cmd(f"{IPTABLES_CMD} -t nat -X")
        run_cmd(f"{IPTABLES_CMD} -P INPUT ACCEPT")
        run_cmd(f"{IPTABLES_CMD} -P FORWARD ACCEPT")
        run_cmd(f"{IPTABLES_CMD} -P OUTPUT ACCEPT")
        print(f"{Color.GREEN}[✓] iptables flushed{Color.RESET}")
    except:
        print(f"{Color.YELLOW}[!] Could not flush iptables{Color.RESET}")
    
    # Clean nft rules if using nft
    if USING_NFT_BACKEND:
        run_cmd("nft delete table inet filter 2>/dev/null", check=False)
    
    print(f"{Color.CYAN}[*] Re-enabling IPv6...{Color.RESET}")
    run_cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=0 >/dev/null 2>&1")
    run_cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=0 >/dev/null 2>&1")
    print(f"{Color.GREEN}[✓] IPv6 re-enabled{Color.RESET}")
    
    backup_resolv = BACKUP_DIR / "resolv.conf.backup"
    if backup_resolv.exists():
        print(f"{Color.CYAN}[*] Restoring DNS...{Color.RESET}")
        run_cmd(f"cp {backup_resolv} /etc/resolv.conf", check=False)
        print(f"{Color.GREEN}[✓] DNS restored{Color.RESET}")
    
    print(f"\n{Color.GREEN}[✓] Clearnet restored{Color.RESET}")

def restart_tor():
    """Restart Tor to get new circuit"""
    print(f"\n{Color.CYAN}[*] Restarting Tor for new circuit...{Color.RESET}")
    
    result = run_cmd("systemctl restart tor-t0rpoiz0n.service", check=False)
    
    if result.returncode == 0:
        time.sleep(5)
        print(f"{Color.GREEN}[✓] New Tor circuit established{Color.RESET}")
        check_tor_status()
        return True
    else:
        print(f"{Color.RED}[✗] Failed to restart Tor{Color.RESET}")
        return False

def check_tor_status():
    """Check Tor connection status"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] Checking Tor Status{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    detect_iptables_backend()
    
    result = run_cmd("systemctl is-active tor-t0rpoiz0n.service", check=False)
    
    if result.stdout.strip() == "active":
        print(f"{Color.GREEN}[✓] Tor service: Active{Color.RESET}")
    else:
        print(f"{Color.RED}[✗] Tor service: Inactive{Color.RESET}")
        return False
    
    print(f"{Color.CYAN}[*] Testing Tor connection...{Color.RESET}")
    
    result = run_cmd("curl -s --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip", check=False)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            if data.get('IsTor'):
                print(f"{Color.GREEN}[✓] Connected through Tor{Color.RESET}")
                print(f"{Color.CYAN}[*] Exit IP: {data.get('IP', 'Unknown')}{Color.RESET}")
            else:
                print(f"{Color.RED}[✗] Not connected through Tor!{Color.RESET}")
        except:
            print(f"{Color.YELLOW}[!] Could not parse response{Color.RESET}")
    else:
        print(f"{Color.YELLOW}[!] Could not test connection{Color.RESET}")
    
    result = run_cmd("journalctl -u tor-t0rpoiz0n.service -n 3 --no-pager | grep -i bootstrap", check=False)
    if result.stdout.strip():
        print(f"\n{Color.CYAN}[*] Bootstrap status:{Color.RESET}")
        print(result.stdout.strip())
    
    print(f"\n{Color.CYAN}[*] iptables statistics (backend: {IPTABLES_CMD}):{Color.RESET}")
    result = run_cmd(f"{IPTABLES_CMD} -L -n -v | head -15", check=False)
    if result.returncode == 0:
        print(result.stdout)
    
    print(f"\n{Color.YELLOW}{'='*60}{Color.RESET}")
    print(f"{Color.YELLOW}[!] Test as regular user (NOT root):{Color.RESET}")
    print(f"  curl https://check.torproject.org/api/ip")
    print(f"  https://whoer.net")
    print(f"{Color.YELLOW}{'='*60}{Color.RESET}\n")
    
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='t0rpoiz0n - Advanced Tor Transparent Proxy + MAC Spoofing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-s', '--start', action='store_true',
                       help='Start transparent proxy')
    parser.add_argument('-k', '--stop', action='store_true',
                       help='Stop transparent proxy')
    parser.add_argument('-r', '--restart', action='store_true',
                       help='Restart Tor (new circuit)')
    parser.add_argument('-c', '--check', action='store_true',
                       help='Check Tor status')
    parser.add_argument('-m', '--mac', action='store_true',
                       help='Change MAC address')
    parser.add_argument('-v', '--vendor', type=str,
                       help='MAC vendor prefix')
    parser.add_argument('-i', '--interface', type=str,
                       help='Network interface')
    parser.add_argument('--setup', action='store_true',
                       help='Re-run setup')
    
    args = parser.parse_args()
    
    banner()
    check_root()
    
    if args.setup or not DATA_DIR.exists():
        if not first_time_setup():
            sys.exit(1)
        if args.setup:
            sys.exit(0)
    
    if args.mac:
        interface = args.interface or get_default_interface()
        if not interface:
            print(f"{Color.RED}[✗] Could not detect interface{Color.RESET}")
            sys.exit(1)
        
        change_mac(interface, args.vendor)
        
        if not args.start:
            sys.exit(0)
    
    if args.start:
        if not start_transparent_proxy():
            sys.exit(1)
    elif args.stop:
        stop_transparent_proxy()
    elif args.restart:
        restart_tor()
    elif args.check:
        check_tor_status()
    else:
        parser.print_help()
        print(f"\n{Color.CYAN}Examples:{Color.RESET}")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -s{Color.RESET}              # Start")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -s -m -v apple{Color.RESET}  # Start + MAC")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -c{Color.RESET}              # Check status")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -r{Color.RESET}              # New identity")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -k{Color.RESET}              # Stop\n")

if __name__ == "__main__":
    main()
