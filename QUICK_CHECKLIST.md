# ✅ Quick Action Checklist
## Do This Exactly - Step by Step

### 🚀 SETUP PHASE
- [ ] Open Terminal on Mac (`Cmd + Space` → "Terminal")
- [ ] Navigate to project: `cd "/Users/bebs/Downloads/DAT 505 assignment"`
- [ ] Install packages: `pip3 install -r requirements.txt`
- [ ] Test setup: `python3 test_suite.py`

### 🖥️ VIRTUAL MACHINES (If not done)
- [ ] Download VirtualBox
- [ ] Download Kali Linux, Ubuntu Desktop, Ubuntu Server ISOs
- [ ] Create 3 VMs with "Internal Network" = "lab-network"
- [ ] Set IP addresses:
  - Attacker (Kali): 192.168.1.100
  - Victim (Ubuntu): 192.168.1.10  
  - Gateway (Server): 192.168.1.1

### 🧪 NETWORK TEST
- [ ] From Attacker VM: `ping 192.168.1.10`
- [ ] From Attacker VM: `ping 192.168.1.1`
- [ ] Both should work!

### ⚡ RUN ASSIGNMENT  
- [ ] Copy project files to Attacker VM (Kali Linux)
- [ ] On Attacker VM: `chmod +x scripts/*.py demo.py`
- [ ] Run demo: `sudo python3 demo.py`
- [ ] Follow the interactive prompts

### 📸 TAKE SCREENSHOTS
- [ ] **Before**: ARP table on Victim (`arp -a`)
- [ ] **During**: ARP table showing attacker MAC  
- [ ] **DNS Spoof**: Browser showing fake Google page
- [ ] **Wireshark**: Packet captures with annotations

### 📝 FINISH UP
- [ ] Complete `report_template.md`
- [ ] Include all screenshots
- [ ] Submit project files

---

## 🆘 IF SOMETHING BREAKS:
1. **Copy the exact error message**
2. **Check BROWSER_WALKTHROUGH.md for detailed help**
3. **Most common fix: add `sudo` before commands**

## 🎯 YOU'RE DONE WHEN:
- ARP spoofing changes victim's network routing
- DNS spoofing shows fake websites  
- You have packet captures proving it worked
- Report is complete with evidence

**Ready? Start with the BROWSER_WALKTHROUGH.md file!** 🚀
