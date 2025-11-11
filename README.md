# ARP Spoofing & DNS MitM with Scapy

This project implements ARP spoofing and DNS man-in-the-middle attacks using Python and Scapy for educational purposes in an isolated lab environment.

## Project Structure

```
 scripts/
    arp_spoof.py          # ARP spoofing tool
    traffic_interceptor.py # Traffic capture and analysis
    dns_spoof.py          # DNS spoofing tool
    sslstrip_demo.py      # Optional SSLStrip demonstration
 pcap_files/               # Captured network traffic
 evidence/                 # Screenshots and logs
 config/                   # Configuration files
 requirements.txt          # Python dependencies
 README.md                 # This file

## Prerequisites

- Python 3.6+
- Scapy library
- Root/sudo privileges for packet crafting
- Virtual lab environment with 3 VMs:
  - Attacker VM (Kali/Ubuntu)
  - Victim VM (Ubuntu/Windows)
  - Gateway/Server VM (Ubuntu)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Task 1: ARP Spoofing

```bash
sudo python3 scripts/arp_spoof.py -v 192.168.1.10 -g 192.168.1.1 -i eth0 --verbose
```

### Task 2: Traffic Capture & Analysis

```bash
sudo python3 scripts/traffic_interceptor.py -i eth0 -o capture.pcap --duration 300
```

### Task 3: DNS Spoofing

```bash
sudo python3 scripts/dns_spoof.py -i eth0 -c config/dns_targets.json --verbose
```

### Optional Task 4: SSLStrip Demo

```bash
sudo python3 scripts/sslstrip_demo.py -i eth0 -p 8080
```

## Safety Notice

**WARNING**: This project is for educational purposes only. Only use in isolated lab environments you control. Unauthorized network attacks are illegal and unethical.

## Lab Setup

1. Create isolated virtual network
2. Configure three VMs with limited resources (1-2 vCPU, 1-2 GB RAM)
3. Disable automatic network managers
4. Take VM snapshots before experiments
5. Keep all traffic confined to virtual network

## Evidence Collection

- Capture traffic with tcpdump/Wireshark
- Store pcaps in `pcap_files/` directory
- Save screenshots in `evidence/` folder
- Maintain clear logs for reproducibility
