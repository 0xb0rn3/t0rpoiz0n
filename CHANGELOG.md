# Changelog

All notable changes to t0rpoiz0n will be documented in this file.

## [1.1.2] - 2025-12-19

### 🔧 Critical Fixes
- **CRITICAL**: Fixed "iptables: Table does not exist" error on modern Arch systems
- **CRITICAL**: Automatic iptables backend detection (nft vs legacy)
- **CRITICAL**: Auto-switches to working iptables backend
- Fixed SyntaxWarning: invalid escape sequence in banner function
- Fixed compatibility with nftables-only kernels

### ✨ New Features
- Automatic iptables backend detection system
- Smart backend switching via update-alternatives
- Dynamic command selection (iptables-nft vs iptables-legacy)
- Backend status shown in all iptables operations
- Graceful fallback between nft and legacy backends

### 🛠️ Improvements
- All iptables commands now use detected backend
- Better error messages showing which backend is being used
- Smarter module loading (detects nft backend before attempting legacy modules)
- Enhanced status display shows detected backend
- Works out-of-the-box on modern Arch with nftables-only kernels

### 📝 Technical Changes
- Added `detect_iptables_backend()` function
- Added `switch_to_iptables_nft()` function for automatic switching
- Global variables for dynamic command selection:
  - `IPTABLES_CMD` - Dynamically set to working command
  - `IPTABLES_RESTORE_CMD` - Dynamically set to working restore command
  - `IPTABLES_SAVE_CMD` - Dynamically set to working save command
- Modified `load_iptables_modules()` to try backend detection first
- Updated `start_transparent_proxy()` to use detected backend
- Updated `stop_transparent_proxy()` to use detected backend
- Updated `check_tor_status()` to use detected backend
- Fixed banner function with raw string literal

### 🐛 Bug Fixes
- Fixed: "can't initialize iptables table `filter': Table does not exist"
- Fixed: "iptables-restore: unable to initialize table 'nat'"
- Fixed: Module loading failures on nftables-only kernels
- Fixed: SyntaxWarning about invalid escape sequence '\\ ' in docstring

### ⚠️ Breaking Changes
- None - fully backward compatible

### 🔄 Migration from v1.1.1

```bash
# Quick update method
cd ~/t0rpoiz0n
cp ~/Downloads/t0rpoiz0n.py ./t0rpoiz0n.py
sudo cp ./t0rpoiz0n.py /usr/local/bin/t0rpoiz0n
sudo chmod +x /usr/local/bin/t0rpoiz0n
sudo t0rpoiz0n -s

# Or clean reinstall
cd ~/Downloads
chmod +x cleanup.sh
sudo bash cleanup.sh
cd ~/t0rpoiz0n
cp ~/Downloads/t0rpoiz0n.py ./t0rpoiz0n.py
chmod +x t0rpoiz0n.py
sudo ./run --install
```

---

## [1.1.1] - 2025-12-19

### 🔧 Bug Fixes
- **CRITICAL**: Fixed iptables "Table does not exist" error on modern Arch systems
- **CRITICAL**: Auto-loads iptables kernel modules (iptable_filter, iptable_nat, iptable_mangle)
- Fixed compatibility with systems using nftables by default
- Added graceful fallback when iptables modules fail to load

### ✨ New Features
- Automatic detection and loading of iptables kernel modules
- Persistent module configuration via `/etc/modules-load.d/iptables.conf`
- Modules automatically load on boot after setup
- Better error messages with actionable troubleshooting steps
- Enhanced compatibility check for nftables systems
- **Auto-Update Checker** - Checks GitHub for updates every 24 hours
- **One-Click Updates** - Prompts user and auto-installs new versions
- **Smart Update Timing** - Only checks once per 24 hours to avoid slowdown

### 🛠️ Improvements
- More robust iptables initialization process
- Better error handling for module loading
- Clear status messages during module loading
- Graceful degradation on module loading failures
- Auto-update system integrated into run script
- Update checks run silently in background (no slowdown)
- Stores last check timestamp to avoid redundant checks

### ⚠️ Breaking Changes
- None - fully backward compatible

---

## [1.1.0] - 2025-12-12

### 🔒 Security Fixes
- **CRITICAL**: Fixed browser IP leak through DNS-over-HTTPS (DoH)
- **CRITICAL**: Fixed browser IP leak through QUIC/HTTP3 protocol
- Blocked UDP port 443 (QUIC) and 853 (DNS-over-TLS) to prevent bypasses
- Added aggressive UDP blocking to prevent protocol leaks
- Enhanced iptables rules with stricter OUTPUT filtering

### ✨ New Features
- Added browser configuration warnings on startup
- Enhanced status check with leak testing recommendations
- Added packet counter display in status check
- Better iptables rules verification

### 🛠️ Improvements
- Improved iptables rules with comprehensive leak protection
- Better user guidance for browser configuration
- Added clear warnings about root vs regular user testing

### ⚠️ Breaking Changes
- None - fully backward compatible

---

## [1.0.0] - 2025-12-12

### 🎉 Initial Release

#### Features
- ✅ Transparent Tor proxy for all system traffic
- ✅ MAC address spoofing with 10 vendor profiles
- ✅ Automated setup and configuration
- ✅ IPv6 leak protection
- ✅ DNS leak protection
- ✅ Easy identity changes (new Tor circuits)
- ✅ Both systemwide and local execution modes
- ✅ Comprehensive error handling
- ✅ Clean uninstall functionality

#### Fixed Issues (from original archtorify)
- ✅ Fixed `Type=symple` typo in systemd service
- ✅ Removed conflicting `User tor` directive
- ✅ Proper DNSPort 53 permissions with setcap
- ✅ Optimized service file without restrictive hardening
- ✅ Correct directory ownership for root execution

---

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.1.2 | 2025-12-19 | **Auto iptables backend detection**, fixed nftables compatibility |
| 1.1.1 | 2025-12-19 | Auto module loading, auto-updates |
| 1.1.0 | 2025-12-12 | DoH/QUIC leak fixes |
| 1.0.0 | 2025-12-12 | Initial release |

---

## Upgrade Paths

### 1.1.1 → 1.1.2 (Recommended for all users)
**Critical fix for "Table does not exist" errors**

```bash
cd ~/t0rpoiz0n
cp ~/Downloads/t0rpoiz0n.py ./t0rpoiz0n.py
sudo cp ./t0rpoiz0n.py /usr/local/bin/t0rpoiz0n
sudo chmod +x /usr/local/bin/t0rpoiz0n
```

### 1.1.0 → 1.1.2
```bash
cd ~/t0rpoiz0n
git pull
sudo ./run --install
```

### 1.0.0 → 1.1.2
```bash
cd ~/t0rpoiz0n
git pull
sudo ./run --install
```

---

## Known Issues

### All Versions
- Firefox/Chrome require manual DoH/QUIC disabling for maximum security
- **Recommended**: Use Tor Browser instead of regular browsers
- Root user traffic bypasses Tor (by design, cannot be fixed)

### Version-Specific

**v1.1.1 and earlier:**
- ❌ "Table does not exist" errors on nftables-only kernels → **FIXED in v1.1.2**

---

## Future Roadmap

### v1.3.0 (Planned)
- [ ] Automatic browser configuration
- [ ] Bridge support for censored regions
- [ ] GUI interface
- [ ] Multi-distro support

### v2.0.0 (Planned)
- [ ] Whonix-style isolation
- [ ] Container support
- [ ] Network-wide transparent proxy
- [ ] Native nftables rules

---

**Stay Anonymous, Stay Safe** 🛡️
