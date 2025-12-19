# t0rpoiz0n

**Advanced Tor Transparent Proxy + MAC Spoofing Framework for Arch Linux**

Author: **0xb0rn3 | oxbv1**  
Version: **1.1.3**  
Release Date: **December 19, 2025**

---

## 🎯 Features

- ✅ **Transparent Tor Proxy** - Route ALL system traffic through Tor
- ✅ **MAC Address Spoofing** - Change MAC with vendor-specific prefixes
- ✅ **Automated Setup** - One-command installation and configuration
- ✅ **Zero Configuration** - Works out of the box
- ✅ **Production Ready** - Comprehensive error handling
- ✅ **nftables Compatible** - Native support for modern iptables-nft backend
- ✅ **Smart Rule Generation** - Automatically creates compatible rules for your system
- ✅ **IPv6 Disabled** - Prevents leaks
- ✅ **DNS through Tor** - All DNS queries via Tor DNSPort
- ✅ **Easy Identity Changes** - New Tor circuit with one command
- ✅ **Dual Backend Support** - Works with both iptables-nft and iptables-legacy
- ✅ **Auto-Update Check** - Checks GitHub for updates every 24 hours

---

## 🆕 What's New in v1.1.3

### 🔧 CRITICAL FIX - nftables Compatibility

**FINALLY FIXED**: The "RULE_APPEND failed (Invalid argument)" error on modern Arch Linux!

#### The Problem (v1.1.2 and earlier)
```
[✗] Command failed: iptables-nft-restore
Error: line 15: RULE_APPEND failed (Invalid argument)
```

#### The Solution (v1.1.3)
- ✅ **Smart Rule Generation**: Creates nftables-compatible OR legacy rules based on detected backend
- ✅ **Native nft Support**: Uses direct `nft` commands for IPv6 blocking on modern systems
- ✅ **Automatic Backend Detection**: Detects iptables-nft vs iptables-legacy and adapts
- ✅ **Dual Rule System**: Separate optimized rules for each backend type

**Result**: Tool now works perfectly on modern Arch Linux with nftables! 🎉

---

## 📦 Installation

### Method 1: Systemwide Install (Recommended)

```bash
# Clone repository
git clone https://github.com/0xb0rn3/t0rpoiz0n.git
cd t0rpoiz0n

# Make installer executable
chmod +x run

# Install systemwide
sudo ./run --install
```

After installation, use `t0rpoiz0n` from anywhere:
```bash
sudo t0rpoiz0n -s
```

### Method 2: Run Locally (No Installation)

```bash
# Clone repository
git clone https://github.com/0xb0rn3/t0rpoiz0n.git
cd t0rpoiz0n

# Make executable and run
chmod +x run
sudo ./run -s
```

The installer will:
1. Install dependencies (tor, iptables, macchanger)
2. Detect your iptables backend (nft or legacy)
3. Create backend-appropriate rules
4. Setup Tor service with optimized configuration
5. Grant necessary capabilities
6. Make `t0rpoiz0n` available system-wide

---

## 🔄 Upgrading from v1.1.2 or Earlier

**IMPORTANT**: If you're experiencing "RULE_APPEND failed" errors, upgrade immediately!

```bash
# Go to your repository
cd ~/t0rpoiz0n

# Download new v1.1.3 file
# Copy the new t0rpoiz0n.py to your directory

# Replace old version
cp ~/Downloads/t0rpoiz0n.py ./t0rpoiz0n.py

# Update system installation
sudo cp ./t0rpoiz0n.py /usr/local/bin/t0rpoiz0n
sudo chmod +x /usr/local/bin/t0rpoiz0n

# Regenerate rules for YOUR backend
sudo t0rpoiz0n --setup

# Test it
sudo t0rpoiz0n -s -m -v motorola
```

---

## 🚀 Quick Start

### After Systemwide Install

