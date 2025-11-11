# Complete Beginner's Guide: ARP Spoofing & DNS MitM Assignment

## 🎯 What You're About to Do

You're going to learn about **network attacks** used by hackers to intercept internet traffic. This is for educational purposes in a **safe, controlled environment** to understand cybersecurity better.

### What These Attacks Do:
- **ARP Spoofing**: Tricks devices into sending their internet traffic through your computer
- **DNS Spoofing**: Redirects websites to fake pages you control
- **Traffic Interception**: Captures and analyzes the data flowing through your computer

**⚠️ IMPORTANT**: This is only for educational use in isolated lab environments. Using these techniques on real networks without permission is illegal!

---

## 📋 Step 1: Understanding What You Need

### Required Equipment:
1. **A computer** (Windows, Mac, or Linux)
2. **Virtualization software** (VMware or VirtualBox - free)
3. **3 Virtual Machines** (VMs - like computers inside your computer)
4. **Internet connection** (to download software)

### What Virtual Machines Are:
Think of VMs as separate computers running inside your real computer. Each VM acts like a completely independent computer with its own operating system.

---

## 🖥️ Step 2: Setting Up Your Virtual Lab

### Download Required Software:

1. **VirtualBox** (Free virtualization software)
   - Go to: https://www.virtualbox.org/
   - Download and install VirtualBox
   - This lets you run multiple "computers" on your one computer

2. **Operating System Images** (ISO files)
   - **Kali Linux**: https://www.kali.org/get-kali/ (For the attacker)
   - **Ubuntu Desktop**: https://ubuntu.com/download/desktop (For the victim)
   - **Ubuntu Server**: https://ubuntu.com/download/server (For the gateway)

### Create Your 3 Virtual Machines:

#### VM #1: Attacker Machine (Kali Linux)
1. Open VirtualBox
2. Click "New" to create a new VM
3. Name: "Attacker-Kali"
4. Type: Linux
5. Version: Debian (64-bit)
6. Memory: 2048 MB (2 GB)
7. Create a virtual hard disk (20 GB)
8. Install Kali Linux from the ISO file
9. **Network Settings**: Internal Network named "lab-network"

#### VM #2: Victim Machine (Ubuntu Desktop)
1. Create new VM
2. Name: "Victim-Ubuntu"
3. Memory: 1024 MB (1 GB)
4. Hard disk: 15 GB
5. Install Ubuntu Desktop
6. **Network Settings**: Internal Network named "lab-network"

#### VM #3: Gateway Machine (Ubuntu Server)
1. Create new VM
2. Name: "Gateway-Server"
3. Memory: 1024 MB (1 GB)
4. Hard disk: 10 GB
5. Install Ubuntu Server
6. **Network Settings**: Internal Network named "lab-network"

### Configure Network Addresses:

Each VM needs a specific IP address:

**Attacker VM (Kali)**: 192.168.1.100
**Victim VM (Ubuntu)**: 192.168.1.10
**Gateway VM (Server)**: 192.168.1.1

#### How to Set IP Addresses:

**On Ubuntu Desktop/Server:**
1. Open terminal
2. Edit network configuration:
   ```bash
   sudo nano /etc/netplan/01-netcfg.yaml
   ```
3. Add this configuration (replace IP as needed):
   ```yaml
   network:
     version: 2
     ethernets:
       enp0s3:
         dhcp4: false
         addresses: [192.168.1.10/24]  # Change last number for each VM
         gateway4: 192.168.1.1
         nameservers:
           addresses: [192.168.1.1, 8.8.8.8]
   ```
4. Apply changes:
   ```bash
   sudo netplan apply
   ```

**On Kali Linux:**
1. Open terminal
2. Edit network interfaces:
   ```bash
   sudo nano /etc/network/interfaces
   ```
3. Add:
   ```
   auto eth0
   iface eth0 inet static
   address 192.168.1.100
   netmask 255.255.255.0
   gateway 192.168.1.1
   ```
4. Restart networking:
   ```bash
   sudo systemctl restart networking
   ```

---

## 📥 Step 3: Installing the Attack Tools

### On the Attacker VM (Kali Linux):

