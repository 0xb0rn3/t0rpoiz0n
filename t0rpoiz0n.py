#!/usr/bin/env python3
"""
t0rpoiz0n - Advanced Tor Transparent Proxy + MAC Spoofing Tool
Author: 0xb0rn3 | oxbv1
Version: 1.1.1 - Fixed iptables rules
Built for Arch Linux
"""

import os
import sys
import time
import subprocess
import random
import string
import json
import argparse
from pathlib import Path
from typing import Optional, List, Dict

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
    print(f"""{Color.CYAN}{Color.BOLD}
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
                    Version: 1.1.0
{Color.RESET}""")

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

def check_dependencies() -> bool:
    """Check if required packages are installed"""
    required = ['tor', 'iptables', 'macchanger']
    missing = []
    
    for pkg in required:
        if run_cmd(f"which {pkg}", check=False).returncode != 0:
            missing.append(pkg)
    
    if missing:
        print(f"{Color.YELLOW}[!] Missing packages: {', '.join(missing)}{Color.RESET}")
        print(f"{Color.CYAN}[*] Installing dependencies...{Color.RESET}")
        
        for pkg in missing:
            print(f"{Color.CYAN}    Installing {pkg}...{Color.RESET}")
            result = run_cmd(f"pacman -S --noconfirm {pkg}", check=False)
            if result.returncode != 0:
                print(f"{Color.RED}[✗] Failed to install {pkg}{Color.RESET}")
                return False
        
        print(f"{Color.GREEN}[✓] All dependencies installed{Color.RESET}")
    
    return True

def setup_directories():
    """Create necessary directories"""
    directories = [DATA_DIR, BACKUP_DIR, CONFIG_FILE.parent]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"{Color.GREEN}[✓] Created directory: {directory}{Color.RESET}")

def create_tor_service():
    """Create optimized tor.service file"""
    service_content = """[Unit]
Description=Anonymizing overlay network for TCP (t0rpoiz0n)
After=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/bin/tor -f /etc/tor/torrc
Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
"""
    
    service_path = Path("/etc/systemd/system/tor-t0rpoiz0n.service")
    
    # Backup original if exists
    original_service = Path("/usr/lib/systemd/system/tor.service")
    if original_service.exists() and not (BACKUP_DIR / "tor.service.original").exists():
        run_cmd(f"cp {original_service} {BACKUP_DIR}/tor.service.original")
    
    service_path.write_text(service_content)
    print(f"{Color.GREEN}[✓] Created custom tor service{Color.RESET}")
    
    run_cmd("systemctl daemon-reload")
    return service_path

def create_torrc():
    """Create optimized torrc configuration"""
    torrc_content = """## t0rpoiz0n Tor Configuration
## Author: 0xb0rn3 | oxbv1

DataDirectory /var/lib/tor
VirtualAddrNetworkIPv4 10.192.0.0/10
AutomapHostsOnResolve 1

# Transparent Proxy
TransPort 9040 IsolateClientAddr IsolateClientProtocol IsolateDestAddr IsolateDestPort

# SOCKS Proxy
SocksPort 9050 IsolateClientAddr IsolateClientProtocol IsolateDestAddr IsolateDestPort

# DNS
DNSPort 53

# Performance & Security
AvoidDiskWrites 1
HardwareAccel 1
SafeLogging 1
"""
    
    torrc_path = Path("/etc/tor/torrc")
    
    # Backup original
    if torrc_path.exists() and not (BACKUP_DIR / "torrc.original").exists():
        run_cmd(f"cp {torrc_path} {BACKUP_DIR}/torrc.original")
    
    torrc_path.write_text(torrc_content)
    print(f"{Color.GREEN}[✓] Created torrc configuration{Color.RESET}")

def setup_tor_permissions():
    """Setup proper Tor directory permissions"""
    tor_dir = Path("/var/lib/tor")
    
    # Ensure directory exists
    tor_dir.mkdir(parents=True, exist_ok=True)
    
    # Set ownership to root (since we run as root)
    run_cmd(f"chown -R root:root {tor_dir}")
    run_cmd(f"chmod 700 {tor_dir}")
    
    print(f"{Color.GREEN}[✓] Set Tor directory permissions{Color.RESET}")

def grant_port_capabilities():
    """Grant Tor capability to bind to privileged ports"""
    run_cmd("setcap 'cap_net_bind_service=+ep' /usr/bin/tor")
    print(f"{Color.GREEN}[✓] Granted port binding capabilities to Tor{Color.RESET}")