```bash
# Start transparent proxy
sudo t0rpoiz0n -s

# Start with MAC spoofing
sudo t0rpoiz0n -s -m

# Start with specific MAC vendor
sudo t0rpoiz0n -s -m -v apple

# Check status
sudo t0rpoiz0n -c

# Change identity (new Tor circuit)
sudo t0rpoiz0n -r

# Stop and restore clearnet
sudo t0rpoiz0n -k
```

### Running Locally (No Install)

```bash
# Start transparent proxy
sudo ./run -s

# Start with MAC spoofing
sudo ./run -s -m -v apple

# Check status
sudo ./run -c

# Change identity
sudo ./run -r

# Stop
sudo ./run -k
```

---

## 📖 Usage

### Command-Line Options

```
-s, --start              Start transparent proxy
-k, --stop               Stop transparent proxy and restore clearnet
-r, --restart            Restart Tor and get new circuit/IP
-c, --check              Check Tor status and connection
-m, --mac                Change MAC address
-v, --vendor VENDOR      Use specific MAC vendor prefix
-i, --interface IFACE    Specify network interface
--setup                  Re-run first-time setup
```

### Available MAC Vendors

- `samsung` - Samsung devices
- `apple` - Apple devices
- `huawei` - Huawei devices
- `nokia` - Nokia devices
- `google` - Google devices
- `dell` - Dell computers
- `hp` - HP computers
- `asus` - ASUS devices
- `lenovo` - Lenovo computers
- `motorola` - Motorola devices

---

## 🔧 Advanced Usage

### Change MAC Only
```bash
sudo t0rpoiz0n -m -v samsung
```

### Specify Network Interface
```bash
sudo t0rpoiz0n -s -m -v apple -i wlan0
```

### Check Current Status
```bash
sudo t0rpoiz0n -c
```
Shows:
- Tor service status
- Connection test
- Current exit IP
- Bootstrap status
- iptables statistics
- Detected backend (nft or legacy)

---

## 🛠️ Technical Details

### What's Fixed in v1.1.3

This version completely resolves the nftables compatibility issues:

1. **✅ Smart Rule Generation** - Creates different rules for different backends
2. **✅ nftables-Compatible Rules** - Removes incompatible options for nft backend
3. **✅ Native nft Commands** - Uses direct `nft` for IPv6 blocking
4. **✅ Owner Matching Handled** - Removed from nft rules, kept in legacy rules
5. **✅ IPv6-ICMP Fixed** - Uses native nft commands instead of iptables syntax
6. **✅ Automatic Backend Detection** - Detects and adapts to your system

### Architecture

```
User Command
    ↓
Backend Detection
    ├→ iptables-nft (modern) → nftables-compatible rules
    └→ iptables-legacy (traditional) → full-featured rules
    ↓
t0rpoiz0n (Python)
    ↓
├→ Smart Rule Generator
│   ├→ create_iptables_rules_nft() for nftables
│   └→ create_iptables_rules_legacy() for legacy
│
├→ Tor Service (systemd)
│   ├→ TransPort: 9040 (Transparent Proxy)
│   ├→ SocksPort: 9050 (SOCKS5 Proxy)
│   └→ DNSPort: 53 (DNS)
│
├→ iptables (NAT + Filter)
│   ├→ Redirect TCP → 9040
│   ├→ Redirect DNS → 53
│   └→ Block IPv6
│
├→ Native nft (for nftables backend)
│   └→ Block IPv6-ICMP
│
└→ macchanger (Optional)
    └→ Spoof MAC Address
```

### Rule Differences by Backend

#### nftables Backend (Modern Arch)
```bash
# What's REMOVED (incompatible with nft):
-m owner --uid-owner tor    # Owner matching
-p ipv6-icmp                # IPv6-ICMP protocol

# What's ADDED (native nft):
nft add rule inet filter output meta l4proto ipv6-icmp drop
nft add rule inet filter output ip6 version 6 drop
```

