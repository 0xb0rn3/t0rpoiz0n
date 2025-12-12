# Changelog

All notable changes to t0rpoiz0n will be documented in this file.

## [1.1.0] - 2024-12-12

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

## [1.0.0] - 2024-12-12

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

### v1.1.0
- Firefox/Chrome require manual DoH/QUIC disabling for maximum security
- **Recommended**: Use Tor Browser instead of regular browsers
- Root user traffic still bypasses Tor (by design, cannot be fixed)

### Reporting Issues

Found a bug? Please report it:
1. Check if already reported: https://github.com/0xb0rn3/t0rpoiz0n/issues
2. Include:
   - Version (`t0rpoiz0n -c` shows version)
   - Operating system
   - Steps to reproduce
   - Error messages
   - Output of `sudo journalctl -u tor-t0rpoiz0n.service -n 50`

---

## Future Plans

### Planned for v1.2.0
- [ ] Automatic browser configuration (Firefox profile injection)
- [ ] Bridge support for censored regions
- [ ] Pluggable transports integration
- [ ] GUI interface
- [ ] Support for more Linux distributions

### Planned for v2.0.0
- [ ] Whonix-style isolation
- [ ] Container support (Docker/Podman)
- [ ] Network-wide transparent proxy (gateway mode)
- [ ] Advanced traffic analysis protection

---

## Security Advisories

No security advisories at this time.

To receive security notifications:
- Watch the repository on GitHub
- Enable email notifications for security advisories

---

**Stay Anonymous, Stay Safe** 🛡️
