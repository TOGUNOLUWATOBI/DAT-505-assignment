#  VirtualBox Setup Guide for Mac
## Detailed Step-by-Step VM Configuration

###  **Goal:** Create 3 isolated VMs that can only talk to each other

---

##  **Before You Start**

### Check Your Mac Architecture:
```bash
uname -m
```
- `x86_64` = Intel Mac  Download **AMD64** versions
- `arm64` = Apple Silicon  Download **ARM64** versions

---

##  **Phase 1: Download Everything**

### 1. Download VirtualBox
1. Go to: https://www.virtualbox.org/wiki/Downloads
2. Click "VirtualBox 7.0.x platform packages"
3. Download "macOS / Intel hosts" or "macOS / Apple Silicon hosts"
4. Install the .dmg file
5. **Important:** Allow VirtualBox in System Preferences  Privacy & Security

### 2. Download Operating Systems

**Kali Linux:**
- URL: https://www.kali.org/get-kali/
- Click "Installer Images"
- Download: `kali-linux-2023.x-installer-amd64.iso` (or arm64)

**Ubuntu Desktop:**
- URL: https://ubuntu.com/download/desktop
- Download: `ubuntu-24.04.3-desktop-amd64.iso` (or arm64)

**Ubuntu Server:**
- URL: https://ubuntu.com/download/server
- Download: `ubuntu-24.04.3-live-server-amd64.iso` (or arm64)

---

##  **Phase 2: Create Virtual Machines**

### VM #1: Attacker (Kali Linux)

**Step 1: Create VM**
1. Open VirtualBox
2. Click **"New"** button (blue icon)
3. **VM Creation Dialog:**
   - Name: `Attacker-Kali`
   - Folder: (default is fine)
   - Type: `Linux`
   - Version: `Debian (64-bit)`
   - Click **"Continue"**

**Step 2: Memory**
- Set: `2048 MB` (2 GB)
- Click **"Continue"**

**Step 3: Hard Disk**
- Select: `Create a virtual hard disk now`
- Click **"Create"**
- Hard disk file type: `VDI (VirtualBox Disk Image)`
- Click **"Continue"**
- Storage: `Dynamically allocated`
- Click **"Continue"**
- Size: `20.00 GB`
- Click **"Create"**

**Step 4: Add Kali ISO**
1. Right-click `Attacker-Kali`  **"Settings"**
2. Click **"Storage"** tab
3. Click the **CD/DVD icon** (empty)
4. Click **"Choose a disk file..."**
5. Select your `kali-linux-xxx.iso` file
6. Click **"OK"**

**Step 5: Configure Network (CRITICAL)**
1. Right-click `Attacker-Kali`  **"Settings"**
2. Click **"Network"** tab
3. **Adapter 1:**
   -  Check **"Enable Network Adapter"**
   - "Attached to:"  Select **"Internal Network"**
   - "Name:"  Type `lab-network`
   - **Advanced:** Leave everything default
4. Click **"OK"**

### VM #2: Victim (Ubuntu Desktop)

**Repeat same process with these settings:**
- Name: `Victim-Ubuntu`
- Type: `Linux`, Version: `Ubuntu (64-bit)`
- Memory: `1024 MB`
- Disk: `15.00 GB`
- ISO: Ubuntu Desktop .iso
- **Network:** Internal Network named `lab-network`

### VM #3: Gateway (Ubuntu Server)

**Repeat same process with these settings:**
- Name: `Gateway-Server`
- Type: `Linux`, Version: `Ubuntu (64-bit)`
- Memory: `1024 MB`
- Disk: `10.00 GB`
- ISO: Ubuntu Server .iso
- **Network:** Internal Network named `lab-network`

---

##  **Phase 3: Install Operating Systems**

### Install Kali Linux (VM #1)
1. **Start** `Attacker-Kali` VM
2. Choose **"Graphical install"**
3. Follow prompts:
   - Language: English
   - Location: Your country
   - Keyboard: US
   - Hostname: `kali`
   - Domain: (leave blank)
   - Root password: `kali` (simple for lab)
   - User: `kali`, Password: `kali`
   - Partitioning: **"Guided - use entire disk"**
   - Software: **"Default selection"**
4. **Reboot** when complete
5. **Remove ISO:** Settings  Storage  Remove disk from drive

### Install Ubuntu Desktop (VM #2)
1. **Start** `Victim-Ubuntu` VM
2. Choose **"Try or Install Ubuntu"**
3. Click **"Install Ubuntu"**
4. Follow prompts:
   - Keyboard: US
   - Installation type: **"Normal installation"**
   - Installation type: **"Erase disk and install Ubuntu"**
   - User: `victim`, Password: `victim`
   - Computer name: `victim-ubuntu`
5. **Restart** when complete

### Install Ubuntu Server (VM #3)
1. **Start** `Gateway-Server` VM
2. Choose **"Try or Install Ubuntu Server"**
3. Follow prompts:
   - Language: English
   - Keyboard: US
   - Network: **Skip for now** (we'll configure manually)
   - Storage: **Use entire disk**
   - Profile: User `gateway`, Password `gateway`
   - SSH: **Install OpenSSH server** 
   - Snaps: (skip)
4. **Reboot** when complete

---

##  **Phase 4: Verify Network Isolation**

### Test Internal Network
**On any VM, try:**
```bash
ping 8.8.8.8
```
**Should FAIL** - this proves VMs are isolated from internet 

**From VM to VM should work after we configure IPs in Step 6**

---

##  **Verification Checklist**

Before proceeding to Step 6, verify:

- [ ] All 3 VMs created and OS installed
- [ ] Each VM network shows: "Attached to: Internal Network"
- [ ] Each VM network shows: "Name: lab-network"  
- [ ] VMs cannot ping internet (8.8.8.8) = isolated 
- [ ] All ISOs removed from Storage settings

### Check Network Settings:
**For each VM:**
1. Right-click VM  Settings  Network
2. Should see:
```
 Enable Network Adapter
Attached to: Internal Network
Name: lab-network
```

---

##  **Success!**

If all checks pass, your VMs are properly isolated and ready for Step 6 (IP configuration).

The internal network `lab-network` creates a virtual switch that only these 3 VMs can access - no internet, no host machine access, completely isolated for safe testing! 

---

##  **Troubleshooting**

### "VT-x is not available" error:
- **Intel Mac:** Enable virtualization in BIOS/UEFI
- **Apple Silicon Mac:** Should work automatically

### VM won't start:
- Check: Enough RAM available on host
- Check: VirtualBox has permissions in System Preferences

### Can't select "Internal Network":
- Make sure VirtualBox is updated to latest version
- Try restarting VirtualBox application

### Installation stuck/slow:
- Allocate more RAM if available
- Enable 3D acceleration in Display settings