#### Legacy Backend (Traditional)
```bash
# What's INCLUDED (full features):
-m owner --uid-owner tor    # Owner matching works
-p ipv6-icmp                # Protocol blocking works
```

### Files Created

- `/usr/local/bin/t0rpoiz0n` - Main executable
- `/etc/systemd/system/tor-t0rpoiz0n.service` - Custom Tor service
- `/etc/tor/torrc` - Tor configuration
- `/usr/share/t0rpoiz0n/` - Data directory
- `/usr/share/t0rpoiz0n/iptables.rules` - Backend-specific rules
- `/var/lib/t0rpoiz0n/backups/` - Original file backups
- `/etc/t0rpoiz0n/config.json` - Tool configuration
- `/etc/t0rpoiz0n/.last_update_check` - Update check timestamp
- `/etc/t0rpoiz0n/.repo_path` - Repository path for updates

### Network Flow

```
Application
    ↓
Kernel Network Stack
    ↓
iptables REDIRECT (nft or legacy)
    ↓
Tor TransPort (9040) / DNSPort (53)
    ↓
Tor Network (3 hops)
    ↓
Exit Node
    ↓
Destination
```

---

## 🔒 Security Notes

### What This Tool Protects Against

✅ **IP Address Leaks** - All TCP traffic through Tor  
✅ **DNS Leaks** - All DNS queries through Tor  
✅ **IPv6 Leaks** - IPv6 disabled during operation  
✅ **MAC Address Tracking** - Optional MAC spoofing  

### What This Tool Does NOT Protect Against

❌ **Application-Level Leaks** - Apps with hardcoded IPs  
❌ **WebRTC Leaks** - Use browser extensions to block  
❌ **Time-Based Attacks** - Keep your system time accurate  
❌ **Malware** - Use proper security practices  

### Best Practices

1. **Use Tor Browser** for web browsing (not just Firefox)
2. **Don't torrent** over Tor (slows network, can leak IP)
3. **Don't login** to accounts with your real identity
4. **Keep software updated** including Tor
5. **Change identity regularly** with `-r` flag
6. **Test for leaks** at: https://whoer.net or https://ipleak.net

---

## 🛠 Troubleshooting

### "RULE_APPEND failed" Error (FIXED in v1.1.3)

If you're still seeing this error, you need to upgrade to v1.1.3:

```bash
# Quick upgrade
cd ~/t0rpoiz0n
cp ~/Downloads/t0rpoiz0n.py ./t0rpoiz0n.py
sudo cp ./t0rpoiz0n.py /usr/local/bin/t0rpoiz0n
sudo chmod +x /usr/local/bin/t0rpoiz0n
sudo t0rpoiz0n --setup
```

### Check Which Backend You're Using

```bash
# Check detection
sudo t0rpoiz0n --setup | grep backend

# Should show one of:
# [✓] Using iptables-nft (nftables backend)
# [✓] Using iptables-legacy (legacy backend)
```

### Tor Service Won't Start

```bash
# Check logs
sudo journalctl -u tor-t0rpoiz0n.service -n 50

# Check if port 53 is in use
sudo netstat -tulpn | grep :53

# Re-run setup
sudo t0rpoiz0n --setup
```

### Can't Access Internet

```bash
# Check Tor status
sudo t0rpoiz0n -c

# Restart with new circuit
sudo t0rpoiz0n -r

# If still failing, stop and restart
sudo t0rpoiz0n -k
sudo t0rpoiz0n -s
```

### MAC Change Fails

```bash
# Check interface name
ip link show

# Specify interface manually
sudo t0rpoiz0n -m -i wlan0
```

### DNS Not Working

```bash
# Check resolv.conf
cat /etc/resolv.conf
# Should show: nameserver 127.0.0.1

# Check Tor DNSPort
sudo netstat -tulpn | grep :53
```

### Rules Not Applying

