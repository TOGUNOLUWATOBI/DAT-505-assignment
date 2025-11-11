#!/usr/bin/env python3
"""
Fake Web Server for DNS Spoofing Demonstration
Serves content to demonstrate successful DNS redirection
"""

from flask import Flask, request, render_template_string
import argparse
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

app = Flask(__name__)

# Store visitor logs
visitor_logs = []

# HTML template for the fake page
FAKE_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DNS Spoofing Demonstration - {{ domain }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 50px;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 40px;
            max-width: 600px;
            margin: 0 auto;
            backdrop-filter: blur(10px);
        }
        .warning {
            background: #ff4757;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .info {
            background: #2f3542;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            text-align: left;
        }
        h1 { color: #ff6b6b; }
        h2 { color: #4ecdc4; }
    </style>
</head>
<body>
    <div class="container">
        <h1> DNS Spoofing Successful!</h1>
        
        <div class="warning">
            <h2> Security Alert</h2>
            <p>This page demonstrates a successful DNS spoofing attack. You requested <strong>{{ domain }}</strong> but were redirected to an attacker-controlled server.</p>
        </div>
        
        <div class="info">
            <h3> Connection Details:</h3>
            <p><strong>Requested Domain:</strong> {{ domain }}</p>
            <p><strong>Your IP Address:</strong> {{ client_ip }}</p>
            <p><strong>Server IP:</strong> {{ server_ip }}</p>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            <p><strong>User Agent:</strong> {{ user_agent }}</p>
        </div>
        
        <div class="info">
            <h3> Mitigation Strategies:</h3>
            <ul style="text-align: left;">
                <li>Use DNS over HTTPS (DoH) or DNS over TLS (DoT)</li>
                <li>Implement DNSSEC validation</li>
                <li>Use trusted DNS servers (e.g., 1.1.1.1, 8.8.8.8)</li>
                <li>Monitor network traffic for suspicious ARP activity</li>
                <li>Use static ARP entries for critical servers</li>
                <li>Implement network segmentation and VLANs</li>
            </ul>
        </div>
        
        <p style="margin-top: 30px; font-size: 14px; opacity: 0.8;">
            This is a controlled demonstration in a lab environment.<br>
            Real attacks of this nature are illegal and unethical.
        </p>
    </div>
</body>
</html>
"""

@app.route('/')
@app.route('/<path:path>')
def fake_page(path=''):
    """Serve fake page to demonstrate DNS spoofing"""
    
    # Log the visitor
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'domain': request.headers.get('Host', 'unknown'),
        'path': path,
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'referrer': request.headers.get('Referer', 'none')
    }
    visitor_logs.append(log_entry)
    
    # Print log to console
    print(f"{Fore.RED}[VICTIM] {log_entry['domain']}{path} accessed by {log_entry['client_ip']}{Style.RESET_ALL}")
    
    # Render fake page
    return render_template_string(
        FAKE_PAGE_TEMPLATE,
        domain=log_entry['domain'],
        client_ip=log_entry['client_ip'],
        server_ip=request.environ.get('SERVER_NAME', 'unknown'),
        timestamp=log_entry['timestamp'],
        user_agent=log_entry['user_agent'],
        path=path
    )

@app.route('/logs')
def show_logs():
    """Show visitor logs"""
    logs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visitor Logs</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>DNS Spoofing Visitor Logs</h1>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Domain</th>
                <th>Path</th>
                <th>Client IP</th>
                <th>User Agent</th>
            </tr>
    """
    
    for log in visitor_logs:
        logs_html += f"""
            <tr>
                <td>{log['timestamp']}</td>
                <td>{log['domain']}</td>
                <td>{log['path']}</td>
                <td>{log['client_ip']}</td>
                <td>{log['user_agent']}</td>
            </tr>
        """
    
    logs_html += """
        </table>
        <p>Total visitors: {}</p>
    </body>
    </html>
    """.format(len(visitor_logs))
    
    return logs_html

def main():
    parser = argparse.ArgumentParser(description='Fake Web Server for DNS Spoofing Demo')
    parser.add_argument('-p', '--port', type=int, default=80, help='Server port (default: 80)')
    parser.add_argument('-H', '--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}FAKE WEB SERVER")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Starting server on {args.host}:{args.port}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Visit /logs to see visitor statistics{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] This server demonstrates DNS spoofing redirection{Style.RESET_ALL}")
    
    try:
        app.run(host=args.host, port=args.port, debug=False)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Server stopped{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {e}{Style.RESET_ALL}")

if __name__ == '__main__':
    main()
