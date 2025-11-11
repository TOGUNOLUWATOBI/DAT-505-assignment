# DAT 505 Assignment Checklist

## Pre-Assignment Setup 

### Lab Environment
- [ ] Three VMs configured (Attacker, Victim, Gateway)
- [ ] Isolated virtual network created (192.168.1.0/24)
- [ ] VM snapshots taken before testing
- [ ] Network managers disabled on all VMs
- [ ] IP forwarding configured on attacker VM

### Software Installation
- [ ] Python 3.6+ installed on attacker VM
- [ ] Scapy library installed (`pip3 install scapy`)
- [ ] Wireshark/tcpdump installed for packet capture
- [ ] All project dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Scripts have execute permissions (`chmod +x scripts/*.py`)

### Initial Testing
- [ ] Test suite runs successfully (`python3 test_suite.py`)
- [ ] Network connectivity verified between VMs
- [ ] Basic packet crafting works (Scapy import test)

## Task 1: ARP Spoofing Tool 

### Implementation Requirements
- [x] Command-line arguments (victim IP, gateway IP, interface)
- [x] Enable/disable IP forwarding functionality
- [x] Graceful restore on exit (Ctrl+C handling)
- [x] Verbose mode for detailed logging
- [x] Bidirectional ARP spoofing (victim  gateway)

### Testing & Evidence Collection
- [ ] Screenshot of ARP table before spoofing attack
- [ ] Screenshot of ARP table after spoofing attack
- [ ] PCAP file showing ARP spoofing packets
- [ ] tcpdump output demonstrating traffic flow through attacker
- [ ] Verification that victim traffic routes through attacker

### Commands to Run
```bash
# Before attack - on victim VM
arp -a

# Start ARP spoofing - on attacker VM
sudo python3 scripts/arp_spoof.py -v 192.168.1.10 -g 192.168.1.1 -i eth0 --verbose

# During attack - on victim VM
arp -a
ping 8.8.8.8

# Capture traffic - on attacker VM
sudo tcpdump -i eth0 -w evidence/arp_spoofing.pcap
```

## Task 2: Traffic Capture & Analysis 

### Implementation Requirements
- [x] Sniff and save PCAPs for common protocols (HTTP, DNS, SSH, FTP)
- [x] Parser to extract visited URLs
- [x] Parser to extract DNS queries
- [x] Top talkers identification
- [x] Protocol count statistics

### Testing & Evidence Collection
- [ ] PCAP files captured during MitM attack
- [ ] CSV extract of visited URLs
- [ ] CSV extract of DNS queries
- [ ] Text summary of protocol statistics
- [ ] Two Wireshark screenshots with annotations

### Commands to Run
```bash
# Start traffic capture - on attacker VM
sudo python3 scripts/traffic_interceptor.py -i eth0 -o pcap_files/mitm_capture.pcap --duration 300 --verbose

# Generate traffic - on victim VM
curl http://example.com
dig google.com
wget http://httpbin.org/get
```

## Task 3: DNS Spoofing 

### Implementation Requirements
- [x] Correct transaction ID and flags in DNS responses
- [x] Selective spoof list (whitelist/blacklist configuration)
- [x] Optional forwarding of non-targeted queries
- [x] Configuration file for target domains

### Supporting Components
- [x] Small fake web server to show redirection
- [x] Web server logging functionality
- [x] DNS spoofing statistics and logging

### Testing & Evidence Collection
- [ ] Configuration file with target domains
- [ ] PCAP showing spoofed DNS response
- [ ] Browser screenshot showing redirection to fake page
- [ ] Web server logs showing victim access
- [ ] Before/after DNS resolution comparison

### Commands to Run
```bash
# Start fake web server - on attacker VM
sudo python3 scripts/fake_web_server.py -p 80

# Start DNS spoofing - on attacker VM (new terminal)
sudo python3 scripts/dns_spoof.py -i eth0 -c config/dns_targets.json --verbose

# Test DNS resolution - on victim VM
dig google.com
nslookup facebook.com
curl http://github.com
```

## Task 4: SSLStrip Demo (Optional) 

