#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONITER 2026 - Lightweight Remote Command Executor Installer
This script runs xoniter.py and verifies dependencies with multiple fallback options
Supports: Linux (all distros), Windows, macOS
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
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
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

# ============================================================================
# System detection
# ============================================================================
def get_system():
    return platform.system().lower()

def get_linux_distro():
    if get_system() != 'linux':
        return None
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content or 'debian' in content or 'mint' in content or 'pop' in content:
                    return 'debian-based'
                elif 'arch' in content or 'manjaro' in content or 'endeavouros' in content:
                    return 'arch-based'
                elif 'fedora' in content or 'rhel' in content or 'centos' in content:
                    return 'fedora-based'
                elif 'opensuse' in content or 'suse' in content:
                    return 'suse-based'
                elif 'alpine' in content:
                    return 'alpine'
        # Fallback: check package managers
        if shutil.which('apt'):
            return 'debian-based'
        elif shutil.which('pacman'):
            return 'arch-based'
        elif shutil.which('dnf'):
            return 'fedora-based'
        elif shutil.which('zypper'):
            return 'suse-based'
        elif shutil.which('apk'):
            return 'alpine'
        return 'linux-generic'
    except:
        return 'linux-generic'

def get_python_command():
    if get_system() == 'windows':
        return ['python']
    else:
        for cmd in ['python3', 'python']:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                return [cmd]
            except:
                continue
        return ['python3']

def get_pip_commands():
    """Returns list of possible pip commands to try"""
    system = get_system()
    python_cmd = get_python_command()[0]
    
    commands = [
        [sys.executable, '-m', 'pip'],
        [python_cmd, '-m', 'pip'],
    ]
    
    if system != 'windows':
        commands.append(['pip3'])
        commands.append(['pip'])
    
    return commands

def get_install_flags():
    """Returns list of flag combinations to try"""
    system = get_system()
    distro = get_linux_distro()
    flags_list = [[]]  # Start with no flags
    
    if system == 'linux':
        if distro in ['arch-based', 'fedora-based']:
            flags_list.append(['--break-system-packages'])
            flags_list.append(['--user', '--break-system-packages'])
            flags_list.append(['--user'])
        else:
            flags_list.append(['--user'])
            flags_list.append(['--break-system-packages'])
            flags_list.append(['--user', '--break-system-packages'])
    elif system == 'darwin':
        flags_list.append(['--user'])
    
    return flags_list

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_xoniter_path():
    """Detects xoniter.py in multiple locations"""
    script_dir = get_script_dir()
    rutas = [
        os.path.join(script_dir, 'xoniter.py'),
        os.path.join(os.getcwd(), 'xoniter.py'),
        '/usr/share/xoniter/xoniter.py',
        os.path.join(os.path.expanduser("~"), '.xoniter', 'xoniter.py'),
    ]
    for r in rutas:
        if os.path.exists(r):
            return r
    return None

def print_banner():
    system = get_system()
    distro = get_linux_distro()
    system_text = {
        'windows': 'WINDOWS',
        'linux': f'LINUX ({distro.upper()})' if distro else 'LINUX',
        'darwin': 'MACOS'
    }.get(system, 'UNKNOWN')
    
    banner = f"""
{Colors.PURPLE}{Colors.BOLD}═══════════════════════════════════════════════════════════
                    XONITER 2026 v1.0.1                    
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

def mostrar_ayuda():
    ayuda = f"""
{Colors.BOLD}XONITER USAGE:{Colors.END}

  python start.py [options]

{Colors.BOLD}DESCRIPTION:{Colors.END}

  XONITER is a lightweight tool that provides a web interface
  to execute commands on a Linux machine from any device on
  the same local network.

{Colors.BOLD}OPTIONS:{Colors.END}

  --host HOST     Host to bind to (default: 0.0.0.0)
  --port PORT     Port to bind to (default: 5100)
  --no-sudo       Disable sudo mode (run without privileges)
  --no-qr         Disable QR code display

