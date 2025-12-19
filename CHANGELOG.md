# Changelog

All notable changes to t0rpoiz0n will be documented in this file.

## [1.1.3] - 2025-12-19

### 🔧 CRITICAL FIX
- **FIXED**: "RULE_APPEND failed (Invalid argument)" errors with nftables backend
- **FIXED**: IPv6-ICMP blocking incompatibility with iptables-nft
- **FIXED**: Owner matching module incompatibility with nftables

### ✨ Major Improvements
- **Smart Rules Generation**: Automatically creates nftables-compatible or legacy rules based on detected backend
- **Dual Rules System**: Separate rule sets for nft vs legacy backends
- **Native nft Support**: Added direct `nft` commands for IPv6 blocking on nftables systems
- **Intelligent Detection**: Backend detection now triggers appropriate rule generation

### 🛠️ Technical Changes
- Added `USING_NFT_BACKEND` global flag for backend tracking
- Implemented `create_iptables_rules_nft()` for nftables-compatible rules
- Implemented `create_iptables_rules_legacy()` for traditional iptables rules
- Smart rule selection in `create_iptables_rules()` based on detected backend
- Added `apply_ipv6_blocks_nft()` for native nft IPv6 blocking
- Rules now regenerated on each start to match current backend

### 📝 Rule Changes for nftables
**Removed from nft rules (not supported):**
- `-m owner --uid-owner tor` (owner matching module)
- `-p ipv6-icmp` in filter table (handled via native nft)

**Added for nft backend:**
- Direct `nft` commands for IPv6 blocking
- Simplified OUTPUT chain without owner matching

**Retained in legacy rules:**
- Full owner matching support
- ipv6-icmp protocol blocking in iptables

### 🐛 Bug Fixes
- Fixed: RULE_APPEND failures on lines 15, 16, 19 of iptables.rules
- Fixed: "Invalid argument" errors with iptables-nft-restore
- Fixed: IPv6 traffic not properly blocked on nftables systems
- Fixed: Backend detection not triggering appropriate rule format

### ⚡ Performance
- Rules now optimized for each backend type
- No more incompatible module attempts on nftables
- Direct nft commands for better performance on modern systems

### 📋 Compatibility
- ✅ Full compatibility with iptables-nft (modern Arch Linux)
- ✅ Full compatibility with iptables-legacy (traditional systems)
- ✅ Automatic backend selection and rule adaptation
- ✅ Works on mixed systems (both backends installed)

### 🔄 Migration from v1.1.2

**Quick Update (Recommended):**
```bash
cd ~/t0rpoiz0n
# Download new t0rpoiz0n.py
cp ~/Downloads/t0rpoiz0n.py ./t0rpoiz0n.py
sudo cp ./t0rpoiz0n.py /usr/local/bin/t0rpoiz0n
sudo chmod +x /usr/local/bin/t0rpoiz0n

# Regenerate rules for your backend
sudo t0rpoiz0n --setup

# Test
sudo t0rpoiz0n -s
```

**Clean Reinstall:**
```bash
# Use cleanup.sh to remove old version
sudo bash cleanup.sh

# Copy new file
cd ~/t0rpoiz0n
cp ~/Downloads/t0rpoiz0n.py ./t0rpoiz0n.py

# Fresh install
chmod +x t0rpoiz0n.py
sudo ./run --install
```

### ⚠️ Breaking Changes
- None - fully backward compatible
- Rules file format changes are automatic

### 🎯 What This Fixes

**Before v1.1.3:**
```
[✗] Command failed: iptables-nft-restore < /usr/share/t0rpoiz0n/iptables.rules
    Error: iptables-nft-restore v1.8.11 (nf_tables): 
line 15: RULE_APPEND failed (Invalid argument): rule in chain OUTPUT
line 16: RULE_APPEND failed (Invalid argument): rule in chain OUTPUT
line 19: RULE_APPEND failed (Invalid argument): rule in chain OUTPUT
```

**After v1.1.3:**
```
[✓] Using iptables-nft (nftables backend)
[*] Creating nftables-compatible rules...
[✓] iptables rules created
[✓] iptables rules applied using iptables-nft
[✓] IPv6 blocked via nft
[✓] Transparent proxy activated
```

---

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

---

## [1.1.1] - 2025-12-19

### 🔧 Bug Fixes
- **CRITICAL**: Fixed iptables "Table does not exist" error
- **CRITICAL**: Auto-loads iptables kernel modules
- Fixed compatibility with systems using nftables by default
- Added graceful fallback when modules fail to load

### ✨ New Features
- Auto-Update Checker - checks GitHub every 24 hours
- One-Click Updates - prompts and auto-installs new versions
- Smart Update Timing - only checks once per 24 hours

---

## [1.1.0] - 2025-12-12

### 🔒 Security Fixes
- **CRITICAL**: Fixed browser IP leak through DNS-over-HTTPS (DoH)
- **CRITICAL**: Fixed browser IP leak through QUIC/HTTP3 protocol
- Blocked UDP port 443 (QUIC) and 853 (DNS-over-TLS)

---

## [1.0.0] - 2025-12-12

### 🎉 Initial Release
- Transparent Tor proxy for all system traffic
- MAC address spoofing with 10 vendor profiles
- Automated setup and configuration
- IPv6 leak protection
- DNS leak protection

---

## Version Comparison

| Version | Date | Key Fix |
|---------|------|---------|
| 1.1.3 | 2024-12-19 | **nftables rules compatibility** |
| 1.1.2 | 2025-12-19 | Backend detection |
| 1.1.1 | 2025-12-19 | Module loading |
| 1.1.0 | 2025-12-12 | DoH/QUIC leaks |
| 1.0.0 | 2025-12-12 | Initial release |

---

## Upgrade Path

### ALL USERS: Upgrade to v1.1.3 Immediately

This version fixes the critical "RULE_APPEND failed" error that prevents the tool from working on modern Arch Linux with nftables.

```bash
# Quick method
cd ~/t0rpoiz0n
cp ~/Downloads/t0rpoiz0n.py ./t0rpoiz0n.py
sudo cp ./t0rpoiz0n.py /usr/local/bin/t0rpoiz0n
sudo chmod +x /usr/local/bin/t0rpoiz0n
sudo t0rpoiz0n --setup
sudo t0rpoiz0n -s
```

---

**Stay Anonymous, Stay Safe** 🛡️
