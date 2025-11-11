#!/usr/bin/env python3
"""
Traffic Interceptor and Analyzer
Captures and analyzes network traffic during MitM attacks
"""

import argparse
import sys
import time
import threading
import signal
import os
import csv
import json
from collections import defaultdict, Counter
from datetime import datetime
from colorama import init, Fore, Style
from scapy.all import *
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.dns import DNS, DNSQR, DNSRR

init(autoreset=True)

class TrafficInterceptor:
    def __init__(self, interface, output_file, duration=None, verbose=False):
        self.interface = interface
        self.output_file = output_file
        self.duration = duration
        self.verbose = verbose
        self.running = False
        self.packets = []
        self.stats = {
            'total_packets': 0,
            'protocols': Counter(),
            'dns_queries': [],
            'http_requests': [],
            'top_talkers': Counter(),
            'start_time': None,
            'end_time': None
        }
        
    def packet_handler(self, packet):
        """Handle captured packets"""
        if not self.running:
            return
            
        self.packets.append(packet)
        self.stats['total_packets'] += 1
        
        # Extract source and destination IPs
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            self.stats['top_talkers'][f"{src_ip} -> {dst_ip}"] += 1
            
            # Protocol analysis
            if TCP in packet:
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    self.stats['protocols']['HTTP'] += 1
                elif packet[TCP].dport == 443 or packet[TCP].sport == 443:
                    self.stats['protocols']['HTTPS'] += 1
                elif packet[TCP].dport == 22 or packet[TCP].sport == 22:
                    self.stats['protocols']['SSH'] += 1
                elif packet[TCP].dport == 21 or packet[TCP].sport == 21:
                    self.stats['protocols']['FTP'] += 1
                else:
                    self.stats['protocols']['TCP'] += 1
            elif UDP in packet:
                if packet[UDP].dport == 53 or packet[UDP].sport == 53:
                    self.stats['protocols']['DNS'] += 1
                else:
                    self.stats['protocols']['UDP'] += 1
            elif ICMP in packet:
                self.stats['protocols']['ICMP'] += 1
            else:
                self.stats['protocols']['Other'] += 1
        
        # HTTP analysis
        if HTTPRequest in packet:
            try:
                host = packet[HTTPRequest].Host.decode() if packet[HTTPRequest].Host else "Unknown"
                path = packet[HTTPRequest].Path.decode() if packet[HTTPRequest].Path else "/"
                method = packet[HTTPRequest].Method.decode() if packet[HTTPRequest].Method else "GET"
                url = f"http://{host}{path}"
                
                self.stats['http_requests'].append({
                    'timestamp': datetime.now().isoformat(),
                    'method': method,
                    'url': url,
                    'host': host,
                    'src_ip': packet[IP].src,
                    'dst_ip': packet[IP].dst
                })
                
                if self.verbose:
                    print(f"{Fore.GREEN}[HTTP] {method} {url} from {packet[IP].src}{Style.RESET_ALL}")
                    
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}[HTTP Error] {e}{Style.RESET_ALL}")
        
        # DNS analysis
        if DNS in packet and DNSQR in packet:
            try:
                query_name = packet[DNSQR].qname.decode().rstrip('.')
                query_type = packet[DNSQR].qtype
                
                self.stats['dns_queries'].append({
                    'timestamp': datetime.now().isoformat(),
                    'query': query_name,
                    'type': query_type,
                    'src_ip': packet[IP].src,
                    'dst_ip': packet[IP].dst
                })
                
                if self.verbose:
                    print(f"{Fore.BLUE}[DNS] Query for {query_name} from {packet[IP].src}{Style.RESET_ALL}")
                    
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}[DNS Error] {e}{Style.RESET_ALL}")
        
        if self.verbose and self.stats['total_packets'] % 100 == 0:
            print(f"{Fore.CYAN}[*] Captured {self.stats['total_packets']} packets{Style.RESET_ALL}")
    
    def save_pcap(self):
        """Save captured packets to PCAP file"""
        try:
            wrpcap(self.output_file, self.packets)
            print(f"{Fore.GREEN}[+] PCAP saved to {self.output_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error saving PCAP: {e}{Style.RESET_ALL}")
    
    def save_analysis(self):
        """Save analysis results to files"""
        base_name = os.path.splitext(self.output_file)[0]
        
        # Save DNS queries to CSV
        dns_file = f"{base_name}_dns_queries.csv"
        try:
            with open(dns_file, 'w', newline='') as f:
                if self.stats['dns_queries']:
                    writer = csv.DictWriter(f, fieldnames=self.stats['dns_queries'][0].keys())
                    writer.writeheader()
                    writer.writerows(self.stats['dns_queries'])
            print(f"{Fore.GREEN}[+] DNS queries saved to {dns_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error saving DNS queries: {e}{Style.RESET_ALL}")
        
        # Save HTTP requests to CSV
        http_file = f"{base_name}_http_requests.csv"
        try:
            with open(http_file, 'w', newline='') as f:
                if self.stats['http_requests']:
                    writer = csv.DictWriter(f, fieldnames=self.stats['http_requests'][0].keys())
                    writer.writeheader()
                    writer.writerows(self.stats['http_requests'])
            print(f"{Fore.GREEN}[+] HTTP requests saved to {http_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error saving HTTP requests: {e}{Style.RESET_ALL}")
        
        # Save summary statistics
        stats_file = f"{base_name}_summary.json"
        summary = {
            'total_packets': self.stats['total_packets'],
            'protocols': dict(self.stats['protocols']),
            'top_talkers': dict(self.stats['top_talkers'].most_common(10)),
            'dns_query_count': len(self.stats['dns_queries']),
            'http_request_count': len(self.stats['http_requests']),
            'capture_duration': (self.stats['end_time'] - self.stats['start_time']).total_seconds() if self.stats['end_time'] and self.stats['start_time'] else 0,
            'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None,
            'end_time': self.stats['end_time'].isoformat() if self.stats['end_time'] else None
        }
        
        try:
            with open(stats_file, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"{Fore.GREEN}[+] Summary statistics saved to {stats_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error saving summary: {e}{Style.RESET_ALL}")
    
    def print_statistics(self):
        """Print capture statistics"""
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}CAPTURE STATISTICS")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Total Packets: {self.stats['total_packets']}{Style.RESET_ALL}")
        
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            print(f"{Fore.YELLOW}Capture Duration: {duration:.2f} seconds{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Protocol Distribution:{Style.RESET_ALL}")
        for protocol, count in self.stats['protocols'].most_common():
            percentage = (count / self.stats['total_packets']) * 100
            print(f"  {protocol}: {count} ({percentage:.1f}%)")
        
        print(f"\n{Fore.CYAN}Top Talkers:{Style.RESET_ALL}")
        for flow, count in self.stats['top_talkers'].most_common(5):
            print(f"  {flow}: {count} packets")
        
        print(f"\n{Fore.CYAN}DNS Queries: {len(self.stats['dns_queries'])}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}HTTP Requests: {len(self.stats['http_requests'])}{Style.RESET_ALL}")
    
    def start_capture(self):
        """Start packet capture"""
        print(f"{Fore.CYAN}[*] Starting packet capture on {self.interface}...{Style.RESET_ALL}")
        
        if self.duration:
            print(f"{Fore.CYAN}[*] Capture duration: {self.duration} seconds{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}[+] Press Ctrl+C to stop capture{Style.RESET_ALL}")
        
        self.stats['start_time'] = datetime.now()
        self.running = True
        
        try:
            if self.duration:
                # Capture with timeout
                sniff(iface=self.interface, prn=self.packet_handler, 
                     timeout=self.duration, store=False)
            else:
                # Capture until interrupted
                sniff(iface=self.interface, prn=self.packet_handler, store=False)
        except Exception as e:
            print(f"{Fore.RED}[-] Error during capture: {e}{Style.RESET_ALL}")
        finally:
            self.running = False
            self.stats['end_time'] = datetime.now()
    
    def run(self):
        """Main execution function"""
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}TRAFFIC INTERCEPTOR")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        # Check if running as root
        if os.geteuid() != 0:
            print(f"{Fore.RED}[-] This script must be run as root (use sudo){Style.RESET_ALL}")
            sys.exit(1)
        
        # Set up signal handler for graceful exit
        def signal_handler(sig, frame):
            print(f"\n{Fore.YELLOW}[!] Interrupt received, stopping capture...{Style.RESET_ALL}")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start capture
        try:
            self.start_capture()
        except KeyboardInterrupt:
            self.running = False
        finally:
            # Save results
            print(f"\n{Fore.YELLOW}[!] Saving capture results...{Style.RESET_ALL}")
            self.save_pcap()
            self.save_analysis()
            self.print_statistics()

def main():
    parser = argparse.ArgumentParser(description='Traffic Interceptor and Analyzer')
    parser.add_argument('-i', '--interface', required=True, help='Network interface to capture on')
    parser.add_argument('-o', '--output', required=True, help='Output PCAP file')
    parser.add_argument('-d', '--duration', type=int, help='Capture duration in seconds')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create and run interceptor
    interceptor = TrafficInterceptor(args.interface, args.output, args.duration, args.verbose)
    interceptor.run()

if __name__ == '__main__':
    main()
