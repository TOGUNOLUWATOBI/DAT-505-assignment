#  Quick Start Checklist for Complete Beginners

##  What Am I Doing?
You're learning how hackers intercept internet traffic - but safely, in a controlled environment for educational purposes only.

##  Setup Checklist (Do This First!)

### Phase 1: Get the Software (30 minutes)
- [ ] Download VirtualBox from https://www.virtualbox.org/
- [ ] Download Kali Linux from https://www.kali.org/get-kali/
- [ ] Download Ubuntu Desktop from https://ubuntu.com/download/desktop
- [ ] Download Ubuntu Server from https://ubuntu.com/download/server

### Phase 2: Create Virtual Machines (60 minutes)
- [ ] Create VM #1: "Attacker-Kali" (2GB RAM, 20GB disk)
- [ ] Create VM #2: "Victim-Ubuntu" (1GB RAM, 15GB disk)  
- [ ] Create VM #3: "Gateway-Server" (1GB RAM, 10GB disk)
- [ ] Set all VMs to "Internal Network" named "lab-network"

### Phase 3: Configure Network (20 minutes)
- [ ] Set Attacker IP: 192.168.1.100
- [ ] Set Victim IP: 192.168.1.10
- [ ] Set Gateway IP: 192.168.1.1
- [ ] Test: All VMs can ping each other

### Phase 4: Install Attack Tools (15 minutes)
- [ ] On Attacker VM: Download this project
- [ ] Run: `pip3 install -r requirements.txt`
- [ ] Run: `chmod +x scripts/*.py`
- [ ] Test: `python3 scripts/arp_spoof.py -h` shows help

##  Running Attacks (The Fun Part!)

### Attack 1: ARP Spoofing (Make traffic go through you)
```bash
# On Attacker VM:
sudo python3 scripts/arp_spoof.py -v 192.168.1.10 -g 192.168.1.1 -i eth0 --verbose

# On Victim VM (to verify):
arp -a    # Should show attacker's MAC for gateway
```

### Attack 2: Capture Traffic (See what victim is doing)
```bash
# On Attacker VM (new terminal):
sudo python3 scripts/traffic_interceptor.py -i eth0 -o capture.pcap --duration 300 --verbose

# On Victim VM (generate traffic):
curl http://example.com
wget http://httpbin.org/get
```

### Attack 3: DNS Spoofing (Redirect websites to fake pages)
```bash
# On Attacker VM (terminal 1):
sudo python3 scripts/fake_web_server.py -p 80

# On Attacker VM (terminal 2):
sudo python3 scripts/dns_spoof.py -i eth0 -c config/dns_targets.json --verbose

# On Victim VM (test):
curl http://google.com    # Should show fake page!
```

##  Evidence to Collect

### Screenshots Needed:
1. **Before attack**: Victim's ARP table (`arp -a`)
2. **During attack**: Victim's ARP table (shows attacker's MAC)
3. **DNS spoofing**: Browser showing fake page instead of real website
4. **Wireshark**: Network traffic analysis

### Files Generated:
- `pcap_files/*.pcap` - Network captures
- `*_dns_queries.csv` - DNS lookups
- `*_http_requests.csv` - Web requests
- Various `.json` log files

##  Emergency Troubleshooting

### Nothing Works?
1. **Check you're in the right directory**: `cd "DAT 505 assignment"`
2. **Use sudo for attacks**: All attack commands need `sudo`
3. **Check network setup**: All VMs should ping each other
4. **Restart VMs**: Sometimes a reboot fixes everything

### Common Error Fixes:
- **"Permission denied"**  Use `sudo`
- **"Interface not found"**  Use `ip addr` to find correct interface name
- **"No such file"**  Check you're in project directory
- **VMs can't talk**  Verify all on "Internal Network" named "lab-network"

##  Success Indicators

### You Know It's Working When:
-  Victim's ARP table shows your MAC address for the gateway
-  Traffic capture shows HTTP requests from victim
-  DNS spoofing redirects victim to your fake website
-  You have screenshots and PCAP files as evidence

##  Safety Rules (READ THIS!)

### NEVER DO:
-  Run on real networks (school, work, home WiFi)
-  Attack networks you don't own
-  Use this to spy on real people

### ALWAYS DO:
-  Only use in your isolated VMs
-  Take VM snapshots before testing
-  Keep everything in virtual lab environment

##  Quick Report Template

Your report needs:
1. **Lab setup**: Describe your 3 VMs and network
2. **Attack results**: Show screenshots proving attacks worked
3. **Technical analysis**: Explain how the attacks work
4. **Defense strategies**: How to prevent these attacks
5. **Ethics section**: Why you only used this in a safe lab

##  Time Estimates

- **Initial setup**: 2-3 hours (first time)
- **Running attacks**: 30 minutes
- **Collecting evidence**: 30 minutes
- **Writing report**: 2-3 hours
- **Total**: 5-7 hours

##  What You're Actually Learning

This isn't just "hacking" - you're learning:
- How network protocols (ARP, DNS) work
- How attackers exploit protocol weaknesses
- How to defend against real-world attacks
- Professional cybersecurity skills

**This knowledge helps you PROTECT networks, not attack them!**

---

##  Still Confused? Start Here:

### If you've never used Linux before:
1. Start with just setting up one Ubuntu VM
2. Learn basic commands: `ls`, `cd`, `ping`, `sudo`
3. Get comfortable with the terminal
4. Then move to the full lab setup

### If VMs seem complicated:
1. Watch VirtualBox tutorials on YouTube
2. Practice creating and deleting test VMs
3. Learn how to take snapshots
4. Understand internal networking

### If networking confuses you:
1. Learn what IP addresses are (like house addresses for computers)
2. Understand that 192.168.1.x is a private network range
3. Know that ping tests if computers can talk to each other
4. ARP = how computers find each other on local networks

**Remember**: Everyone was a beginner once. Take it step by step! 