1. **Update the system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python and required tools:**
   ```bash
   sudo apt install python3 python3-pip git -y
   ```

3. **Download the project:**
   ```bash
   git clone [YOUR-GITHUB-REPO-URL]
   cd "DAT 505 assignment"
   ```

4. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Make scripts executable:**
   ```bash
   chmod +x scripts/*.py
   chmod +x *.py
   chmod +x setup_lab.sh
   ```

6. **Run the setup script:**
   ```bash
   sudo ./setup_lab.sh
   ```

---

## 🧪 Step 4: Testing Your Setup

### Test Network Connectivity:

1. **From Attacker VM**, ping the other machines:
   ```bash
   ping 192.168.1.10  # Victim
   ping 192.168.1.1   # Gateway
   ```

2. **From Victim VM**, ping others:
   ```bash
   ping 192.168.1.100 # Attacker
   ping 192.168.1.1   # Gateway
   ```

If pings work, your network is configured correctly!

### Test the Attack Tools:

1. **Test tool syntax** (these should show help messages):
   ```bash
   python3 scripts/arp_spoof.py -h
   python3 scripts/dns_spoof.py -h
   python3 scripts/traffic_interceptor.py -h
   ```

2. **Run the validation tests:**
   ```bash
   python3 test_suite.py
   ```

---

## 🎯 Step 5: Running the Attacks

### Take VM Snapshots First!
Before running attacks, take snapshots of all VMs so you can restore them if something goes wrong:
1. In VirtualBox, select each VM
2. Go to "Machine" → "Take Snapshot"
3. Give it a name like "Before Attacks"

### Attack #1: ARP Spoofing

**What this does**: Makes the victim's computer think your computer is the internet gateway, so all their traffic goes through you.

**On Attacker VM:**
```bash
sudo python3 scripts/arp_spoof.py -v 192.168.1.10 -g 192.168.1.1 -i eth0 --verbose
```

**What you'll see:**
- The script will show it's "spoofing" the victim and gateway
- Traffic from the victim will now flow through your attacker machine

**To verify it's working:**
1. On Victim VM, check ARP table:
   ```bash
   arp -a
   ```
2. The gateway (192.168.1.1) should show the attacker's MAC address instead of the real gateway's MAC

### Attack #2: Traffic Interception

**What this does**: Captures and analyzes all network traffic flowing through your computer.

**On Attacker VM** (new terminal window):
```bash
sudo python3 scripts/traffic_interceptor.py -i eth0 -o pcap_files/attack_capture.pcap --duration 300 --verbose
```

**Generate traffic on Victim VM:**
```bash
# Browse some websites
curl http://httpbin.org/get
wget http://example.com
dig google.com
```

**What you'll see:**
- The attacker captures all HTTP requests, DNS queries, and other traffic
- Files are saved showing URLs visited, DNS lookups, etc.

### Attack #3: DNS Spoofing

**What this does**: When the victim tries to visit certain websites, redirect them to your fake website instead.

**Step 1 - Start fake web server** (Attacker VM, new terminal):
```bash
sudo python3 scripts/fake_web_server.py -p 80
```

**Step 2 - Start DNS spoofing** (Attacker VM, another new terminal):
```bash
sudo python3 scripts/dns_spoof.py -i eth0 -c config/dns_targets.json --verbose
```

**Step 3 - Test from Victim VM:**
```bash
# Try to visit Google - it should redirect to your fake server!
curl http://google.com
```

**In a web browser on Victim VM:**
- Try visiting facebook.com, google.com, or github.com
- Instead of the real sites, you'll see your fake "hacked" page!

---

## 📸 Step 6: Collecting Evidence

### Screenshots You Need:

1. **Before Attack - Victim's ARP table:**
   ```bash
   arp -a
   ```
   Take screenshot showing real gateway MAC

2. **During Attack - Victim's ARP table:**
   ```bash
   arp -a
   ```
   Take screenshot showing attacker's MAC as gateway

3. **DNS Spoofing Success:**
   - Screenshot of victim's browser showing your fake page instead of real website

4. **Wireshark Analysis:**
   - Open the PCAP files in Wireshark
   - Take screenshots showing captured HTTP requests, DNS queries, ARP packets

