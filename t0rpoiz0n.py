#!/usr/bin/env python3
"""
t0rpoiz0n - Advanced Tor Transparent Proxy + MAC Spoofing Tool
Author: 0xb0rn3 | oxbv1
Version: 1.1.1 - Fixed iptables kernel module loading
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
                    Version: 1.1.1
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

def load_iptables_modules():
    """Load required iptables kernel modules"""
    modules = ['iptable_filter', 'iptable_nat', 'iptable_mangle', 'ip_tables']
    loaded = []
    failed = []
    
    print(f"{Color.CYAN}[*] Checking iptables kernel modules...{Color.RESET}")
    
    for module in modules:
        # Check if module is already loaded
        check_result = run_cmd(f"lsmod | grep -q {module}", check=False)
        
        if check_result.returncode == 0:
            loaded.append(module)
            continue
        
        # Try to load the module
        load_result = run_cmd(f"modprobe {module}", check=False)
        
        if load_result.returncode == 0:
            loaded.append(module)
            print(f"{Color.GREEN}[✓] Loaded module: {module}{Color.RESET}")
        else:
            failed.append(module)
            print(f"{Color.YELLOW}[!] Could not load: {module}{Color.RESET}")
    
    if failed:
        print(f"\n{Color.YELLOW}[!] Warning: Some modules failed to load: {', '.join(failed)}{Color.RESET}")
        print(f"{Color.YELLOW}    This may be normal if you're using nftables{Color.RESET}")
        print(f"{Color.CYAN}    Attempting to continue anyway...{Color.RESET}\n")
    else:
        print(f"{Color.GREEN}[✓] All iptables modules ready{Color.RESET}")
    
    return len(failed) == 0

def ensure_iptables_legacy():
    """Ensure iptables-legacy is available and create modules config for boot"""
    # Create modules-load config for persistence
    modules_conf = Path("/etc/modules-load.d/iptables.conf")
    
    if not modules_conf.exists():
        print(f"{Color.CYAN}[*] Creating persistent modules configuration...{Color.RESET}")
        try:
            modules_conf.parent.mkdir(parents=True, exist_ok=True)
            modules_conf.write_text("# iptables kernel modules for t0rpoiz0n\n"
                                   "iptable_filter\n"
                                   "iptable_nat\n"
                                   "iptable_mangle\n"
                                   "ip_tables\n")
            print(f"{Color.GREEN}[✓] Modules will load automatically on boot{Color.RESET}")
        except Exception as e:
            print(f"{Color.YELLOW}[!] Could not create modules config: {e}{Color.RESET}")

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
    
    # Fallback: get first non-loopback interface
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
    
    # Bring interface down
    run_cmd(f"ip link set {interface} down", check=False)
    
    # Generate new MAC
    new_mac = generate_random_mac(vendor)
    
    # Change MAC
    result = run_cmd(f"macchanger -m {new_mac} {interface}", check=False)
    
    # Bring interface up
    run_cmd(f"ip link set {interface} up", check=False)
    
    if result.returncode == 0:
        print(f"{Color.GREEN}[✓] MAC changed to: {new_mac}{Color.RESET}")
        return True
    else:
        print(f"{Color.RED}[✗] Failed to change MAC address{Color.RESET}")
        return False

def create_iptables_rules():
    """Create iptables rules for transparent proxy"""
    rules = """# t0rpoiz0n iptables rules
# Generated for transparent Tor proxy

*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]

# Redirect DNS to Tor DNSPort
-A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 53
-A OUTPUT -p tcp --dport 53 -j REDIRECT --to-ports 53

# Block DNS-over-TLS (DoT)
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

# Block all IPv6 traffic
-A INPUT -p ipv6-icmp -j DROP
-A OUTPUT -p ipv6-icmp -j DROP
-A FORWARD -p ipv6-icmp -j DROP

# Allow loopback
-A INPUT -i lo -j ACCEPT
-A OUTPUT -o lo -j ACCEPT

# Allow established connections
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
-A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow Tor
-A OUTPUT -m owner --uid-owner tor -j ACCEPT