{Colors.BOLD}EXAMPLES:{Colors.END}

  Basic execution (localhost):
    python start.py

  Expose on local network:
    python start.py --host 0.0.0.0 --port 5100

  Secure mode (local only, no sudo):
    python start.py --host 127.0.0.1 --port 5100 --no-sudo

{Colors.BOLD}WARNING:{Colors.END}

  This tool is for TRUSTED LOCAL NETWORKS ONLY.
  Never expose it to the internet or untrusted networks.
    """
    print(ayuda)

# ============================================================================
# Python and pip verification
# ============================================================================
def check_python():
    try:
        cmd = get_python_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def check_pip():
    """Check if pip is available using multiple methods"""
    for pip_cmd in get_pip_commands():
        try:
            subprocess.run(pip_cmd + ['--version'], capture_output=True, check=True)
            return True, pip_cmd
        except:
            continue
    return False, None

def install_pip_linux():
    """Install pip on various Linux distributions"""
    distro = get_linux_distro()
    print(f"{Colors.YELLOW}Installing pip on Linux ({distro})...{Colors.END}")
    
    install_commands = []
    
    if distro == 'debian-based':
        install_commands = [
            ['sudo', 'apt', 'update'],
            ['sudo', 'apt', 'install', '-y', 'python3-pip'],
            ['sudo', 'apt', 'install', '-y', 'python3-pip', '--fix-missing']
        ]
    elif distro == 'arch-based':
        install_commands = [
            ['sudo', 'pacman', '-S', '--noconfirm', 'python-pip'],
            ['sudo', 'pacman', '-S', '--noconfirm', 'python-pip', '--overwrite', '*']
        ]
    elif distro == 'fedora-based':
        install_commands = [
            ['sudo', 'dnf', 'install', '-y', 'python3-pip'],
            ['sudo', 'dnf', 'install', '-y', 'python3-pip', '--allowerasing']
        ]
    elif distro == 'suse-based':
        install_commands = [
            ['sudo', 'zypper', 'install', '-y', 'python3-pip'],
            ['sudo', 'zypper', 'install', '-y', 'python3-pip', '--force']
        ]
    elif distro == 'alpine':
        install_commands = [
            ['sudo', 'apk', 'add', 'py3-pip'],
            ['sudo', 'apk', 'add', 'python3', 'py3-pip']
        ]
    else:
        # Generic: try multiple package managers
        install_commands = [
            ['sudo', 'apt', 'install', '-y', 'python3-pip'],
            ['sudo', 'pacman', '-S', '--noconfirm', 'python-pip'],
            ['sudo', 'dnf', 'install', '-y', 'python3-pip'],
            ['sudo', 'zypper', 'install', '-y', 'python3-pip'],
        ]
    
    for cmd in install_commands:
        try:
            print(f"  Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, timeout=120)
            print(f"{Colors.GREEN}  Success!{Colors.END}")
            return True
        except:
            continue
    
    return False

def install_pip_windows():
    """Install pip on Windows using ensurepip"""
    print(f"{Colors.YELLOW}Installing pip on Windows...{Colors.END}")
    try:
        subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], check=True)
        print(f"{Colors.GREEN}  Success!{Colors.END}")
        return True
    except:
        pass
    
    # Alternative: download get-pip.py
    try:
        import urllib.request
        print(f"{Colors.YELLOW}  Downloading get-pip.py...{Colors.END}")
        urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')
        subprocess.run([sys.executable, 'get-pip.py'], check=True)
        os.remove('get-pip.py')
        print(f"{Colors.GREEN}  Success!{Colors.END}")
        return True
    except:
        return False

def install_pip_macos():
    """Install pip on macOS"""
    print(f"{Colors.YELLOW}Installing pip on macOS...{Colors.END}")
    
    # Try with ensurepip first
    try:
        subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], check=True)
        print(f"{Colors.GREEN}  Success!{Colors.END}")
        return True
    except:
        pass
    
    # Try with brew
    if shutil.which('brew'):
        try:
            subprocess.run(['brew', 'install', 'python3'], check=True)
            print(f"{Colors.GREEN}  Success!{Colors.END}")
            return True
        except:
            pass
    
    return False

# ============================================================================
# Dependency management
# ============================================================================
def check_python_module(module_name):
    return importlib.util.find_spec(module_name) is not None

def check_dependencies():
    print(f"\n{Colors.BOLD}Checking Python dependencies...{Colors.END}")
    dependencies = [
        ('flask', 'flask', 'Web framework'),
        ('qrcode', 'qrcode', 'QR code generation'),
        ('PIL', 'pillow', 'Image processing'),
    ]
    missing = []
    for module, package, desc in dependencies:
        if check_python_module(module if module != 'PIL' else 'PIL'):
            print(f"{Colors.GREEN}  - {module}: OK{Colors.END}")
        else:
            print(f"{Colors.YELLOW}  - {module}: MISSING{Colors.END}")
            missing.append(package)
    return missing

def install_with_pip(packages):
    """Try multiple pip commands with multiple flag combinations"""
    system = get_system()
    
    # Get all possible pip commands
    pip_commands = get_pip_commands()
    flag_combinations = get_install_flags()
    
    attempt = 1
    for pip_cmd in pip_commands:
        for flags in flag_combinations:
            cmd = pip_cmd + ['install'] + flags + packages
            print(f"\n  Attempt {attempt}: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}  Success!{Colors.END}")
                    return True
                else:
                    print(f"{Colors.YELLOW}  Failed (code {result.returncode}){Colors.END}")
                    if result.stderr:
                        err_line = result.stderr.split('\n')[0][:150]
                        print(f"    Error: {err_line}")
            except subprocess.TimeoutExpired:
                print(f"{Colors.YELLOW}  Timeout{Colors.END}")
            except Exception as e:
                print(f"{Colors.YELLOW}  Error: {str(e)[:100]}{Colors.END}")
            attempt += 1
    
    return False

def install_dependencies(missing):
    if not missing:
        return True
    
    print(f"\n{Colors.BOLD}Installing missing dependencies...{Colors.END}")
    print(f"Packages to install: {', '.join(missing)}")
    
    if install_with_pip(missing):
        print(f"\n{Colors.GREEN}All dependencies installed successfully!{Colors.END}")
        return True
    
    print(f"\n{Colors.RED}Automatic installation failed.{Colors.END}")
    print(f"\n{Colors.YELLOW}Please install dependencies manually:{Colors.END}")
    
    system = get_system()
    distro = get_linux_distro()
    packages_str = ' '.join(missing)
    
    if system == 'linux':
        if distro == 'arch-based':
            print(f"\n  sudo pacman -S python-pip")
            print(f"  pip install --break-system-packages {packages_str}")
        elif distro == 'debian-based':
            print(f"\n  sudo apt update")
            print(f"  sudo apt install python3-pip -y")
            print(f"  pip install --user {packages_str}")
        elif distro == 'fedora-based':
            print(f"\n  sudo dnf install python3-pip")
            print(f"  pip install --break-system-packages {packages_str}")
        else:
            print(f"\n  pip install --user {packages_str}")
            print(f"  pip install --break-system-packages {packages_str}")
    elif system == 'darwin':
        print(f"\n  brew install python3")
        print(f"  pip3 install --user {packages_str}")
    elif system == 'windows':
        print(f"\n  python -m pip install {packages_str}")
    
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

def check_command(command):
    return shutil.which(command) is not None

# ============================================================================
# Shortcuts creation
# ============================================================================
def create_shortcuts():
    system = get_system()
    if system == 'windows':
        with open('START_XONITER.bat', 'w') as f:
            f.write("""@echo off
