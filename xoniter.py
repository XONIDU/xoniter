	#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONITER 2026 - Lightweight Remote Command Executor
Web-based remote command execution for headless systems
Developed by: Darian Alberto Camacho Salas
#Somos XONIDU
"""

from flask import Flask, request, render_template
import subprocess
import argparse
import html
import os
import time
import getpass
import socket
import sys
import re
import json

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5100

app = Flask(__name__)
sudo_password = None
config = {}

# ============================================================================
# Configuration management
# ============================================================================
def get_config_path():
    """Get config file path (prioritizes ~/.xoniter/config.json)"""
    home_config = os.path.join(os.path.expanduser("~"), '.xoniter', 'config.json')
    if os.path.exists(home_config):
        return home_config
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_config = os.path.join(script_dir, 'config.json')
    if os.path.exists(local_config):
        return local_config
    system_config = '/usr/share/xoniter/config.json'
    if os.path.exists(system_config):
        return system_config
    return home_config

def load_config():
    """Load configuration from config.json"""
    global config
    config_path = get_config_path()
    default_config = {
        "allowed_commands": ["ls", "df", "free", "uname", "ip", "cat", "tail", "head", "grep", "systemctl", "ping", "ss", "ps", "top"],
        "blocked_patterns": [r'\brm\b', r'/bin/rm', r';\s*rm', r'&&\s*rm', r'\|\s*rm', r'\bdd\b', r'\bmkfs\b'],
        "ask_for_confirmation": True,
        "confirmation_timeout": 30,
        "require_auth": False,
        "max_command_length": 500
    }
    try:
        with open(config_path, 'r') as f:
            loaded = json.load(f)
            default_config.update(loaded)
        config = default_config
        print(f"[CONFIG] Loaded from {config_path}")
    except FileNotFoundError:
        config = default_config
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"[CONFIG] Created default config at {config_path}")
    except Exception as e:
        print(f"[CONFIG] Error loading config: {e}")
        config = default_config

def is_command_allowed(command):
    """Check if command is in allowed list"""
    if not command or not command.strip():
        return False
    first_word = command.strip().split()[0]
    return first_word in config.get("allowed_commands", [])

def is_command_blocked(command):
    """Check if command contains blocked patterns"""
    for pattern in config.get("blocked_patterns", []):
        if re.search(pattern, command):
            return True
    return False

def ask_confirmation(command):
    """Ask user for confirmation before executing command"""
    if not config.get("ask_for_confirmation", True):
        return True
    
    print(f"\n[CONFIRM] Command: {command[:200]}")
    print("[CONFIRM] Allow this command? (y/n): ", end="")
    sys.stdout.flush()
    try:
        response = input().strip().lower()
        return response == 'y' or response == 'yes'
    except:
        return False

# ============================================================================
# Security functions
# ============================================================================
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def escape_single_quotes(command):
    return command.replace("'", "'\"'\"'")

def auto_add_noconfirm(command):
    if "pacman" in command and "--noconfirm" not in command:
        parts = command.split()
        for i, part in enumerate(parts):
            if part == "pacman":
                parts.insert(i + 1, "--noconfirm")
                break
        return " ".join(parts)
    return command

def run_command(command, timeout=None):
    """Execute command with sudo support and confirmation"""
    global sudo_password
    
    if not command or not command.strip():
        return "", "Empty command", -1, None
    
    if not is_command_allowed(command):
        allowed = ', '.join(config.get("allowed_commands", []))
        return "", f"Command not allowed. Allowed: {allowed}", -1, None
    
    if is_command_blocked(command):
        return "", "Command blocked for security reasons (matches blocked pattern)", -1, None
    
    if config.get("ask_for_confirmation", True):
        if not ask_confirmation(command):
            return "", "Command cancelled by user", -1, None
    
    command = auto_add_noconfirm(command)
    
    if not sudo_password:
        try:
            proc = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            return proc.stdout, proc.stderr, proc.returncode, None
        except subprocess.TimeoutExpired:
            return "", "", -1, f"Timeout after {timeout} seconds."
        except Exception as e:
            return "", "", -1, str(e)
    
    escaped = escape_single_quotes(command)
    sudo_cmd = f"sudo -S bash -c '{escaped}'"
    
    try:
        proc = subprocess.Popen(
            sudo_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(input=f"{sudo_password}\n", timeout=timeout)
        return stdout, stderr, proc.returncode, None
    except subprocess.TimeoutExpired:
        proc.terminate()
        return "", "", -1, f"Timeout after {timeout} seconds."
    except Exception as e:
        return "", "", -1, str(e)

# ============================================================================
# Web routes
# ============================================================================
@app.route("/", methods=["GET", "POST"])
def index():
    ran = False
    stdout = ""
    stderr = ""
    rc = ""
    elapsed = ""
    error = ""
    cmd_text = ""
    timeout_value = ""
    
    if request.method == "POST":
        cmd_text = request.form.get("cmd", "").strip()
        timeout_field = request.form.get("timeout", "").strip()
        timeout = None
        
        if len(cmd_text) > config.get("max_command_length", 500):
            error = f"Command too long (max {config.get('max_command_length', 500)} chars)"
        elif timeout_field:
            try:
                timeout = float(timeout_field)
                timeout_value = timeout_field
            except ValueError:
                pass
        
        if cmd_text and not error:
            ran = True
            start = time.time()
            stdout, stderr, rc, error_msg = run_command(cmd_text, timeout)
            elapsed = f"{time.time() - start:.2f}s"
            if error_msg:
                error = error_msg
    
    try:
        user = getpass.getuser()
    except:
        user = "unknown"
    
    server_ip = get_ip_address()
    full_url = f"http://{server_ip}:{app.config.get('PORT', DEFAULT_PORT)}/"
    network_info = f"{server_ip} (port {app.config.get('PORT', DEFAULT_PORT)})"
    sudo_active = sudo_password is not None
    sudo_status = "Enabled" if sudo_active else "Disabled"
    
    return render_template(
        "index.html",
        host=app.config.get("HOST", DEFAULT_HOST),
        port=app.config.get("PORT", DEFAULT_PORT),
        full_url=full_url,
        network_info=network_info,
        user=user,
        sudo_status=sudo_status,
        sudo_active=sudo_active,
        cmd_escaped=html.escape(cmd_text),
        ran=ran,
        command=html.escape(cmd_text),
        stdout=html.escape(stdout),
        stderr=html.escape(stderr),
        rc=rc,
        elapsed=elapsed,
        error=html.escape(error),
        timeout_value=timeout_value
    )

# ============================================================================
# Colors and banner
# ============================================================================
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_startup_banner(host, port, full_url, no_qr):
    print(f"\n{Colors.PURPLE}{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}                    XONITER 2026 v1.0{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}              Lightweight Remote Command Executor{Colors.END}")
    print(f"{Colors.PURPLE}{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.GREEN}✅ Server started at: {full_url}{Colors.END}")
    print(f"{Colors.GREEN}✅ Host: {host} | Port: {port}{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  Security: Allowed commands: {', '.join(config.get('allowed_commands', [])[:6])}...{Colors.END}")
    if config.get("ask_for_confirmation"):
        print(f"{Colors.YELLOW}🔐 Confirmation mode: ENABLED (asks before executing){Colors.END}")
    print(f"{Colors.PURPLE}{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.CYAN}Press Ctrl+C to stop{Colors.END}")
    print("")

def generate_terminal_qr(url):
    """Generate ASCII QR code in terminal"""
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=1, border=1)
        qr.add_data(url)
        qr.make()
        matrix = qr.get_matrix()
        ascii_qr = ""
        for row in matrix:
            for col in row:
                ascii_qr += "██" if col else "  "
            ascii_qr += "\n"
        return ascii_qr
    except:
        return None

# ============================================================================
# Main
# ============================================================================
def main():
    global sudo_password
    
    parser = argparse.ArgumentParser(description="XONITER - Web-based remote command executor")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind to (default: {DEFAULT_PORT})")
    parser.add_argument("--no-sudo", action="store_true", help="Disable sudo mode (run without privileges)")
    parser.add_argument("--no-qr", action="store_true", help="Disable QR code display")
    args = parser.parse_args()
    
    # Load configuration
    load_config()
    
    # Ask for sudo password if enabled
    if not args.no_sudo:
        try:
            sudo_password = getpass.getpass(f"{Colors.YELLOW}Enter sudo password (press Enter to skip): {Colors.END}")
            if not sudo_password:
                sudo_password = None
                print(f"{Colors.YELLOW}Running without sudo privileges{Colors.END}")
        except:
            sudo_password = None
    
    server_ip = get_ip_address()
    full_url = f"http://{server_ip}:{args.port}/"
    
    print_startup_banner(args.host, args.port, full_url, args.no_qr)
    
    if not args.no_qr:
        qr = generate_terminal_qr(full_url)
        if qr:
            print(qr)
            print(f"{Colors.GREEN}Scan QR code to access from mobile{Colors.END}")
            print(f"{Colors.PURPLE}{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.END}")
    
    app.config["HOST"] = args.host
    app.config["PORT"] = args.port
    
    try:
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Server stopped.{Colors.END}")
        sys.exit(0)

if __name__ == "__main__":
    main()