# Allow DNS to localhost
-A OUTPUT -p udp --dport 53 -d 127.0.0.1 -j ACCEPT
-A OUTPUT -p tcp --dport 53 -d 127.0.0.1 -j ACCEPT

# Allow traffic to Tor ports
-A OUTPUT -p tcp --dport 9040 -j ACCEPT
-A OUTPUT -p tcp --dport 9050 -j ACCEPT

# Block everything else UDP (prevent leaks)
-A OUTPUT -p udp -j REJECT

COMMIT
"""
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rules_file = DATA_DIR / "iptables.rules"
    rules_file.write_text(rules)
    
    return rules_file

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
    
    # Backup original if exists
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

# Run as root to bind to port 53
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
    
    # Reload systemd
    run_cmd("systemctl daemon-reload")
    
    # Grant capabilities to tor binary
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
    
    # Check dependencies
    print(f"{Color.CYAN}[*] Checking dependencies...{Color.RESET}")
    if not check_dependencies():
        return False
    print(f"{Color.GREEN}[✓] Dependencies OK{Color.RESET}")
    
    # Create directories
    print(f"{Color.CYAN}[*] Creating directories...{Color.RESET}")
    setup_directories()
    print(f"{Color.GREEN}[✓] Directories created{Color.RESET}")
    
    # Create iptables rules
    print(f"{Color.CYAN}[*] Creating iptables rules...{Color.RESET}")
    create_iptables_rules()
    print(f"{Color.GREEN}[✓] iptables rules created{Color.RESET}")
    
    # Create Tor config
    print(f"{Color.CYAN}[*] Creating Tor configuration...{Color.RESET}")
    create_torrc()
    print(f"{Color.GREEN}[✓] Tor config created{Color.RESET}")
    
    # Create systemd service
    print(f"{Color.CYAN}[*] Creating systemd service...{Color.RESET}")
    create_systemd_service()
    print(f"{Color.GREEN}[✓] Service created{Color.RESET}")
    
    # Load iptables modules and create persistent config
    load_iptables_modules()
    ensure_iptables_legacy()
    
    print(f"\n{Color.GREEN}[✓] Setup complete!{Color.RESET}")
    return True

def start_transparent_proxy():
    """Start Tor transparent proxy"""
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}[*] Starting Transparent Proxy{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    # Load iptables modules first
    load_iptables_modules()
    
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
    try:
        run_cmd("iptables -F")
        run_cmd("iptables -X")
        run_cmd("iptables -t nat -F")
        run_cmd("iptables -t nat -X")
    except subprocess.CalledProcessError as e:
        print(f"{Color.YELLOW}[!] Warning: Could not flush iptables rules{Color.RESET}")
        print(f"{Color.YELLOW}    This might be OK if you're using nftables{Color.RESET}")
        print(f"{Color.CYAN}    Attempting to continue...{Color.RESET}")
    
    # Apply new rules
    try:
        run_cmd(f"iptables-restore < {rules_path}")
        print(f"{Color.GREEN}[✓] iptables rules applied{Color.RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{Color.RED}[✗] Failed to apply iptables rules{Color.RESET}")
        print(f"{Color.YELLOW}[!] You may be using nftables instead of iptables{Color.RESET}")
        print(f"{Color.YELLOW}[*] Try: sudo systemctl stop nftables && sudo systemctl disable nftables{Color.RESET}")
        return False
    
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
    try:
        run_cmd("iptables -F")
        run_cmd("iptables -X")
        run_cmd("iptables -t nat -F")
        run_cmd("iptables -t nat -X")
        run_cmd("iptables -P INPUT ACCEPT")
        run_cmd("iptables -P FORWARD ACCEPT")
        run_cmd("iptables -P OUTPUT ACCEPT")
        print(f"{Color.GREEN}[✓] iptables flushed{Color.RESET}")
    except subprocess.CalledProcessError:
        print(f"{Color.YELLOW}[!] Could not flush iptables (might be using nftables){Color.RESET}")
    
    # Re-enable IPv6
    print(f"{Color.CYAN}[*] Re-enabling IPv6...{Color.RESET}")
    run_cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=0 >/dev/null 2>&1")
    run_cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=0 >/dev/null 2>&1")
    print(f"{Color.GREEN}[✓] IPv6 re-enabled{Color.RESET}")
    
    # Restore DNS
    backup_resolv = BACKUP_DIR / "resolv.conf.backup"
    if backup_resolv.exists():
        print(f"{Color.CYAN}[*] Restoring DNS configuration...{Color.RESET}")
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
        
        # Try to get new IP
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
    
    # Check service status
    result = run_cmd("systemctl is-active tor-t0rpoiz0n.service", check=False)
    
    if result.stdout.strip() == "active":
        print(f"{Color.GREEN}[✓] Tor service: Active{Color.RESET}")
    else:
        print(f"{Color.RED}[✗] Tor service: Inactive{Color.RESET}")
        return False
    
    # Check connection
    print(f"{Color.CYAN}[*] Testing Tor connection...{Color.RESET}")
    
    # Test with curl using Tor SOCKS proxy
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
            print(f"{Color.YELLOW}[!] Could not parse Tor check response{Color.RESET}")
    else:
        print(f"{Color.YELLOW}[!] Could not test Tor connection{Color.RESET}")
    
    # Show bootstrap status
    result = run_cmd("journalctl -u tor-t0rpoiz0n.service -n 3 --no-pager | grep -i bootstrap", check=False)
    if result.stdout.strip():
        print(f"\n{Color.CYAN}[*] Latest bootstrap messages:{Color.RESET}")
        print(result.stdout.strip())
    
    # Show iptables rule counts
    print(f"\n{Color.CYAN}[*] iptables statistics:{Color.RESET}")
    result = run_cmd("iptables -L -n -v | head -15", check=False)
    if result.returncode == 0:
        print(result.stdout)
    
    print(f"\n{Color.YELLOW}{'='*60}{Color.RESET}")
    print(f"{Color.YELLOW}[!] Testing Instructions:{Color.RESET}")
    print(f"{Color.CYAN}Run as regular user (NOT root):{Color.RESET}")
    print(f"  curl https://check.torproject.org/api/ip")
    print(f"\n{Color.CYAN}Or visit in browser:{Color.RESET}")
    print(f"  https://check.torproject.org")
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
                       help='Stop transparent proxy and restore clearnet')
    parser.add_argument('-r', '--restart', action='store_true',
                       help='Restart Tor and get new circuit/IP')
    parser.add_argument('-c', '--check', action='store_true',
                       help='Check Tor status and connection')
    parser.add_argument('-m', '--mac', action='store_true',
                       help='Change MAC address')
    parser.add_argument('-v', '--vendor', type=str,
                       help='Use specific MAC vendor prefix')
    parser.add_argument('-i', '--interface', type=str,
                       help='Specify network interface')
    parser.add_argument('--setup', action='store_true',
                       help='Re-run first-time setup')
    
    args = parser.parse_args()
    
    # Show banner
    banner()
    
    # Check root
    check_root()
    
    # Run setup if needed or requested
    if args.setup or not DATA_DIR.exists():
        if not first_time_setup():
            sys.exit(1)
        if args.setup:
            sys.exit(0)
    
    # Handle MAC spoofing
    if args.mac:
        interface = args.interface or get_default_interface()
        if not interface:
            print(f"{Color.RED}[✗] Could not detect network interface{Color.RESET}")
            print(f"{Color.YELLOW}[*] Specify with: -i <interface>{Color.RESET}")
            sys.exit(1)
        
        change_mac(interface, args.vendor)
        
        if not args.start:
            sys.exit(0)
    
    # Handle commands
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
        print(f"  {Color.GREEN}sudo t0rpoiz0n -s{Color.RESET}              # Start transparent proxy")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -s -m -v apple{Color.RESET}  # Start with MAC spoofing")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -c{Color.RESET}              # Check status")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -r{Color.RESET}              # Change identity")
        print(f"  {Color.GREEN}sudo t0rpoiz0n -k{Color.RESET}              # Stop and restore clearnet\n")

if __name__ == "__main__":
    main()
