#!/usr/bin/env python3
"""
Test Suite for ARP Spoofing & DNS MitM Tools
Validates all components work correctly before deployment
"""

import subprocess
import sys
import os
import json
import time
import importlib.util
from colorama import init, Fore, Style

init(autoreset=True)

class TestSuite:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        if passed:
            self.tests_passed += 1
            status = f"{Fore.GREEN}PASS{Style.RESET_ALL}"
        else:
            self.tests_failed += 1
            status = f"{Fore.RED}FAIL{Style.RESET_ALL}"
        
        result = f"[{status}] {test_name}"
        if message:
            result += f" - {message}"
        
        print(result)
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })

    def test_dependencies(self):
        """Test Python dependencies"""
        print(f"\n{Fore.CYAN}Testing Python Dependencies...{Style.RESET_ALL}")
        
        required_modules = [
            ('scapy', 'scapy'),
            ('colorama', 'colorama'),
            ('flask', 'flask'),
            ('requests', 'requests')
        ]
        
        for module_name, import_name in required_modules:
            try:
                spec = importlib.util.find_spec(import_name)
                if spec is not None:
                    self.log_test(f"Import {module_name}", True)
                else:
                    self.log_test(f"Import {module_name}", False, "Module not found")
            except Exception as e:
                self.log_test(f"Import {module_name}", False, str(e))

    def test_file_permissions(self):
        """Test file permissions and executability"""
        print(f"\n{Fore.CYAN}Testing File Permissions...{Style.RESET_ALL}")
        
        script_files = [
            'scripts/arp_spoof.py',
            'scripts/traffic_interceptor.py',
            'scripts/dns_spoof.py',
            'scripts/sslstrip_demo.py',
            'scripts/fake_web_server.py',
            'demo.py',
            'setup_lab.sh'
        ]
        
        for script in script_files:
            if os.path.exists(script):
                if os.access(script, os.R_OK):
                    self.log_test(f"Read permission {script}", True)
                else:
                    self.log_test(f"Read permission {script}", False)
                
                if os.access(script, os.X_OK):
                    self.log_test(f"Execute permission {script}", True)
                else:
                    self.log_test(f"Execute permission {script}", False)
            else:
                self.log_test(f"File exists {script}", False, "File not found")

    def test_syntax_validation(self):
        """Test Python syntax validation"""
        print(f"\n{Fore.CYAN}Testing Python Syntax...{Style.RESET_ALL}")
        
        python_files = [
            'scripts/arp_spoof.py',
            'scripts/traffic_interceptor.py',
            'scripts/dns_spoof.py',
            'scripts/sslstrip_demo.py',
            'scripts/fake_web_server.py',
            'demo.py'
        ]
        
        for py_file in python_files:
            if os.path.exists(py_file):
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'py_compile', py_file
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.log_test(f"Syntax {py_file}", True)
                    else:
                        self.log_test(f"Syntax {py_file}", False, result.stderr.strip())
                        
                except Exception as e:
                    self.log_test(f"Syntax {py_file}", False, str(e))

    def test_config_files(self):
        """Test configuration file validity"""
        print(f"\n{Fore.CYAN}Testing Configuration Files...{Style.RESET_ALL}")
        
        # Test DNS targets config
        dns_config = 'config/dns_targets.json'
        if os.path.exists(dns_config):
            try:
                with open(dns_config, 'r') as f:
                    config = json.load(f)
                
                required_keys = ['targets', 'forward_unmatched', 'upstream_dns']
                for key in required_keys:
                    if key in config:
                        self.log_test(f"DNS config key '{key}'", True)
                    else:
                        self.log_test(f"DNS config key '{key}'", False, "Missing key")
                
                # Validate targets format
                if 'targets' in config and isinstance(config['targets'], dict):
                    self.log_test("DNS targets format", True)
                else:
                    self.log_test("DNS targets format", False, "Invalid format")
                    
            except json.JSONDecodeError as e:
                self.log_test("DNS config JSON", False, str(e))
            except Exception as e:
                self.log_test("DNS config file", False, str(e))
        else:
            self.log_test("DNS config file", False, "File not found")

    def test_help_functionality(self):
        """Test help functionality of scripts"""
        print(f"\n{Fore.CYAN}Testing Help Functionality...{Style.RESET_ALL}")
        
        scripts_with_help = [
            'scripts/arp_spoof.py',
            'scripts/traffic_interceptor.py',
            'scripts/dns_spoof.py',
            'scripts/sslstrip_demo.py',
            'scripts/fake_web_server.py'
        ]
        
        for script in scripts_with_help:
            if os.path.exists(script):
                try:
                    result = subprocess.run([
                        sys.executable, script, '-h'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0 and 'usage:' in result.stdout.lower():
                        self.log_test(f"Help {script}", True)
                    else:
                        self.log_test(f"Help {script}", False, "No help output")
                        
                except subprocess.TimeoutExpired:
                    self.log_test(f"Help {script}", False, "Timeout")
                except Exception as e:
                    self.log_test(f"Help {script}", False, str(e))

    def test_directory_structure(self):
        """Test required directory structure"""
        print(f"\n{Fore.CYAN}Testing Directory Structure...{Style.RESET_ALL}")
        
        required_dirs = [
            'scripts',
            'config',
            'pcap_files',
            'evidence'
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                self.log_test(f"Directory {directory}", True)
            else:
                self.log_test(f"Directory {directory}", False, "Missing directory")

    def test_import_capabilities(self):
        """Test if scripts can import required modules"""
        print(f"\n{Fore.CYAN}Testing Import Capabilities...{Style.RESET_ALL}")
        
        # Test critical imports for each script
        import_tests = [
            ('ARP Spoof imports', ['scapy.all', 'colorama', 'argparse']),
            ('Traffic Interceptor imports', ['scapy.all', 'colorama', 'csv', 'json']),
            ('DNS Spoof imports', ['scapy.all', 'scapy.layers.dns', 'json']),
            ('SSLStrip imports', ['flask', 'requests', 'subprocess']),
            ('Fake Server imports', ['flask', 'colorama'])
        ]
        
        for test_name, modules in import_tests:
            try:
                for module in modules:
                    __import__(module)
                self.log_test(test_name, True)
            except ImportError as e:
                self.log_test(test_name, False, f"Missing: {e}")
            except Exception as e:
                self.log_test(test_name, False, str(e))

    def test_basic_scapy_functionality(self):
        """Test basic Scapy functionality"""
        print(f"\n{Fore.CYAN}Testing Scapy Functionality...{Style.RESET_ALL}")
        
        try:
            from scapy.all import IP, TCP, UDP, ARP, DNS
            from scapy.layers.dns import DNSQR, DNSRR
            
            # Test packet creation
            ip_packet = IP(dst="8.8.8.8")
            self.log_test("Scapy IP packet creation", True)
            
            arp_packet = ARP(pdst="192.168.1.1")
            self.log_test("Scapy ARP packet creation", True)
            
            dns_packet = DNS(qd=DNSQR(qname="example.com"))
            self.log_test("Scapy DNS packet creation", True)
            
        except Exception as e:
            self.log_test("Scapy functionality", False, str(e))

    def generate_report(self):
        """Generate test report"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}TEST REPORT")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Fore.YELLOW}Summary:{Style.RESET_ALL}")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {Fore.GREEN}{self.tests_passed}{Style.RESET_ALL}")
        print(f"  Failed: {Fore.RED}{self.tests_failed}{Style.RESET_ALL}")
        print(f"  Pass Rate: {pass_rate:.1f}%")
        
        if self.tests_failed > 0:
            print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   {result['test']}: {result['message']}")
        
        print(f"\n{Fore.CYAN}Recommendations:{Style.RESET_ALL}")
        if self.tests_failed == 0:
            print(f"  {Fore.GREEN} All tests passed! Your project is ready for deployment.{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}  Fix failed tests before proceeding with the assignment.{Style.RESET_ALL}")
            print(f"  {Fore.BLUE} Run 'pip install -r requirements.txt' to install missing dependencies.{Style.RESET_ALL}")
            print(f"  {Fore.BLUE} Use 'chmod +x scripts/*.py' to fix permission issues.{Style.RESET_ALL}")

    def run_all_tests(self):
        """Run all test suites"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}ARP SPOOFING & DNS MitM - TEST SUITE")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        self.test_dependencies()
        self.test_directory_structure()
        self.test_file_permissions()
        self.test_config_files()
        self.test_syntax_validation()
        self.test_import_capabilities()
        self.test_basic_scapy_functionality()
        self.test_help_functionality()
        
        self.generate_report()

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        print(f"{Fore.YELLOW}Running quick validation tests...{Style.RESET_ALL}")
        # Quick tests only
        suite = TestSuite()
        suite.test_dependencies()
        suite.test_directory_structure()
        suite.test_config_files()
        suite.generate_report()
    else:
        # Full test suite
        suite = TestSuite()
        suite.run_all_tests()

if __name__ == '__main__':
    main()
