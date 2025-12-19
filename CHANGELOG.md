# Changelog

All notable changes to t0rpoiz0n will be documented in this file.

## [1.1.1] - 2025-12-19

### 🔧 Bug Fixes
- **CRITICAL**: Fixed "iptables: Table does not exist" error on modern Arch systems
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
- Updated troubleshooting section in README
- Auto-update system integrated into run script
- Update checks run silently in background (no slowdown)
- Stores last check timestamp to avoid redundant checks
- Detects repository location automatically
- `--no-update-check` flag to skip updates when needed

### 📝 Documentation
- Added iptables module troubleshooting section
- Updated architecture diagram to show module loader and auto-updater
- Added "What's New in v1.1.1" section
- Enhanced comparison table with iptables auto-loading
- Added comprehensive Auto-Update section
- Documented update check behavior and timing
- Added `--no-update-check` flag documentation

### ⚠️ Breaking Changes
- None - fully backward compatible

### 🔄 Migration Notes

If you already have v1.1.0 installed and are experiencing iptables errors:

```bash
cd ~/t0rpoiz0n
git pull
sudo ./run --install  # Reinstall to update
sudo t0rpoiz0n -k     # Stop old version
sudo t0rpoiz0n -s     # Start with new auto-loading
```

If you're installing fresh, no special steps needed - it just works!

### 🐛 Bug Context

**The Problem:**
Modern Arch Linux systems use nftables by default. When iptables commands run without the legacy iptables kernel modules loaded, they fail with:
```
iptables v1.8.11 (legacy): can't initialize iptables table `filter': Table does not exist
```

**The Solution:**
v1.1.1 automatically detects and loads the required kernel modules:
- `iptable_filter` - For filtering rules
- `iptable_nat` - For NAT/redirection rules
- `iptable_mangle` - For packet manipulation
- `ip_tables` - Base iptables support

The tool also creates `/etc/modules-load.d/iptables.conf` so these modules load automatically on every boot.

### 🔄 Auto-Update System

**How It Works:**
The run script now includes an intelligent auto-update checker that:
1. **Checks GitHub API** for the latest release/tag
2. **Compares versions** using semantic versioning
3. **Prompts user** if newer version available
4. **Auto-updates** with one keypress (pulls from git and reinstalls)
5. **Caches check time** to avoid checking every single run

**Update Timing:**
- Checks for updates once every 24 hours
- Stores last check timestamp in `/etc/t0rpoiz0n/.last_update_check`
- Silently skips if checked within last 24h (no slowdown)
- Can be manually skipped with `--no-update-check` flag

**Smart Detection:**
- Automatically finds repository location (current dir, /opt, ~/t0rpoiz0n, etc.)
- Saves repo path to `/etc/t0rpoiz0n/.repo_path` for future use
- Works for both systemwide and local installations
- Gracefully handles no internet connection

**User Experience:**
```bash
$ sudo t0rpoiz0n -s
[*] Checking for updates...

╔════════════════════════════════════════════════════════════╗
║              NEW VERSION AVAILABLE!                        ║
╚════════════════════════════════════════════════════════════╝

Current version: 1.1.0
Latest version:  1.1.1

Would you like to update now? [y/N]: y

[*] Fetching latest changes from GitHub...
[*] Pulling latest version...
[✓] Repository updated
[✓] Systemwide installation updated

╔════════════════════════════════════════════════════════════╗
║                  UPDATE COMPLETED!                         ║
╚════════════════════════════════════════════════════════════╝
```

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
- Enhanced documentation about leak prevention

### 📝 Documentation
- Added browser configuration requirements to startup output
- Updated status check with testing instructions
- Added changelog file

### ⚠️ Breaking Changes
- None - fully backward compatible

### 🔄 Migration Notes
If you already have v1.0.0 installed:

```bash
cd ~/t0rpoiz0n
git pull
sudo ./run --install  # Reinstall to update
sudo t0rpoiz0n -k     # Stop old version
sudo t0rpoiz0n -s     # Start with new rules
```

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

#### Supported Platforms
- Arch Linux (primary)
- Arch-based distributions (Manjaro, EndeavourOS, etc.)

#### MAC Vendor Profiles
- Samsung, Apple, Huawei, Nokia, Google
- Dell, HP, ASUS, Lenovo, Motorola

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version: Incompatible API changes
- MINOR version: New functionality (backward compatible)
- PATCH version: Bug fixes (backward compatible)

---

## Upgrade Guide

### From 1.1.0 to 1.1.1

**What's Changed:**
- Automatic iptables module loading (fixes "Table does not exist" error)
- Persistent module configuration for boot
- Better error messages
- No configuration changes needed

**How to Upgrade:**

```bash
# 1. Stop current instance
sudo t0rpoiz0n -k

# 2. Update from GitHub
cd ~/t0rpoiz0n
git pull

# 3. Reinstall
sudo ./run --install

# 4. Start with new version
sudo t0rpoiz0n -s
```

**Post-Upgrade Verification:**

```bash
# Verify modules are loaded
lsmod | grep iptable

# Test as regular user (NOT root)
curl https://check.torproject.org/api/ip

# Should show IsTor: true
```

### From 1.0.0 to 1.1.0

**What's Changed:**
- Enhanced iptables rules for better leak protection
- New browser warnings on startup
- No configuration changes needed

**How to Upgrade:**

```bash
# 1. Stop current instance
sudo t0rpoiz0n -k

# 2. Update from GitHub
cd ~/t0rpoiz0n
git pull

# 3. Reinstall
sudo ./run --install

# 4. Start with new version
sudo t0rpoiz0n -s
```

**Post-Upgrade Testing:**

```bash
# Test as regular user (NOT root)
curl https://check.torproject.org/api/ip

# Should show IsTor: true
```

---

## Known Issues

### v1.1.1
- Firefox/Chrome require manual DoH/QUIC disabling for maximum security
- **Recommended**: Use Tor Browser instead of regular browsers
- Root user traffic still bypasses Tor (by design, cannot be fixed)
- On some systems, nftables may conflict with iptables (tool provides guidance)

### v1.1.0
- Firefox/Chrome require manual DoH/QUIC disabling for maximum security
- **Recommended**: Use Tor Browser instead of regular browsers
- Root user traffic still bypasses Tor (by design, cannot be fixed)
- iptables module loading not automatic (FIXED in v1.1.1)

### Reporting Issues

Found a bug? Please report it:
1. Check if already reported: https://github.com/0xb0rn3/t0rpoiz0n/issues
2. Include:
   - Version (`t0rpoiz0n -c` shows version)
   - Operating system
   - Steps to reproduce
   - Error messages
   - Output of `sudo journalctl -u tor-t0rpoiz0n.service -n 50`
   - Output of `lsmod | grep iptable` (for module-related issues)

---

## Future Plans

### Planned for v1.2.0
- [ ] Automatic browser configuration (Firefox profile injection)
- [ ] Bridge support for censored regions
- [ ] Pluggable transports integration
- [ ] GUI interface
- [ ] Support for more Linux distributions
- [ ] Better nftables integration

### Planned for v2.0.0
- [ ] Whonix-style isolation
- [ ] Container support (Docker/Podman)
- [ ] Network-wide transparent proxy (gateway mode)
- [ ] Advanced traffic analysis protection
- [ ] Native nftables support (drop iptables dependency)

---

## Security Advisories

No security advisories at this time.

To receive security notifications:
- Watch the repository on GitHub
- Enable email notifications for security advisories

---

**Stay Anonymous, Stay Safe** 🛡️
