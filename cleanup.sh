#!/usr/bin/env bash
#
# t0rpoiz0n - Complete Removal Script
# Removes ALL traces of previous installation
# Author: 0xb0rn3 | oxbv1
#

RED='\033[31m'
GREEN='\033[32m'
CYAN='\033[36m'
YELLOW='\033[33m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║         t0rpoiz0n - COMPLETE REMOVAL SCRIPT                ║
║         This will remove ALL traces of t0rpoiz0n           ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}\n"

# Check root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}[✗] This script must be run as root${RESET}"
    echo -e "${YELLOW}[!] Usage: sudo bash cleanup.sh${RESET}"
    exit 1
fi

echo -e "${YELLOW}${BOLD}WARNING: This will remove:${RESET}"
echo -e "${YELLOW}  • All t0rpoiz0n executables${RESET}"
echo -e "${YELLOW}  • Tor service and configuration${RESET}"
echo -e "${YELLOW}  • iptables configurations${RESET}"
echo -e "${YELLOW}  • All backup files${RESET}"
echo -e "${YELLOW}  • Module configurations${RESET}"
echo -e "${YELLOW}  • Update check data${RESET}\n"

read -p "Are you sure you want to continue? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}[*] Aborted.${RESET}"
    exit 0
fi

echo -e "\n${CYAN}${BOLD}[*] COMPLETE REMOVAL IN PROGRESS${RESET}\n"

# Step 1: Stop all services
echo -e "${CYAN}[*] Step 1/10: Stopping services...${RESET}"
systemctl stop tor-t0rpoiz0n.service 2>/dev/null || true
systemctl stop tor.service 2>/dev/null || true
systemctl disable tor-t0rpoiz0n.service 2>/dev/null || true
killall -9 tor 2>/dev/null || true
sleep 2
echo -e "${GREEN}[✓] Services stopped${RESET}"

# Step 2: Flush and restore iptables
echo -e "${CYAN}[*] Step 2/10: Restoring iptables...${RESET}"
iptables -F 2>/dev/null || true
iptables -X 2>/dev/null || true
iptables -t nat -F 2>/dev/null || true
iptables -t nat -X 2>/dev/null || true
iptables -t mangle -F 2>/dev/null || true
iptables -t mangle -X 2>/dev/null || true
iptables -P INPUT ACCEPT 2>/dev/null || true
iptables -P FORWARD ACCEPT 2>/dev/null || true
iptables -P OUTPUT ACCEPT 2>/dev/null || true
echo -e "${GREEN}[✓] iptables restored${RESET}"

# Step 3: Re-enable IPv6
echo -e "${CYAN}[*] Step 3/10: Re-enabling IPv6...${RESET}"
sysctl -w net.ipv6.conf.all.disable_ipv6=0 >/dev/null 2>&1
sysctl -w net.ipv6.conf.default.disable_ipv6=0 >/dev/null 2>&1
echo -e "${GREEN}[✓] IPv6 re-enabled${RESET}"

