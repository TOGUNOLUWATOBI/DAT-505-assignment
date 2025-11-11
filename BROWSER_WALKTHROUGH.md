# Browser Walkthrough Guide
## Step-by-Step Instructions for ARP Spoofing & DNS MitM Assignment

### IMPORTANT: Only do this in your isolated virtual lab!

---

## STEP 1: Open Terminal on Your Mac

**What to do:**
1. Press `Cmd + Space` to open Spotlight
2. Type "Terminal" 
3. Press Enter
4. You should see a terminal window open

---

## STEP 2: Navigate to Project Folder

**What to do:**
1. In the terminal, type exactly this and press Enter:
```bash
cd "/Users/bebs/Downloads/DAT 505 assignment"
```

2. Verify you're in the right place by typing:
```bash
ls
```

3. You should see files like `demo.py`, `README.md`, `scripts/`, etc.

---

## STEP 3: Install Required Software

**What to do:**
1. First, install Python packages by typing:
```bash
pip3 install -r requirements.txt
```

2. Wait for it to finish (may take 1-2 minutes)

3. If you get permission errors, try:
```bash
pip3 install --user -r requirements.txt
```

---

## STEP 4: Test Everything Works

**What to do:**
1. Run the test suite by typing:
```bash
python3 test_suite.py
```

2. Wait for tests to complete
3. You should see green "PASS" messages
4. If you see red "FAIL" messages, let me know what they say

---

## STEP 5: Set Up Virtual Machines (If Not Done Yet)

**If you already have 3 VMs set up, skip to Step 6**

### 5A. Download and Install VirtualBox

1. Download VirtualBox:
   - Go to: https://www.virtualbox.org/
   - Click "Downloads"
   - Download "VirtualBox for macOS hosts"
   - Install the .dmg file (may need to allow in System Preferences  Security)

### 5B. Download Operating System ISOs

First, check your Mac architecture:
```bash
uname -m
```
- If shows `x86_64`  Download AMD64 versions
- If shows `arm64`  Download ARM64 versions

Download these ISO files:

1. Kali Linux ISO:
   - Go to: https://www.kali.org/get-kali/
   - Click "Installer Images" 
   - Choose your architecture (AMD64 or ARM64)
   - Download the .iso file

2. Ubuntu Desktop 24.04.3 LTS:
   - Go to: https://ubuntu.com/download/desktop
   - Choose your architecture
   - Download the .iso file

3. Ubuntu Server 24.04.3 LTS:
   - Go to: https://ubuntu.com/download/server
   - Choose your architecture  
   - Download the .iso file

### 5C. Create Virtual Machine #1: Attacker (Kali Linux)

1. Open VirtualBox
2. Click "New"
3. Fill in details:
   - Name: `Attacker-Kali`
   - Type: `Linux`
   - Version: `Debian (64-bit)`
   - Click "Continue"

4. Set Memory: `2048 MB`  Click "Continue"

5. Hard Disk:
   - Select "Create a virtual hard disk now"  Click "Create"
   - Choose "VDI"  Click "Continue"  
   - Choose "Dynamically allocated"  Click "Continue"
   - Set size: `20.00 GB`  Click "Create"

6. Configure Network (IMPORTANT):
   - Right-click the VM  "Settings"
   - Click "Network" tab
   - Adapter 1:
     - Check "Enable Network Adapter"
     - "Attached to:" select "Internal Network"
     - "Name:" type `lab-network`
   - Click "OK"

7. Install Kali Linux:
   - Right-click VM  "Settings"  "Storage"
   - Click the CD icon  "Choose a disk file"
   - Select your Kali Linux .iso file
   - Click "OK"
   - Start the VM and follow Kali installation

### 5D. Create Virtual Machine #2: Victim (Ubuntu Desktop)

1. Click "New" in VirtualBox
2. Fill in details:
   - Name: `Victim-Ubuntu`
   - Type: `Linux`
   - Version: `Ubuntu (64-bit)`

3. Set Memory: `1024 MB`

4. Hard Disk: Create new VDI, `15.00 GB`

5. Configure Network:
   - Right-click VM  "Settings"  "Network"
   - Adapter 1:
     - Enable Network Adapter 
     - "Attached to:" "Internal Network"
     - "Name:" `lab-network`

6. Install Ubuntu Desktop:
   - Add Ubuntu Desktop .iso to Storage
   - Start VM and install

### 5E. Create Virtual Machine #3: Gateway (Ubuntu Server)

1. Click "New" in VirtualBox
2. Fill in details:
   - Name: `Gateway-Server`
   - Type: `Linux`
   - Version: `Ubuntu (64-bit)`

3. Set Memory: `1024 MB`

4. Hard Disk: Create new VDI, `10.00 GB`

