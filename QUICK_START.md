# Quick Start Guide

## Project Overview

This project implements a complete ARP spoofing and DNS man-in-the-middle attack suite for the DAT 505 assignment. All tools are designed for educational use in isolated lab environments.

## Files Created

### Core Scripts
- `scripts/arp_spoof.py` - ARP spoofing tool (Task 1)
- `scripts/traffic_interceptor.py` - Traffic capture and analysis (Task 2)  
- `scripts/dns_spoof.py` - DNS spoofing tool (Task 3)
- `scripts/sslstrip_demo.py` - SSLStrip demonstration (Task 4)
- `scripts/fake_web_server.py` - Fake web server for demos

### Configuration
- `config/dns_targets.json` - DNS spoofing targets
- `requirements.txt` - Python dependencies

### Documentation
- `README.md` - Main project documentation
- `report_template.md` - Report template for submission
- `setup_lab.sh` - Lab setup script
- `demo.py` - Interactive demonstration script

## Quick Usage

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x scripts/*.py setup_lab.sh demo.py
```

### 2. Run Individual Tools

**ARP Spoofing:**
```bash
sudo python3 scripts/arp_spoof.py -v 192.168.1.10 -g 192.168.1.1 -i eth0 --verbose
```

**Traffic Capture:**
```bash
sudo python3 scripts/traffic_interceptor.py -i eth0 -o capture.pcap --duration 300 --verbose
```

**DNS Spoofing:**
```bash
sudo python3 scripts/dns_spoof.py -i eth0 -c config/dns_targets.json --verbose
```

**Fake Web Server:**
```bash
sudo python3 scripts/fake_web_server.py -p 80
```

### 3. Run Complete Demo
```bash
sudo python3 demo.py
```

## Lab Requirements

### VM Configuration
- **Attacker VM:** Kali/Ubuntu with Python3, Scapy, Wireshark
- **Victim VM:** Ubuntu/Windows with browser, network tools
- **Gateway VM:** Ubuntu with Apache, DNS server

### Network Setup
- Isolated virtual network (192.168.1.0/24)
- All VMs on same subnet
- IP forwarding enabled on attacker
- Network managers disabled

## Safety Reminders

⚠️ **CRITICAL:** Only use in isolated lab environments
- Never test on production networks
- Unauthorized attacks are illegal
- Take VM snapshots before testing
- Keep traffic within virtual network

## Evidence Collection

1. **Screenshots needed:**
   - ARP tables before/after spoofing
   - Wireshark captures with annotations
   - Browser showing spoofed pages
   - Tool output and statistics

2. **Files to collect:**
   - PCAP files from captures
   - CSV exports of URLs/DNS queries
   - JSON log files from tools
   - Web server access logs

3. **Documentation:**
   - Command sequences used
   - Network configuration details
   - Attack success rates
   - Mitigation strategies tested

## Report Structure

Use `report_template.md` as basis for your submission. Include:

1. Lab setup details
2. Implementation explanations
3. Testing results with evidence
4. Analysis of attack effectiveness
5. Proposed mitigation strategies
6. Ethics and legal considerations

## Submission Checklist

- [ ] All scripts implemented and tested
- [ ] PCAP files collected and labeled
- [ ] Screenshots captured with annotations
- [ ] Report completed using template
- [ ] GitHub repository created
- [ ] Evidence folder organized
- [ ] Ethics section completed

## Troubleshooting

**Permission denied errors:**
- Ensure running with sudo for packet crafting
- Check script file permissions

**Network interface issues:**
- Verify interface name with `ip addr`
- Ensure interface is up and has IP

**ARP spoofing not working:**
- Check IP forwarding is enabled
- Verify MAC address discovery
- Ensure no network managers interfering

**DNS spoofing not effective:**
- Clear DNS cache on victim
- Check DNS server configuration
- Verify iptables rules if using redirection

## Academic Integrity

This project is for educational purposes to demonstrate security concepts. Students must:
- Complete work individually
- Only test in authorized lab environments  
- Properly cite any external resources used
- Follow university ethical guidelines
- Report any vulnerabilities responsibly