# Step 4: Remove systemd service files
echo -e "${CYAN}[*] Step 4/10: Removing systemd services...${RESET}"
rm -f /etc/systemd/system/tor-t0rpoiz0n.service
rm -f /etc/systemd/system/tor-t0rpoiz0n.service.d/*
rmdir /etc/systemd/system/tor-t0rpoiz0n.service.d 2>/dev/null || true
systemctl daemon-reload
echo -e "${GREEN}[✓] Systemd services removed${RESET}"

# Step 5: Remove executables
echo -e "${CYAN}[*] Step 5/10: Removing executables...${RESET}"
rm -f /usr/local/bin/t0rpoiz0n
rm -f /usr/local/bin/t0rpoiz0n-wrapper
rm -f /usr/local/bin/t0rpoiz0n-actual
rm -f /usr/bin/t0rpoiz0n
rm -f /bin/t0rpoiz0n
echo -e "${GREEN}[✓] Executables removed${RESET}"

# Step 6: Remove data directories
echo -e "${CYAN}[*] Step 6/10: Removing data directories...${RESET}"
rm -rf /usr/share/t0rpoiz0n
rm -rf /var/lib/t0rpoiz0n
rm -rf /var/cache/t0rpoiz0n
rm -rf /usr/local/share/t0rpoiz0n
echo -e "${GREEN}[✓] Data directories removed${RESET}"

# Step 7: Remove configuration directories
echo -e "${CYAN}[*] Step 7/10: Removing configuration directories...${RESET}"
rm -rf /etc/t0rpoiz0n
rm -f /etc/tor/torrc.t0rpoiz0n
rm -f /etc/tor/torrc.backup
echo -e "${GREEN}[✓] Configuration directories removed${RESET}"

# Step 8: Remove module configuration
echo -e "${CYAN}[*] Step 8/10: Removing module configuration...${RESET}"
rm -f /etc/modules-load.d/iptables.conf
rm -f /etc/modules-load.d/t0rpoiz0n.conf
echo -e "${GREEN}[✓] Module configuration removed${RESET}"

# Step 9: Restore DNS if backed up
echo -e "${CYAN}[*] Step 9/10: Restoring DNS configuration...${RESET}"
if [[ -f /var/lib/t0rpoiz0n/backups/resolv.conf.backup ]]; then
    cp /var/lib/t0rpoiz0n/backups/resolv.conf.backup /etc/resolv.conf
    echo -e "${GREEN}[✓] DNS configuration restored${RESET}"
else
    # Use default DNS
    echo "nameserver 8.8.8.8" > /etc/resolv.conf
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf
    echo -e "${GREEN}[✓] DNS set to Google DNS (8.8.8.8)${RESET}"
fi

# Step 10: Clean up any remaining traces
echo -e "${CYAN}[*] Step 10/10: Final cleanup...${RESET}"
# Remove any orphaned tor directories
rm -rf /var/lib/tor/t0rpoiz0n 2>/dev/null || true
rm -rf /var/cache/tor/t0rpoiz0n 2>/dev/null || true

# Remove capabilities from tor binary if they were set
setcap -r /usr/bin/tor 2>/dev/null || true

# Clear any systemd failures
systemctl reset-failed 2>/dev/null || true

echo -e "${GREEN}[✓] Final cleanup complete${RESET}"

# Display summary
echo -e "\n${GREEN}${BOLD}╔════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║           COMPLETE REMOVAL SUCCESSFUL!                     ║${RESET}"
echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════════════════════╝${RESET}\n"

echo -e "${CYAN}${BOLD}Removed components:${RESET}"
echo -e "${GREEN}  ✓ Tor services and configurations${RESET}"
echo -e "${GREEN}  ✓ All executables and scripts${RESET}"
echo -e "${GREEN}  ✓ iptables rules${RESET}"
echo -e "${GREEN}  ✓ IPv6 blocks${RESET}"
echo -e "${GREEN}  ✓ Data and backup directories${RESET}"
echo -e "${GREEN}  ✓ Configuration files${RESET}"
echo -e "${GREEN}  ✓ Module configurations${RESET}"
echo -e "${GREEN}  ✓ DNS overrides${RESET}\n"

echo -e "${CYAN}${BOLD}System state:${RESET}"
echo -e "${CYAN}  • iptables: ${GREEN}Restored to defaults${RESET}"
echo -e "${CYAN}  • IPv6: ${GREEN}Re-enabled${RESET}"
echo -e "${CYAN}  • DNS: ${GREEN}Restored${RESET}"
echo -e "${CYAN}  • Tor: ${GREEN}Stopped and disabled${RESET}\n"

echo -e "${YELLOW}${BOLD}Next steps:${RESET}"
echo -e "${CYAN}  1. Your system is now clean${RESET}"
echo -e "${CYAN}  2. You can now install v1.1.1 fresh${RESET}"
echo -e "${CYAN}  3. Run: ${GREEN}sudo ./run --install${RESET}\n"

echo -e "${CYAN}Cleanup complete! System returned to normal state.${RESET}\n"