5. Configure Network:
   - Right-click VM  "Settings"  "Network"
   - Adapter 1:
     - Enable Network Adapter 
     - "Attached to:" "Internal Network"
     - "Name:" `lab-network`

6. Install Ubuntu Server:
   - Add Ubuntu Server .iso to Storage
   - Start VM and install

### 5F. Verify All VMs Use Same Network

Double-check each VM:
1. Right-click each VM  "Settings"
2. Go to "Network" tab
3. Confirm:
   - Enable Network Adapter is checked
   - Attached to: shows "Internal Network"
   - Name: shows `lab-network`

All 3 VMs must have identical network settings!

---

## STEP 6: Configure VM Network Addresses

Do this on each VM:

### On Victim VM (Ubuntu Desktop):
1. Open terminal in VM
2. Type:
```bash
sudo nano /etc/netplan/01-netcfg.yaml
```
3. Replace content with:
```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: false
      addresses: [192.168.1.10/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [192.168.1.1, 8.8.8.8]
```
4. Press `Ctrl+X`, then `Y`, then Enter to save
5. Type: `sudo netplan apply`

### On Gateway VM (Ubuntu Server):
1. Same process, but use IP: `192.168.1.1/24`

### On Attacker VM (Kali):
1. Open terminal
2. Type:
```bash
sudo nano /etc/network/interfaces
```
3. Add at the end:
```
auto eth0
iface eth0 inet static
address 192.168.1.100
netmask 255.255.255.0
gateway 192.168.1.1
```
4. Save and type: `sudo systemctl restart networking`

---

## STEP 7: Test Network Connectivity

On Attacker VM (Kali), test if VMs can talk:
1. Type: `ping 192.168.1.10` (should reach Victim)
2. Type: `ping 192.168.1.1` (should reach Gateway)
3. If both work, you're ready!

---

## STEP 8: Copy Project Files to Attacker VM

What to do:
1. Copy the entire "DAT 505 assignment" folder to your Attacker VM
2. You can use USB stick, shared folder, or git clone
3. Make sure all files are on the Kali Linux VM

---

## STEP 9: Run the Assignment Demo

On Attacker VM (Kali Linux):
1. Open terminal
2. Navigate to project folder:
```bash
cd "DAT 505 assignment"
```

3. Make scripts executable:
```bash
chmod +x scripts/*.py
chmod +x demo.py
```

4. Run the interactive demo:
```bash
sudo python3 demo.py
```

5. Follow the prompts! The demo will guide you through each task

---

## STEP 10: Take Screenshots (IMPORTANT!)

During the demo, take these screenshots:

### Before Attack (on Victim VM):
1. Open terminal on Victim VM
2. Type: `arp -a`
3. Take screenshot showing original ARP table

### During ARP Attack (on Victim VM):
1. While ARP spoofing is running on Attacker
2. Type: `arp -a` on Victim VM  
3. Take screenshot showing attacker's MAC address

### DNS Spoofing Success (on Victim VM):
1. Open web browser
2. Try to visit google.com
3. Take screenshot showing fake page instead of real Google

### Wireshark Analysis (on Attacker VM):
1. Open Wireshark
2. Load the PCAP files created
3. Take screenshots showing captured packets

---

## STEP 11: Complete Your Report

What to do:
1. Open the file: `report_template.md`
2. Fill in all sections with your findings
3. Include all your screenshots
4. Explain what you learned

---

## TROUBLESHOOTING

"Permission denied" error:
- Solution: Add `sudo` before the command
- Example: `sudo python3 demo.py`

"No such device eth0":
- Solution: Check interface name with `ip addr show`
- Use the correct name (might be enp0s3, wlan0, etc.)

VMs can't ping each other:
- Check: All VMs use "Internal Network" named "lab-network"
- Check: IP addresses are configured correctly
- Restart: Network services on each VM

Python packages won't install:
- Try: `pip3 install --user -r requirements.txt`
- Or: Install packages one by one

---

## SUCCESS CHECKLIST

You've succeeded when you can:
- All 3 VMs can ping each other
- ARP spoofing changes victim's ARP table  
- DNS spoofing redirects websites to fake pages
- You have PCAP files with captured traffic
- You have screenshots of all attacks working
- You completed the report

---

## SAFETY REMINDERS

- NEVER run these tools on your school/work network
- NEVER attack networks you don't own  
- ONLY use in your isolated virtual lab
- This is for learning cybersecurity defense

---

## WHAT TO DO IF STUCK

1. Read error messages carefully - they tell you what's wrong
2. Check this guide again - make sure you followed each step
3. Try the troubleshooting section
4. Ask for help - copy/paste the exact error message

Remember: Learning cybersecurity takes practice. Don't get discouraged!