### Log Files Generated:
- `pcap_files/*.pcap` - Network traffic captures
- `*_dns_queries.csv` - DNS lookups captured
- `*_http_requests.csv` - Web requests captured
- `dns_spoof_log_*.json` - DNS spoofing activity

---

## 📝 Step 7: Writing Your Report

Use the provided template (`report_template.md`) and fill in:

### Lab Setup Section:
- Describe your 3 VMs and their IP addresses
- Explain the isolated network you created
- Include screenshots of your VM setup

### Implementation Section:
- Explain what each attack tool does
- Show the commands you used
- Describe how the attacks work technically

### Results Section:
- Include all your screenshots
- Show the captured network traffic
- Demonstrate that the attacks worked

### Mitigation Section:
- Explain how to defend against these attacks
- Discuss security measures like DNSSEC, HSTS, ARP monitoring

### Ethics Section:
- Explain why you only used this in a controlled lab
- Discuss the legal and ethical implications
- Emphasize this is for educational purposes only

---

## 🚨 Important Safety Reminders

### What You Must NOT Do:
- ❌ **Never run these tools on your school/work network**
- ❌ **Never attack networks you don't own**
- ❌ **Never use this to actually harm or spy on people**
- ❌ **Never share these tools with people who might misuse them**

### What You SHOULD Do:
- ✅ **Only use in your isolated virtual lab**
- ✅ **Take VM snapshots before experimenting**
- ✅ **Keep detailed logs of everything you do**
- ✅ **Restore VMs to clean state when done**
- ✅ **Use this knowledge to better secure networks**

---

## 🔧 Troubleshooting Common Problems

### "Permission denied" errors:
- Solution: Run commands with `sudo`
- Example: `sudo python3 scripts/arp_spoof.py ...`

### "No such file or directory":
- Check you're in the right directory: `cd "DAT 505 assignment"`
- Make sure scripts are executable: `chmod +x scripts/*.py`

### Network interfaces not found:
- Check interface name: `ip addr show`
- Use the correct interface (usually `eth0` or `enp0s3`)

### VMs can't communicate:
- Verify all VMs are on "Internal Network" named "lab-network"
- Check IP addresses are configured correctly
- Test with `ping` commands

### ARP spoofing not working:
- Make sure IP forwarding is enabled: `sudo sysctl -w net.ipv4.ip_forward=1`
- Check you're using the correct IP addresses
- Verify the victim is generating network traffic

### DNS spoofing not redirecting:
- Clear DNS cache on victim: `sudo systemctl flush-dns`
- Make sure fake web server is running
- Check DNS targets configuration file

---

## 🎓 What You're Learning

This assignment teaches you:

1. **How network protocols work** (ARP, DNS, HTTP)
2. **How attackers exploit protocol weaknesses**
3. **How to detect and prevent these attacks**
4. **The importance of network security**
5. **Ethical hacking and responsible disclosure**

### Career Applications:
- **Cybersecurity Analyst**: Understanding attack methods to defend against them
- **Penetration Tester**: Legally testing network security for companies
- **Network Administrator**: Securing networks against these attacks
- **Security Researcher**: Finding and fixing security vulnerabilities

---

## 📞 Getting Help

If you're stuck:

1. **Check the error messages** - they often tell you what's wrong
2. **Review this guide** - make sure you followed each step
3. **Check your network configuration** - most problems are networking issues
4. **Look at the log files** - they show what the tools are doing
5. **Ask your instructor** - they can help with assignment-specific questions

Remember: Learning cybersecurity takes practice. Don't get discouraged if it doesn't work perfectly the first time!

---

## 🏆 Success Checklist

You've succeeded when you can:

- ✅ Set up 3 VMs that can communicate with each other
- ✅ Run ARP spoofing and see the victim's ARP table change
- ✅ Capture network traffic flowing through your attacker machine
- ✅ Redirect DNS queries to your fake web server
- ✅ Take screenshots proving all attacks worked
- ✅ Generate analysis files (PCAP, CSV, JSON)
- ✅ Write a complete report explaining everything

**Congratulations!** You've just learned fundamental network security concepts that cybersecurity professionals use every day! 🎉