```bash
# Check your backend
iptables-nft -L -n 2>&1 | head -5
iptables-legacy -L -n 2>&1 | head -5

# Force regeneration
sudo rm -rf /usr/share/t0rpoiz0n
sudo t0rpoiz0n --setup
```

---

## 📄 Comparison with Original Tools

### vs archtorify

| Feature | archtorify | t0rpoiz0n |
|---------|-----------|-----------|
| Setup | Manual | Automated |
| Service File | Broken typo | Fixed |
| User directive | Conflicts | Removed |
| Hardening | Too strict | Optimized |
| MAC Spoofing | ❌ | ✅ |
| Error Handling | Basic | Comprehensive |
| Status Checking | Limited | Detailed |
| nftables Support | ❌ | ✅ |
| Smart Rules | ❌ | ✅ |
| Dual Backend | ❌ | ✅ |

### vs ToriFY

| Feature | ToriFY | t0rpoiz0n |
|---------|--------|-----------|
| Transparent Proxy | ❌ | ✅ |
| MAC Spoofing | ✅ | ✅ |
| All Traffic | ❌ | ✅ |
| DNS Leak Protection | ❌ | ✅ |
| IPv6 Leak Protection | ❌ | ✅ |
| Arch Linux | ❌ | ✅ |
| nftables Support | ❌ | ✅ |
| Auto Backend Detection | ❌ | ✅ |

---

## 📜 License

This tool is for **educational and research purposes only**.

Users are responsible for complying with all applicable laws and regulations.

The author assumes no liability for misuse of this tool.

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Support for other Linux distributions
- GUI interface
- Additional MAC vendor databases
- Bridge support for censored regions
- Pluggable transports integration
- IPv6 transparent proxy support

---

## 📧 Contact

**Author:** 0xb0rn3 | oxbv1  
**GitHub:** https://github.com/0xb0rn3/t0rpoiz0n  
**Version:** 1.1.3  
**Release Date:** December 19, 2025

---

## 🗑️ Uninstallation

To completely remove t0rpoiz0n from your system:

```bash
cd t0rpoiz0n
sudo ./run --uninstall
```

Or use the cleanup script:

```bash
sudo bash cleanup.sh
```

This will:
- Stop and disable Tor service
- Remove all installed files
- Clean up system directories
- Restore iptables rules
- Remove systemwide command
- Remove all configurations

---

## 🎓 Credits

- **Tor Project** - The Tor network and software
- **brainfucksec** - Original archtorify concept
- **Debajyoti0-0** - MAC spoofing inspiration from ToriFY
- **Arch Linux Community** - nftables compatibility feedback

---

## ⚠️ Legal Disclaimer

This tool is provided for educational and legitimate security research purposes only. 

Users must:
- Comply with all applicable local, state, and federal laws
- Only use on networks and systems they own or have explicit permission to test
- Accept full responsibility for their actions
- Not use for illegal activities including unauthorized access, surveillance, or malicious purposes

The author and contributors are not responsible for misuse or damage caused by this tool.

**Use responsibly and ethically.**

---

## 🔖 Version History

| Version | Date | Status | Key Feature |
|---------|------|--------|-------------|
| **1.1.3** | **Dec 19, 2025** | **✅ STABLE** | **nftables compatibility** |
| 1.1.2 | Dec 19, 2025 | ⚠️ Broken on nftables | Backend detection |
| 1.1.1 | Dec 19, 2025 | ⚠️ Broken on nftables | Auto-updates |
| 1.1.0 | Dec 12, 2025 | ⚠️ Broken on nftables | DoH/QUIC fixes |
| 1.0.0 | Dec 12, 2025 | ⚠️ Broken on nftables | Initial release |

**Recommended Version:** v1.1.3 (Current)

---

*Built with 💀 for the security research community*

**Stay Anonymous. Stay Safe. Stay Updated.** 🛡️
