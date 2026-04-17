#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONITER 2026 - Lightweight Remote Command Executor Installer
This script runs xoniter.py and verifies dependencies with multiple fallback options
Now includes automatic pip installation for various Linux distributions
Developed by: Darian Alberto Camacho Salas
#Somos XONIDU
"""

import subprocess
import sys
import os
import platform
import shutil
import importlib.util
import time

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def supports_color():
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                return kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                return False
        return True

if not Colors.supports_color():
    for attr in dir(Colors):
        if not attr.startswith('_') and attr != 'supports_color':
            setattr(Colors, attr, '')

def get_system():
    return platform.system().lower()

def get_linux_distro():
    if get_system() != 'linux':
        return None
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content: return 'ubuntu'
                if 'debian' in content: return 'debian'
                if 'fedora' in content: return 'fedora'
                if 'centos' in content: return 'centos'
                if 'arch' in content: return 'arch'
                if 'manjaro' in content: return 'manjaro'
                if 'mint' in content: return 'mint'
                if 'opensuse' in content: return 'opensuse'
        return 'linux-generic'
    except:
        return 'linux-generic'

def get_python_command():
    if get_system() == 'windows':
        return ['python']
    else:
        try:
            subprocess.run(['python3', '--version'], capture_output=True, check=True)
            return ['python3']
        except:
            return ['python']

def print_banner():
    system = get_system()
    distro = get_linux_distro()
    system_text = {
        'windows': 'WINDOWS',
        'linux': f'LINUX ({distro.upper()})' if distro else 'LINUX',
        'darwin': 'MACOS'
    }.get(system, 'UNKNOWN')
    banner = f"""
{Colors.BLUE}{Colors.BOLD}═══════════════════════════════════════════════════════════
                    XONITER 2026 v1.0                    
              Lightweight Remote Command Executor            
              Execute commands on headless systems          
              via web interface                             
                                                          
              System detected: {system_text}            
                                                          
              Developed by: Darian Alberto            
              Camacho Salas                               
              #Somos XONIDU