title XONITER 2026 - Remote Command Executor
color 1F
echo ========================================
echo      XONITER 2026 - Remote Executor
echo      Developed by Darian Alberto Camacho Salas
echo      #Somos XONIDU
echo ========================================
echo.
python start.py
pause
""")
        print(f"{Colors.GREEN}Created START_XONITER.bat - Run as Administrator if needed{Colors.END}")
    elif system == 'linux':
        with open('START_XONITER.sh', 'w') as f:
            f.write("""#!/bin/bash
echo "========================================"
echo "      XONITER 2026 - Remote Executor"
echo "      Developed by Darian Alberto Camacho Salas"
echo "      #Somos XONIDU"
echo "========================================"
echo ""
python3 start.py
read -p "Press Enter to exit"
""")
        os.chmod('START_XONITER.sh', 0o755)
        print(f"{Colors.GREEN}Created START_XONITER.sh - Run with: ./START_XONITER.sh{Colors.END}")
    elif system == 'darwin':
        with open('START_XONITER.command', 'w') as f:
            f.write("""#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "      XONITER 2026 - Remote Executor"
echo "      Developed by Darian Alberto Camacho Salas"
echo "      #Somos XONIDU"
echo "========================================"
echo ""
python3 start.py
""")
        os.chmod('START_XONITER.command', 0o755)
        print(f"{Colors.GREEN}Created START_XONITER.command{Colors.END}")

# ============================================================================
# Main function
# ============================================================================
def main():
    if get_system() == 'windows':
        os.system('cls')
    else:
        os.system('clear')
    
    print_banner()
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', '/?']:
        mostrar_ayuda()
        if get_system() != 'windows':
            input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
        return
    
    # Check Python
    if not check_python():
        print(f"\n{Colors.RED}Error: Python is not installed{Colors.END}")
        print("Install Python from: https://www.python.org/downloads/")
        if get_system() != 'windows':
            input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
        sys.exit(1)
    
    python_version = subprocess.run(get_python_command() + ['--version'], capture_output=True, text=True).stdout.strip()
    print(f"{Colors.BOLD}Python:{Colors.END} {python_version}")
    
    # Check and install pip if needed
    pip_ok, pip_cmd = check_pip()
    if not pip_ok:
        print(f"\n{Colors.YELLOW}pip not found. Installing...{Colors.END}")
        system = get_system()
        success = False
        if system == 'linux':
            success = install_pip_linux()
        elif system == 'windows':
            success = install_pip_windows()
        elif system == 'darwin':
            success = install_pip_macos()
        
        if not success:
            print(f"{Colors.RED}Could not install pip automatically.{Colors.END}")
            print(f"{Colors.YELLOW}Please install pip manually and re-run.{Colors.END}")
            if get_system() != 'windows':
                input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
            sys.exit(1)
        else:
            print(f"{Colors.GREEN}pip installed successfully!{Colors.END}")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"\n{Colors.YELLOW}Missing dependencies: {', '.join(missing)}{Colors.END}")
        resp = input("Install automatically? (y/n): ")
        if resp.lower() == 'y':
            if not install_dependencies(missing):
                print(f"{Colors.RED}Installation failed.{Colors.END}")
                if get_system() != 'windows':
                    input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
                sys.exit(1)
        else:
            print(f"{Colors.YELLOW}Please install manually and re-run.{Colors.END}")
            if get_system() != 'windows':
                input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
            sys.exit(1)
    
    # Verify imports work
    if not verify_imports():
        print(f"\n{Colors.RED}Error: Cannot import required modules{Colors.END}")
        print(f"{Colors.YELLOW}Please check your installation.{Colors.END}")
        if get_system() != 'windows':
            input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
        sys.exit(1)
    
    # Find and run xoniter.py
    xoniter_path = get_xoniter_path()
    if not xoniter_path:
        print(f"\n{Colors.RED}Error: xoniter.py not found{Colors.END}")
        if get_system() != 'windows':
            input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
        sys.exit(1)
    
    print(f"\n{Colors.BOLD}Starting XONITER...{Colors.END}")
    print(f"{Colors.CYAN}To exit: Ctrl+C{Colors.END}")
    print("-" * 50)
    
    try:
        python_cmd = get_python_command()
        cmd = python_cmd + [xoniter_path] + sys.argv[1:]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stopped by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
    
    print(f"\n{Colors.GREEN}Thank you for using XONITER 2026{Colors.END}")
    print(f"{Colors.GREEN}Developed by Darian Alberto Camacho Salas{Colors.END}")
    print(f"{Colors.GREEN}#Somos XONIDU{Colors.END}")
    
    if get_system() != 'windows':
        input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")

if __name__ == '__main__':
    try:
        create_shortcuts()
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