def create_iptables_rules():
    """Create iptables rules for transparent proxy with leak protection - FIXED VERSION"""
    rules = """*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]

# Redirect DNS to Tor DNSPort (for non-local traffic)
-A PREROUTING ! -i lo -p udp -m udp --dport 53 -j REDIRECT --to-ports 53
-A PREROUTING ! -i lo -p tcp -m tcp --dport 53 -j REDIRECT --to-ports 53

# Redirect TCP to Tor TransPort (for non-local traffic)
-A PREROUTING ! -i lo -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j REDIRECT --to-ports 9040

# OUTPUT chain - redirect local traffic
# Allow loopback
-A OUTPUT -o lo -j RETURN

# Allow LAN (optional - comment out for maximum security)
-A OUTPUT -d 192.168.0.0/16 -j RETURN
-A OUTPUT -d 10.0.0.0/8 -j RETURN
-A OUTPUT -d 172.16.0.0/12 -j RETURN

# Allow Tor process (UID 0 = root) - FIXED: use numeric UID
-A OUTPUT -m owner --uid-owner 0 -j RETURN

# Redirect DNS queries to Tor DNSPort
-A OUTPUT -p udp -m udp --dport 53 -j REDIRECT --to-ports 53
-A OUTPUT -p tcp -m tcp --dport 53 -j REDIRECT --to-ports 53

# Redirect all other TCP traffic to Tor TransPort
-A OUTPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j REDIRECT --to-ports 9040

COMMIT

*filter
:INPUT ACCEPT [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]

# INPUT rules
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow LAN input (optional)
-A INPUT -s 192.168.0.0/16 -j ACCEPT
-A INPUT -s 10.0.0.0/8 -j ACCEPT
-A INPUT -s 172.16.0.0/12 -j ACCEPT

# OUTPUT rules
# Allow loopback
-A OUTPUT -o lo -j ACCEPT

# Allow established connections
-A OUTPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow Tor process (UID 0) - FIXED: use numeric UID
-A OUTPUT -m owner --uid-owner 0 -j ACCEPT

# Allow DNS (will be redirected by nat table)
-A OUTPUT -p udp -m udp --dport 53 -j ACCEPT
-A OUTPUT -p tcp -m tcp --dport 53 -j ACCEPT

# Allow Tor ports
-A OUTPUT -p tcp -m tcp --dport 9040 -j ACCEPT
-A OUTPUT -p tcp -m tcp --dport 9050 -j ACCEPT

# Allow common Tor network ports
-A OUTPUT -p tcp -m tcp --dport 443 -j ACCEPT
-A OUTPUT -p tcp -m tcp --dport 80 -j ACCEPT
-A OUTPUT -p tcp -m tcp --dport 9001 -j ACCEPT
-A OUTPUT -p tcp -m tcp --dport 9030 -j ACCEPT

# Block QUIC/HTTP3 to prevent browser bypass (UDP 443)
-A OUTPUT -p udp -m udp --dport 443 -j REJECT --reject-with icmp-port-unreachable
-A OUTPUT -p udp -m udp --dport 80 -j REJECT --reject-with icmp-port-unreachable

# Block DNS over TLS/HTTPS (port 853)
-A OUTPUT -p tcp -m tcp --dport 853 -j REJECT --reject-with tcp-reset
-A OUTPUT -p udp -m udp --dport 853 -j REJECT --reject-with icmp-port-unreachable

# Drop other UDP to prevent leaks
-A OUTPUT -p udp -j DROP

# Accept other TCP (will be redirected by nat table)
-A OUTPUT -p tcp -j ACCEPT

COMMIT
"""
    
    rules_path = DATA_DIR / "iptables.rules"
    rules_path.write_text(rules)
    print(f"{Color.GREEN}[✓] Created iptables rules{Color.RESET}")
    
    return rules_path

def get_network_interface() -> str:
    """Detect active network interface"""
    result = run_cmd("ip route | grep default | awk '{print $5}' | head -n1", check=False)
    
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    
    # Fallback detection
    interfaces = Path("/sys/class/net").iterdir()
    for iface in interfaces:
        if iface.name not in ['lo', 'docker0', 'virbr0']:
            return iface.name
    
    return "eth0"

