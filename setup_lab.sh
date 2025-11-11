#!/bin/bash
# Lab Setup Script
# Sets up the virtual lab environment for ARP spoofing and DNS MitM testing

echo "🔧 ARP Spoofing & DNS MitM Lab Setup"
echo "====================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "📦 Installing required packages..."

# Update package lists
apt update

# Install required packages
apt install -y python3 python3-pip tcpdump wireshark dnsmasq apache2 iptables-persistent

# Install Python packages
pip3 install -r requirements.txt

echo "🌐 Configuring network settings..."

# Enable IP forwarding
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
sysctl -p

# Configure dnsmasq for local DNS (optional)
cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
cat >> /etc/dnsmasq.conf << EOF

# Lab DNS configuration
interface=eth0
dhcp-range=192.168.1.50,192.168.1.150,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
EOF

echo "🔒 Setting up file permissions..."

# Make scripts executable
chmod +x scripts/*.py
chmod +x scripts/fake_web_server.py

# Create directories for evidence collection
mkdir -p pcap_files evidence logs

echo "📝 Creating lab documentation..."

cat > lab_instructions.md << 'EOF'
# Lab Instructions

## VM Setup

### Attacker VM (Kali/Ubuntu)
- IP: 192.168.1.100
- Tools: Python3, Scapy, Wireshark, tcpdump
- Role: Performs ARP spoofing and DNS spoofing

### Victim VM (Ubuntu/Windows)
- IP: 192.168.1.10
- Tools: Web browser, dig, nslookup
- Role: Target of the attacks

### Gateway/Server VM (Ubuntu)
- IP: 192.168.1.1
- Tools: Apache/NGINX, DNS server
- Role: Legitimate gateway and DNS server

## Test Scenarios

### 1. ARP Spoofing Test
```bash
# On Attacker VM
sudo python3 scripts/arp_spoof.py -v 192.168.1.10 -g 192.168.1.1 -i eth0 --verbose

# On Victim VM - check ARP table
arp -a

# On Victim VM - test connectivity
ping 8.8.8.8
```

### 2. Traffic Capture Test
```bash
# On Attacker VM
sudo python3 scripts/traffic_interceptor.py -i eth0 -o pcap_files/mitm_capture.pcap --duration 300 --verbose

# On Victim VM - generate traffic
wget http://example.com
dig google.com
```

### 3. DNS Spoofing Test
```bash
# Start fake web server
sudo python3 scripts/fake_web_server.py -p 80

# Start DNS spoofing
sudo python3 scripts/dns_spoof.py -i eth0 -c config/dns_targets.json --verbose

# On Victim VM - test DNS resolution
dig google.com
nslookup facebook.com
curl http://github.com
```

### 4. SSLStrip Demo (Optional)
```bash
# On Attacker VM
sudo python3 scripts/sslstrip_demo.py -i eth0 -p 8080 --verbose

# On Victim VM - browse HTTPS sites
curl https://example.com
```

## Evidence Collection

1. Take screenshots of ARP tables before/after spoofing
2. Capture network traffic with Wireshark
3. Save browser screenshots showing redirections
4. Export packet captures for analysis
5. Document all steps and observations

## Safety Reminders

- Keep all traffic within isolated virtual network
- Never test on production networks
- Take VM snapshots before experiments
- Restore original ARP tables when done
- Document everything for reproducibility
EOF

echo "✅ Lab setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review lab_instructions.md"
echo "2. Configure your VMs according to the IP scheme"
echo "3. Take VM snapshots before testing"
echo "4. Start with ARP spoofing tests"
echo "5. Document all evidence"
echo ""
echo "⚠️  Remember: Use only in isolated lab environments!"