### Implementation Requirements
- [x] iptables redirection of HTTP/HTTPS traffic
- [x] Local proxy implementation (Flask-based)
- [x] Log downgraded connections
- [x] Observe rewritten redirects

### Testing & Evidence Collection
- [ ] PCAP evidence of HTTPSHTTP downgrade
- [ ] Comparison of traffic before/after SSLStrip
- [ ] Discussion of HSTS and modern mitigations
- [ ] Explanation of limited effectiveness

### Commands to Run
```bash
# Start SSLStrip demo - on attacker VM
sudo python3 scripts/sslstrip_demo.py -i eth0 -p 8080 --verbose

# Test HTTPS sites - on victim VM
curl -v https://example.com
curl -v https://httpbin.org/get
```

## Submission Requirements 

### GitHub Repository
- [x] All scripts (arp_spoof.py, traffic_interceptor.py, dns_spoof.py, sslstrip_demo.py)
- [x] README.md with project documentation
- [x] requirements.txt with Python dependencies
- [ ] Repository created and files uploaded

### Evidence Collection
- [ ] pcap_files/ directory with labeled captures
- [ ] evidence/ folder with screenshots and log files
- [ ] All PCAP files properly named and organized
- [ ] Screenshots have clear annotations

### Report (4-8 pages PDF)
- [ ] Setup summary with VM configurations
- [ ] Methodology explaining approach
- [ ] Results section with evidence
- [ ] Mitigation ideas and recommendations
- [ ] Ethics section discussing legal/ethical considerations

## Evidence Checklist

### Screenshots Required
- [ ] ARP table before spoofing (victim VM)
- [ ] ARP table after spoofing (victim VM)
- [ ] Wireshark capture showing ARP packets
- [ ] Wireshark capture showing intercepted traffic (annotated)
- [ ] DNS resolution before spoofing
- [ ] DNS resolution during spoofing
- [ ] Browser showing spoofed/redirected page
- [ ] Fake web server access logs
- [ ] SSLStrip demonstration (if implemented)

### PCAP Files Required
- [ ] ARP spoofing traffic capture
- [ ] HTTP/HTTPS traffic during MitM
- [ ] DNS spoofing packets
- [ ] Complete MitM session capture
- [ ] SSLStrip traffic (if implemented)

### Log Files Required
- [ ] DNS spoofing logs (JSON format)
- [ ] Web server access logs
- [ ] Traffic analysis summaries (CSV/JSON)
- [ ] Tool execution logs with timestamps

## Final Submission Steps

### Organization
- [ ] All files organized in proper directory structure
- [ ] Evidence files have descriptive names
- [ ] PCAP files are properly labeled
- [ ] Screenshots include timestamps and annotations

### Quality Assurance
- [ ] All scripts run without errors
- [ ] Test suite passes completely
- [ ] Evidence clearly demonstrates attack success
- [ ] Report is well-structured and complete

### Ethical Compliance
- [ ] All testing done in isolated lab environment
- [ ] No unauthorized network access
- [ ] Ethics section completed in report
- [ ] Mitigation strategies properly documented

### Upload Checklist
- [ ] GitHub repository created
- [ ] All code files committed and pushed
- [ ] Evidence files uploaded (or linked if too large)
- [ ] PDF report generated and included
- [ ] Assignment submission completed

## Emergency Troubleshooting

### Common Issues
- **Permission denied**: Run with `sudo` for packet crafting
- **Network interface not found**: Check interface name with `ip addr`
- **ARP spoofing not working**: Verify IP forwarding enabled
- **DNS spoofing ineffective**: Clear DNS cache, check configuration
- **Import errors**: Install dependencies with `pip3 install -r requirements.txt`

### Quick Fixes
```bash
# Fix permissions
sudo chmod +x scripts/*.py

# Install dependencies
pip3 install -r requirements.txt

# Check network interfaces
ip addr show

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Clear DNS cache (victim)
sudo systemctl flush-dns
```

### Contact Information
- Course: DAT 505
- Assignment: ARP Spoofing & DNS MitM with Scapy
- Due Date: 11 Nov by 23:59
- Submission: PDF report + GitHub repository
