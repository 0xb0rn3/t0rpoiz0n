# t0rpoiz0n

**Advanced Tor Transparent Proxy + MAC Spoofing Framework for Arch Linux**

Author: **0xb0rn3 | oxbv1**  
Version: **1.1.0**

---

## 🎯 Features

- ✅ **Transparent Tor Proxy** - Route ALL system traffic through Tor
- ✅ **MAC Address Spoofing** - Change MAC with vendor-specific prefixes
- ✅ **Automated Setup** - One-command installation and configuration
- ✅ **Zero Configuration** - Works out of the box
- ✅ **Production Ready** - Comprehensive error handling
- ✅ **Fixed All Issues** - No more `Type=symple` or permission errors
- ✅ **IPv6 Disabled** - Prevents leaks
- ✅ **DNS through Tor** - All DNS queries via Tor DNSPort
- ✅ **Easy Identity Changes** - New Tor circuit with one command

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
2. Create system directories
3. Setup Tor service with fixed configuration
4. Grant necessary capabilities
5. Make `t0rpoiz0n` available system-wide

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

---

## 🛠️ Technical Details

### What Gets Fixed

This tool fixes all the issues from the original archtorify:

1. **✅ Type=symple → Type=simple** - Fixed systemd service typo
2. **✅ User tor conflict** - Removed from torrc, handled by systemd
3. **✅ DNSPort 53 permission** - Uses `setcap` for port binding
4. **✅ Hardening conflicts** - Simplified service file
5. **✅ Directory permissions** - Proper ownership for root execution
6. **✅ IPv6 leaks** - Disabled during proxy mode
7. **✅ DNS leaks** - All DNS through Tor

### Architecture

```
User Space
    ↓
t0rpoiz0n (Python)
    ↓
├─→ Tor Service (systemd)
│   ├─→ TransPort: 9040 (Transparent Proxy)
│   ├─→ SocksPort: 9050 (SOCKS5 Proxy)
│   └─→ DNSPort: 53 (DNS)
│
├─→ iptables (NAT + Filter)
│   ├─→ Redirect TCP → 9040
│   ├─→ Redirect DNS → 53
│   └─→ Block IPv6
│
└─→ macchanger (Optional)
    └─→ Spoof MAC Address
```

### Files Created

- `/usr/local/bin/t0rpoiz0n` - Main executable
- `/etc/systemd/system/tor-t0rpoiz0n.service` - Custom Tor service
- `/etc/tor/torrc` - Tor configuration
- `/usr/share/t0rpoiz0n/` - Data directory
- `/var/lib/t0rpoiz0n/backups/` - Original file backups
- `/etc/t0rpoiz0n/config.json` - Tool configuration

### Network Flow

```
Application
    ↓
Kernel Network Stack
    ↓
iptables REDIRECT
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

## 🐛 Troubleshooting

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

---

## 🔄 Comparison with Original Tools

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

### vs ToriFY

| Feature | ToriFY | t0rpoiz0n |
|---------|--------|-----------|
| Transparent Proxy | ❌ | ✅ |
| MAC Spoofing | ✅ | ✅ |
| All Traffic | ❌ | ✅ |
| DNS Leak Protection | ❌ | ✅ |
| IPv6 Leak Protection | ❌ | ✅ |
| Arch Linux | ❌ | ✅ |

---

## 📝 License

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

---

## 📧 Contact

**Author:** 0xb0rn3 | oxbv1  
**GitHub:** https://github.com/0xb0rn3/t0rpoiz0n  
**Version:** 1.0.0

---

## 🗑️ Uninstallation

To completely remove t0rpoiz0n from your system:

```bash
cd t0rpoiz0n
sudo ./run --uninstall
```

This will:
- Stop and disable Tor service
- Remove all installed files
- Clean up system directories
- Restore iptables rules
- Remove systemwide command

---

## 🎓 Credits

- **Tor Project** - The Tor network and software
- **brainfucksec** - Original archtorify concept
- **Debajyoti0-0** - MAC spoofing inspiration from ToriFY

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

*Built with 💀 for the security research community*