═══════════════════════════════════════════════════════════{Colors.END}
    """
    print(banner)

def check_python():
    try:
        cmd = get_python_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def check_command(command):
    return shutil.which(command) is not None

def check_python_module(module_name):
    return importlib.util.find_spec(module_name) is not None

def install_pip():
    """Installs pip if not present, using the system package manager."""
    system = get_system()
    if system != 'linux':
        # Windows/macOS: pip usually comes with Python; if not, we can't auto-install easily.
        # We'll just show a message.
        if not check_command('pip') and not check_command('pip3'):
            print(f"{Colors.RED}Error: pip not found. Please install pip manually.{Colors.END}")
            return False
        return True
    
    distro = get_linux_distro()
    print(f"{Colors.BOLD}Installing pip for {distro}...{Colors.END}")
    
    # Commands to install pip
    install_cmds = []
    if distro in ['ubuntu', 'debian', 'mint']:
        install_cmds = [['sudo', 'apt', 'update'], ['sudo', 'apt', 'install', '-y', 'python3-pip']]
    elif distro in ['arch', 'manjaro']:
        install_cmds = [['sudo', 'pacman', '-S', '--noconfirm', 'python-pip']]
    elif distro in ['fedora']:
        install_cmds = [['sudo', 'dnf', 'install', '-y', 'python3-pip']]
    elif distro in ['centos']:
        install_cmds = [['sudo', 'yum', 'install', '-y', 'python3-pip']]
    elif distro in ['opensuse']:
        install_cmds = [['sudo', 'zypper', 'install', '-y', 'python3-pip']]
    else:
        # generic: try apt, pacman, dnf
        print(f"{Colors.YELLOW}Unrecognized distribution. Trying common package managers...{Colors.END}")
        install_cmds = [
            ['sudo', 'apt', 'update'], ['sudo', 'apt', 'install', '-y', 'python3-pip'],
            ['sudo', 'pacman', '-S', '--noconfirm', 'python-pip'],
            ['sudo', 'dnf', 'install', '-y', 'python3-pip']
        ]
    
    for cmd in install_cmds:
        try:
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, timeout=120)
        except Exception as e:
            print(f"{Colors.YELLOW}Command failed: {e}{Colors.END}")
            # continue to next command
    
    # Verify pip is now available
    if check_command('pip3') or check_command('pip'):
        print(f"{Colors.GREEN}pip installed successfully.{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}Failed to install pip automatically. Please install pip manually.{Colors.END}")
        return False

def check_dependencies():
    print(f"\n{Colors.BOLD}Checking Python dependencies...{Colors.END}")
    dependencies = [
        ('flask', 'flask', 'Web framework', 'flask'),
        ('qrcode', 'qrcode[pil]', 'QR code generation', 'qrcode'),
        ('Pillow', 'pillow', 'Image processing', 'PIL'),
    ]
    missing = []
    for module, package, desc, import_name in dependencies:
        if check_python_module(import_name):
            print(f"{Colors.GREEN}  - {module}: OK{Colors.END}")
        else:
            print(f"{Colors.YELLOW}  - {module}: MISSING{Colors.END}")
            missing.append(package)
    return missing

def install_with_pip(packages):
    system = get_system()
    distro = get_linux_distro()
    
    strategies = []
    strategies.append([sys.executable, '-m', 'pip', 'install'])
    if system != 'windows':
        strategies.append([sys.executable, '-m', 'pip', 'install', '--user'])
    if system == 'linux':
        strategies.append([sys.executable, '-m', 'pip', 'install', '--break-system-packages'])
        strategies.append([sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages'])
    strategies.append([sys.executable, '-m', 'pip', 'install', '--ignore-installed'])
    if check_command('pip3'):
        strategies.append(['pip3', 'install'])
        if system == 'linux':
            strategies.append(['pip3', 'install', '--break-system-packages'])
            strategies.append(['pip3', 'install', '--user'])
    if check_command('pip'):
        strategies.append(['pip', 'install'])
        if system == 'linux':
            strategies.append(['pip', 'install', '--break-system-packages'])
    
    for idx, strategy in enumerate(strategies, 1):
        cmd = strategy + packages
        print(f"\n  Attempt {idx}: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"{Colors.GREEN}  Success!{Colors.END}")
                return True
            else:
                print(f"{Colors.YELLOW}  Failed (code {result.returncode}){Colors.END}")
                if result.stderr:
                    print(f"    Error: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}  Timeout{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}  Error: {str(e)[:100]}{Colors.END}")
    return False

def install_dependencies(missing):
    if not missing:
        return True
    print(f"\n{Colors.BOLD}Installing missing dependencies...{Colors.END}")
    print(f"Packages: {', '.join(missing)}")
    if install_with_pip(missing):
        print(f"{Colors.GREEN}All dependencies installed!{Colors.END}")
        return True
    print(f"{Colors.RED}Automatic installation failed.{Colors.END}")
    print(f"{Colors.YELLOW}Manual instructions:{Colors.END}")
    system = get_system()
    distro = get_linux_distro()
    if system == 'linux':
        if distro in ['arch', 'manjaro']:
            print(f"  sudo pacman -S python-pip")
            print(f"  pip install --break-system-packages {' '.join(missing)}")
        elif distro in ['ubuntu', 'debian', 'mint']:
            print(f"  sudo apt install python3-pip -y")
            print(f"  pip install --user {' '.join(missing)}")
        else:
            print(f"  pip install --break-system-packages {' '.join(missing)}")
            print(f"  or pip install --user {' '.join(missing)}")
    else:
        print(f"  pip install {' '.join(missing)}")
    return False

def verify_imports():
    print(f"\n{Colors.BOLD}Verifying imports...{Colors.END}")
    modules = [('flask', 'flask'), ('qrcode', 'qrcode'), ('PIL', 'Pillow')]
    all_ok = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"{Colors.GREEN}  - {name}: OK{Colors.END}")
        except ImportError:
            print(f"{Colors.RED}  - {name}: FAILED{Colors.END}")
            all_ok = False
    return all_ok

def create_shortcuts():
    system = get_system()
    if system == 'windows':
        with open('START_XONITER.bat', 'w') as f:
            f.write("""@echo off