def change_mac_address(vendor: Optional[str] = None, interface: Optional[str] = None):
    """Change MAC address"""
    if not interface:
        interface = get_network_interface()
    
    print(f"{Color.CYAN}[*] Changing MAC address for {interface}...{Color.RESET}")
    
    # Bring interface down
    run_cmd(f"ip link set {interface} down")
    
    if vendor and vendor in MAC_VENDORS:
        prefix = MAC_VENDORS[vendor]
        suffix = ':'.join([''.join(random.choices('0123456789ABCDEF', k=2)) for _ in range(3)])
        new_mac = f"{prefix}:{suffix}"
        run_cmd(f"macchanger -m {new_mac} {interface}", check=False)
    else:
        # Random MAC
        run_cmd(f"macchanger -r {interface}", check=False)
    
    # Bring interface up
    run_cmd(f"ip link set {interface} up")
    
    # Get new MAC
    result = run_cmd(f"cat /sys/class/net/{interface}/address")
    new_mac = result.stdout.strip()
    
    print(f"{Color.GREEN}[✓] MAC changed to: {new_mac}{Color.RESET}")
    return new_mac

def start_transparent_proxy():
    """Start Tor transparent proxy"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] Starting Transparent Proxy{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    # Stop any existing Tor instances
    run_cmd("systemctl stop tor.service tor-t0rpoiz0n.service", check=False)
    run_cmd("killall tor", check=False)
    time.sleep(2)
    
    # Disable IPv6
    print(f"{Color.CYAN}[*] Disabling IPv6...{Color.RESET}")
    run_cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1 >/dev/null 2>&1")
    run_cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1 >/dev/null 2>&1")
    print(f"{Color.GREEN}[✓] IPv6 disabled{Color.RESET}")
    
    # Backup current DNS
    if Path("/etc/resolv.conf").exists():
        run_cmd(f"cp /etc/resolv.conf {BACKUP_DIR}/resolv.conf.backup", check=False)
    
    # Set DNS to localhost
    Path("/etc/resolv.conf").write_text("nameserver 127.0.0.1\n")
    print(f"{Color.GREEN}[✓] DNS configured{Color.RESET}")
    
    # Start Tor
    print(f"{Color.CYAN}[*] Starting Tor service...{Color.RESET}")
    result = run_cmd("systemctl start tor-t0rpoiz0n.service", check=False)
    
    if result.returncode != 0:
        print(f"{Color.RED}[✗] Failed to start Tor service{Color.RESET}")
        print(f"{Color.YELLOW}[*] Checking logs...{Color.RESET}")
        run_cmd("journalctl -u tor-t0rpoiz0n.service -n 20 --no-pager")
        return False
    
    time.sleep(3)
    print(f"{Color.GREEN}[✓] Tor service started{Color.RESET}")
    
    # Apply iptables rules
    print(f"{Color.CYAN}[*] Applying iptables rules...{Color.RESET}")
    rules_path = DATA_DIR / "iptables.rules"
    
    # Flush existing rules
    run_cmd("iptables -F")
    run_cmd("iptables -X")
    run_cmd("iptables -t nat -F")
    run_cmd("iptables -t nat -X")
    
    # Apply new rules
    run_cmd(f"iptables-restore < {rules_path}")
    print(f"{Color.GREEN}[✓] iptables rules applied{Color.RESET}")
    
    # Wait for Tor to bootstrap
    print(f"{Color.CYAN}[*] Waiting for Tor to bootstrap...{Color.RESET}")
    
    for i in range(30):
        result = run_cmd("systemctl is-active tor-t0rpoiz0n.service", check=False)
        if result.stdout.strip() == "active":
            time.sleep(2)
            break
        time.sleep(1)
    else:
        print(f"{Color.YELLOW}[!] Tor may still be bootstrapping...{Color.RESET}")
    
    print(f"{Color.GREEN}[✓] Transparent proxy activated{Color.RESET}")
    
    # Show browser warning
    print(f"\n{Color.YELLOW}{'='*60}{Color.RESET}")
    print(f"{Color.YELLOW}{Color.BOLD}[!] IMPORTANT: Browser Configuration Required{Color.RESET}")
    print(f"{Color.YELLOW}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}Modern browsers may leak your IP through:{Color.RESET}")
    print(f"  • DNS-over-HTTPS (DoH)")
    print(f"  • QUIC/HTTP3 protocol")
    print(f"  • WebRTC")
    print(f"\n{Color.GREEN}RECOMMENDED: Use Tor Browser{Color.RESET}")
    print(f"  Download: https://www.torproject.org/download/\n")
    print(f"{Color.YELLOW}OR configure Firefox manually:{Color.RESET}")
    print(f"  1. Go to: {Color.CYAN}about:config{Color.RESET}")
    print(f"  2. Set {Color.CYAN}network.trr.mode = 5{Color.RESET} (disable DoH)")
    print(f"  3. Set {Color.CYAN}network.http.http3.enabled = false{Color.RESET} (disable QUIC)")
    print(f"  4. Set {Color.CYAN}media.peerconnection.enabled = false{Color.RESET} (disable WebRTC)")
    print(f"{Color.YELLOW}{'='*60}{Color.RESET}\n")
    
    return True

def stop_transparent_proxy():
    """Stop Tor transparent proxy and restore system"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] Stopping Transparent Proxy{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    # Stop Tor
    print(f"{Color.CYAN}[*] Stopping Tor service...{Color.RESET}")
    run_cmd("systemctl stop tor-t0rpoiz0n.service", check=False)
    print(f"{Color.GREEN}[✓] Tor stopped{Color.RESET}")
    
    # Flush iptables
    print(f"{Color.CYAN}[*] Flushing iptables rules...{Color.RESET}")
    run_cmd("iptables -F")
    run_cmd("iptables -X")
    run_cmd("iptables -t nat -F")
    run_cmd("iptables -t nat -X")
    run_cmd("iptables -P INPUT ACCEPT")
    run_cmd("iptables -P FORWARD ACCEPT")
    run_cmd("iptables -P OUTPUT ACCEPT")
    print(f"{Color.GREEN}[✓] iptables flushed{Color.RESET}")
    
    # Restore DNS
    resolv_backup = BACKUP_DIR / "resolv.conf.backup"
    if resolv_backup.exists():
        run_cmd(f"cp {resolv_backup} /etc/resolv.conf")
        print(f"{Color.GREEN}[✓] DNS restored{Color.RESET}")
    
    # Enable IPv6
    print(f"{Color.CYAN}[*] Enabling IPv6...{Color.RESET}")
    run_cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=0 >/dev/null 2>&1")
    run_cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=0 >/dev/null 2>&1")
    print(f"{Color.GREEN}[✓] IPv6 enabled{Color.RESET}")
    
    # Restart NetworkManager
    print(f"{Color.CYAN}[*] Restarting NetworkManager...{Color.RESET}")
    run_cmd("systemctl restart NetworkManager", check=False)
    print(f"{Color.GREEN}[✓] NetworkManager restarted{Color.RESET}")
    
    print(f"\n{Color.GREEN}[✓] Transparent proxy stopped - clearnet restored{Color.RESET}")

