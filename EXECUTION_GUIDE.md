# ARP Spoofing & DNS MitM Assignment Execution Guide

## Overview
This guide provides step-by-step instructions to complete the cybersecurity assignment using the provided tools in an isolated virtual environment.

##  SAFETY FIRST
- Only use these tools in isolated virtual machines
- Never run on production networks
- This is for educational purposes only

## Lab Setup Requirements

### Virtual Machines Needed:
1. **Attacker VM** (Kali Linux recommended)
   - IP: 192.168.1.100
   - Tools: Python3, Scapy, Wireshark, tcpdump
   
2. **Victim VM** (Ubuntu Desktop)
   - IP: 192.168.1.10
   - Tools: Web browser, basic networking tools
   
3. **Gateway/Server VM** (Ubuntu Server)
   - IP: 192.168.1.1
   - Tools: Apache/NGINX, DNS server

### Network Configuration:
- All VMs on internal network "lab-network"
- No internet access (isolated environment)
- Static IP addresses configured

## Step-by-Step Execution

### Phase 1: Environment Setup

#### 1.1 Prepare Attacker VM
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip tcpdump wireshark git -y

# Clone project (or copy files)
cd /home/kali/Desktop
git clone [repository-url] || cp -r "DAT 505 assignment" .
cd "DAT 505 assignment"

# Install Python packages
pip3 install -r requirements.txt

# Make scripts executable
chmod +x scripts/*.py
chmod +x setup_lab.sh

# Run setup script
sudo ./setup_lab.sh
```

#### 1.2 Test Network Connectivity
```bash
# From attacker VM, test connectivity
ping 192.168.1.10  # Victim
ping 192.168.1.1   # Gateway

# Check network interface
ip addr show
# Note: Use correct interface name (eth0, enp0s3, etc.)
```

### Phase 2: Task 1 - ARP Spoofing

#### 2.1 Capture Baseline Evidence
```bash
# On victim VM, capture original ARP table
arp -a > /tmp/arp_before.txt
cat /tmp/arp_before.txt
```

#### 2.2 Execute ARP Spoofing Attack
```bash
# On attacker VM
sudo python3 scripts/arp_spoof.py -v 192.168.1.10 -g 192.168.1.1 -i eth0 --verbose

# Let it run for 30-60 seconds
# Press Ctrl+C to stop gracefully
```

#### 2.3 Verify Attack Success
```bash
# On victim VM, check ARP table during attack
arp -a > /tmp/arp_during.txt
cat /tmp/arp_during.txt

# Compare before and during
diff /tmp/arp_before.txt /tmp/arp_during.txt
```

### Phase 3: Task 2 - Traffic Capture & Analysis

#### 3.1 Start Traffic Capture
```bash
# On attacker VM (new terminal)
sudo python3 scripts/traffic_interceptor.py -i eth0 -o pcap_files/mitm_capture.pcap --duration 300 --verbose
```

#### 3.2 Generate Traffic on Victim
```bash
# On victim VM, generate various traffic types
curl http://httpbin.org/get
wget http://example.com -O /dev/null
dig google.com
nslookup facebook.com
ping 8.8.8.8 -c 5
```

#### 3.3 Analyze Captured Traffic
```bash
# The traffic interceptor automatically generates:
# - pcap_files/mitm_capture.pcap
# - *_dns_queries.csv
# - *_http_requests.csv
# - Analysis summary

# View in Wireshark
wireshark pcap_files/mitm_capture.pcap &
```

### Phase 4: Task 3 - DNS Spoofing

#### 4.1 Configure DNS Targets
```bash
# Edit config/dns_targets.json to set target domains
cat config/dns_targets.json
```

#### 4.2 Start Fake Web Server
```bash
# On attacker VM (new terminal)
sudo python3 scripts/fake_web_server.py -p 80 --verbose

# This serves fake pages for spoofed domains
```

#### 4.3 Execute DNS Spoofing
```bash
# On attacker VM (another terminal)
sudo python3 scripts/dns_spoof.py -i eth0 -c config/dns_targets.json --verbose
```

#### 4.4 Test DNS Redirection
```bash
# On victim VM
# Test DNS resolution
nslookup google.com
dig facebook.com

# Test web redirection
curl http://google.com
curl http://facebook.com

# Or use web browser to visit spoofed sites
firefox http://google.com &
```

### Phase 5: Optional Task 4 - SSLStrip Demo

#### 5.1 Setup Traffic Redirection
```bash
# On attacker VM
sudo python3 scripts/sslstrip_demo.py -i eth0 -p 8080 --verbose

# In another terminal, set up iptables redirection
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8080
```

#### 5.2 Test HTTPS Downgrade
```bash
# On victim VM
curl https://httpbin.org/get
curl https://example.com

# Check if HTTPS is downgraded to HTTP
```

## Evidence Collection

### Required Screenshots:
1. **ARP Tables**: Before/during/after ARP spoofing
2. **Network Topology**: VM network configuration
3. **DNS Spoofing**: Victim browser showing fake pages
4. **Wireshark Analysis**: Captured packets with annotations
5. **Tool Outputs**: Terminal screenshots showing successful attacks

### Required Files:
1. **PCAP Files**: All network captures
2. **Log Files**: Tool outputs and analysis
3. **Configuration**: DNS targets and setup files

### Wireshark Analysis Points:
- ARP poisoning packets
- DNS query/response pairs
- HTTP requests to spoofed domains
- Traffic flow through attacker

## Troubleshooting

### Common Issues:

#### "Permission denied"
```bash
# Solution: Run with sudo
sudo python3 scripts/arp_spoof.py ...
```

#### "No such device"
```bash
# Check interface name
ip addr show
# Use correct interface (eth0, enp0s3, etc.)
```

#### "ARP spoofing not working"
```bash
# Check IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Verify target IPs are correct
ping 192.168.1.10
ping 192.168.1.1
```

#### "DNS spoofing not redirecting"
```bash
# Clear DNS cache on victim
sudo systemctl flush-dns
# or
sudo systemd-resolve --flush-caches

# Verify fake web server is running
curl http://192.168.1.100
```

## Report Structure

### 1. Introduction
- Assignment objectives
- Lab setup description
- Safety considerations

### 2. Implementation
- Tool descriptions
- Technical methodology
- Command sequences used

### 3. Results
- Evidence screenshots
- Traffic analysis
- Attack success metrics

### 4. Analysis
- Wireshark findings
- Protocol behavior
- Attack effectiveness

### 5. Mitigation Strategies
- DNSSEC implementation
- ARP monitoring
- Network segmentation
- HSTS enforcement

### 6. Ethics & Legal Considerations
- Controlled environment usage
- Educational purpose statement
- Legal implications discussion

## Success Criteria

 ARP spoofing changes victim's ARP table
 Traffic flows through attacker (PCAP evidence)
 DNS spoofing redirects domains to fake server
 Comprehensive traffic analysis completed
 All evidence properly documented
 Report covers all required sections

## Timeline

- **Day 1**: Lab setup and network configuration
- **Day 2**: ARP spoofing implementation and testing
- **Day 3**: Traffic capture and DNS spoofing
- **Day 4**: Analysis and documentation
- **Day 5**: Report writing and submission prep

Remember: This assignment is about understanding network security to defend against attacks, not to perform malicious activities!