title XONITER 2026 - Remote Command Executor
color 1F
echo ========================================
echo      XONITER 2026 - Remote Executor
echo      Developed by Darian Alberto
echo ========================================
echo.
python start.py
pause
""")
        print(f"{Colors.GREEN}Created START_XONITER.bat{Colors.END}")
    elif system == 'linux':
        with open('START_XONITER.sh', 'w') as f:
            f.write("""#!/bin/bash
echo "========================================"
echo "      XONITER 2026 - Remote Executor"
echo "      Developed by Darian Alberto"
echo "========================================"
echo ""
python3 start.py
read -p "Press Enter to exit"
""")
        os.chmod('START_XONITER.sh', 0o755)
        print(f"{Colors.GREEN}Created START_XONITER.sh{Colors.END}")
    elif system == 'darwin':
        with open('START_XONITER.command', 'w') as f:
            f.write("""#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "      XONITER 2026 - Remote Executor"
echo "      Developed by Darian Alberto"
echo "========================================"
echo ""
python3 start.py
""")
        os.chmod('START_XONITER.command', 0o755)
        print(f"{Colors.GREEN}Created START_XONITER.command{Colors.END}")

def main():
    if get_system() == 'windows':
        os.system('cls')
    else:
        os.system('clear')
    print_banner()
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', '/?']:
        show_help()
        input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
        return
    
    if not check_python():
        print(f"\n{Colors.RED}Error: Python not installed{Colors.END}")
        print("Install from https://www.python.org/downloads/")
        input(f"\n{Colors.YELLOW}Press Enter...{Colors.END}")
        return
    
    python_version = subprocess.run(get_python_command() + ['--version'], capture_output=True, text=True).stdout.strip()
    print(f"{Colors.BOLD}Python:{Colors.END} {python_version}")
    print(f"{Colors.BOLD}Directory:{Colors.END} {os.path.dirname(os.path.abspath(__file__))}")
    
    # Ensure pip is installed (Linux only)
    if get_system() == 'linux' and not (check_command('pip') or check_command('pip3')):
        print(f"\n{Colors.YELLOW}pip not found. Attempting to install...{Colors.END}")
        if not install_pip():
            input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
            return
    
    missing = check_dependencies()
    if missing:
        print(f"\n{Colors.YELLOW}Missing dependencies: {', '.join(missing)}{Colors.END}")
        resp = input("Install automatically? (y/n): ")
        if resp.lower() == 'y':
            if not install_dependencies(missing):
                input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
                return
        else:
            print("\nPlease install manually and re-run.")
            input(f"\n{Colors.YELLOW}Press Enter...{Colors.END}")
            return
    
    if not os.path.exists('xoniter.py'):
        print(f"\n{Colors.RED}Error: xoniter.py not found{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter...{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}Verifying imports...{Colors.END}")
    if not verify_imports():
        print(f"{Colors.RED}Import error. Reinstalling...{Colors.END}")
        if not install_dependencies(['flask', 'qrcode', 'pillow']):
            input(f"\n{Colors.YELLOW}Press Enter...{Colors.END}")
            return
    
    print(f"\n{Colors.BOLD}Starting XONITER...{Colors.END}")
    print(f"{Colors.BOLD}Press Ctrl+C to stop{Colors.END}")
    print("-" * 60)
    try:
        python_cmd = get_python_command()
        cmd = python_cmd + ['xoniter.py'] + sys.argv[1:]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"\n{Colors.RED}Error: xoniter.py exited with code {result.returncode}{Colors.END}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stopped by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
    
    print(f"\n{Colors.BLUE}Thank you for using XONITER 2026{Colors.END}")
    print(f"{Colors.BLUE}#Somos XONIDU{Colors.END}")
    if get_system() != 'windows':
        input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")

def show_help():
    help_text = f"""
{Colors.BOLD}XONITER USAGE:{Colors.END}
  python start.py [options]
{Colors.BOLD}OPTIONS:{Colors.END}
  --host HOST     Host to bind to (default: 0.0.0.0)
  --port PORT     Port to bind to (default: 5100)
  --no-sudo       Disable sudo mode
  --no-qr         Disable QR code
{Colors.BOLD}WARNING:{Colors.END}
  For trusted local networks only. No authentication.
"""
    print(help_text)

if __name__ == '__main__':
    try:
        create_shortcuts()
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter...{Colors.END}")