def check_status():
    """Check status of Tor and connection"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] System Status{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    # Check Tor service
    result = run_cmd("systemctl is-active tor-t0rpoiz0n.service", check=False)
    if result.stdout.strip() == "active":
        print(f"{Color.GREEN}[✓] Tor service: ACTIVE{Color.RESET}")
    else:
        print(f"{Color.RED}[✗] Tor service: INACTIVE{Color.RESET}")
        return
    
    # Check Tor connection
    print(f"\n{Color.CYAN}[*] Testing Tor connection...{Color.RESET}")
    result = run_cmd(
        "curl -s --socks5-hostname localhost:9050 https://check.torproject.org/api/ip",
        check=False
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            if data.get('IsTor'):
                print(f"{Color.GREEN}[✓] Connected to Tor network{Color.RESET}")
                print(f"{Color.CYAN}[*] Exit IP: {data.get('IP')}{Color.RESET}")
            else:
                print(f"{Color.RED}[✗] NOT connected to Tor{Color.RESET}")
        except:
            print(f"{Color.YELLOW}[!] Could not parse response{Color.RESET}")
    else:
        print(f"{Color.RED}[✗] Connection test failed{Color.RESET}")
    
    # Test transparent proxy (as current user, not root)
    print(f"\n{Color.CYAN}[*] Testing transparent proxy...{Color.RESET}")
    print(f"{Color.YELLOW}[!] Note: Test this as regular user (not root){Color.RESET}")
    
    # Check iptables rules
    print(f"\n{Color.CYAN}[*] Checking iptables rules...{Color.RESET}")
    result = run_cmd("iptables -t nat -L -n -v | grep -c '9040'", check=False)
    if int(result.stdout.strip() or 0) > 0:
        print(f"{Color.GREEN}[✓] iptables rules active{Color.RESET}")
    else:
        print(f"{Color.RED}[✗] iptables rules not found{Color.RESET}")
    
    # Show packet counts
    result = run_cmd("iptables -t nat -L -n -v | grep 9040 | head -1", check=False)
    if result.stdout.strip():
        print(f"{Color.CYAN}[*] Packets redirected: {result.stdout.strip().split()[0]}{Color.RESET}")
    
    # Show bootstrap status
    print(f"\n{Color.CYAN}[*] Recent Tor logs:{Color.RESET}")
    run_cmd("journalctl -u tor-t0rpoiz0n.service --no-pager | grep 'Bootstrapped' | tail -3", check=False)
    
    # Leak test warning
    print(f"\n{Color.YELLOW}{'='*60}{Color.RESET}")
    print(f"{Color.YELLOW}{Color.BOLD}[!] Leak Testing Recommendations{Color.RESET}")
    print(f"{Color.YELLOW}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}Test for leaks (as regular user, NOT root):{Color.RESET}")
    print(f"  • https://check.torproject.org")
    print(f"  • https://whoer.net")
    print(f"  • https://ipleak.net")
    print(f"  • https://browserleaks.com")
    print(f"\n{Color.YELLOW}Command line test:{Color.RESET}")
    print(f"  {Color.GREEN}curl https://check.torproject.org/api/ip{Color.RESET}")
    print(f"  (Run as regular user, NOT with sudo)")
    print(f"{Color.YELLOW}{'='*60}{Color.RESET}\n")

def change_identity():
    """Get new Tor circuit / IP"""
    print(f"{Color.CYAN}[*] Requesting new Tor circuit...{Color.RESET}")
    
    run_cmd("systemctl restart tor-t0rpoiz0n.service")
    time.sleep(5)
    
    print(f"{Color.GREEN}[✓] New circuit established{Color.RESET}")
    check_status()

def setup_environment():
    """Complete first-time setup"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] First-Time Setup{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    # Check dependencies
    print(f"{Color.CYAN}[*] Checking dependencies...{Color.RESET}")
    if not check_dependencies():
        return False
    
    # Create directories
    print(f"\n{Color.CYAN}[*] Creating directories...{Color.RESET}")
    setup_directories()
    
    # Create Tor service
    print(f"\n{Color.CYAN}[*] Creating Tor service...{Color.RESET}")
    create_tor_service()
    
    # Create torrc
    print(f"\n{Color.CYAN}[*] Creating Tor configuration...{Color.RESET}")
    create_torrc()
    
    # Setup permissions
    print(f"\n{Color.CYAN}[*] Setting permissions...{Color.RESET}")
    setup_tor_permissions()
    
    # Grant capabilities
    print(f"\n{Color.CYAN}[*] Granting capabilities...{Color.RESET}")
    grant_port_capabilities()
    
    # Create iptables rules
    print(f"\n{Color.CYAN}[*] Creating iptables rules...{Color.RESET}")
    create_iptables_rules()
    
    # Mark setup as complete
    CONFIG_FILE.write_text(json.dumps({'setup_complete': True, 'version': '1.1.1'}))
    
    print(f"\n{Color.GREEN}{'='*60}{Color.RESET}")
    print(f"{Color.GREEN}{Color.BOLD}[✓] Setup Complete!{Color.RESET}")
    print(f"{Color.GREEN}{'='*60}{Color.RESET}\n")
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='t0rpoiz0n - Advanced Tor Transparent Proxy + MAC Spoofing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-s', '--start', action='store_true', help='Start transparent proxy')
    parser.add_argument('-k', '--stop', action='store_true', help='Stop transparent proxy')
    parser.add_argument('-r', '--restart', action='store_true', help='Restart and change identity')
    parser.add_argument('-c', '--check', action='store_true', help='Check status')
    parser.add_argument('-m', '--mac', action='store_true', help='Change MAC address')
    parser.add_argument('-v', '--vendor', choices=list(MAC_VENDORS.keys()), help='MAC vendor')
    parser.add_argument('-i', '--interface', help='Network interface')
    parser.add_argument('--setup', action='store_true', help='Run first-time setup')
    
    args = parser.parse_args()
    
    # Check root
    check_root()
    
    # Show banner
    banner()
    
    # Check if setup is needed
    if not CONFIG_FILE.exists() or args.setup:
        if not setup_environment():
            sys.exit(1)
        if args.setup:
            sys.exit(0)
    
    # Handle commands
    if args.start:
        if args.mac:
            change_mac_address(args.vendor, args.interface)
        start_transparent_proxy()
        check_status()
    
    elif args.stop:
        stop_transparent_proxy()
    
    elif args.restart:
        change_identity()
    
    elif args.check:
        check_status()
    
    elif args.mac:
        change_mac_address(args.vendor, args.interface)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}[!] Interrupted by user{Color.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Color.RED}[✗] Error: {e}{Color.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
