#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONITER 2026 - Lightweight Remote Command Executor Installer
This script runs xoniter.py and verifies dependencies with multiple fallback options
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
# Detección del sistema
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
                if 'ubuntu' in content or 'debian' in content or 'mint' in content:
                    return 'debian-based'
                elif 'arch' in content or 'manjaro' in content:
                    return 'arch-based'
                elif 'fedora' in content:
                    return 'fedora'
        if shutil.which('apt'):
            return 'debian-based'
        elif shutil.which('pacman'):
            return 'arch-based'
        elif shutil.which('dnf'):
            return 'fedora'
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

def get_pip_command():
    return [sys.executable, '-m', 'pip']

def get_install_flags():
    flags = []
    sistema = get_system()
    distro = get_linux_distro()
    if sistema == 'linux':
        if distro in ['arch-based', 'fedora']:
            flags.append('--break-system-packages')
        else:
            flags.append('--user')
    elif sistema == 'darwin':
        flags.append('--user')
    return flags

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_xoniter_path():
    """Detecta la ruta de xoniter.py en múltiples ubicaciones"""
    script_dir = get_script_dir()
    rutas = [
        os.path.join(script_dir, 'xoniter.py'),
        '/usr/share/xoniter/xoniter.py',
        os.path.join(os.path.expanduser("~"), '.xoniter', 'xoniter.py'),
        os.path.join(os.getcwd(), 'xoniter.py')
    ]
    for r in rutas:
        if os.path.exists(r):
            return r
    return None

def print_banner():
    sistema = get_system()
    distro = get_linux_distro()
    sistema_texto = {
        'windows': 'WINDOWS',
        'linux': f'LINUX ({distro.upper()})' if distro else 'LINUX',
        'darwin': 'MACOS'
    }.get(sistema, 'UNKNOWN')
    
    banner = f"""
{Colors.PURPLE}{Colors.BOLD}═══════════════════════════════════════════════════════════
                    XONITER 2026 v1.0                    
              Lightweight Remote Command Executor            
              Execute commands on headless systems          
              via web interface                             
                                                          
              System detected: {sistema_texto}            
                                                          
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
# Verificación de dependencias
# ============================================================================
def check_python():
    try:
        cmd = get_python_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def check_pip():
    try:
        cmd = get_pip_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def install_pip_linux():
    distro = get_linux_distro()
    print(f"{Colors.YELLOW}Installing pip on Linux ({distro})...{Colors.END}")
    if distro == 'debian-based':
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=False)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'python3-pip'], check=True)
            return True
        except:
            return False
    elif distro == 'arch-based':
        try:
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'python-pip'], check=True)
            return True
        except:
            return False
    elif distro == 'fedora':
        try:
            subprocess.run(['sudo', 'dnf', 'install', '-y', 'python3-pip'], check=True)
            return True
        except:
            return False
    return False

def install_pip_windows():
    print(f"{Colors.YELLOW}Installing pip on Windows...{Colors.END}")
    try:
        subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], check=True)
        return True
    except:
        return False

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
    system = get_system()
    distro = get_linux_distro()
    
    strategies = []
    strategies.append([sys.executable, '-m', 'pip', 'install'])
    if system != 'windows':
        strategies.append([sys.executable, '-m', 'pip', 'install', '--user'])
    if system == 'linux':
        strategies.append([sys.executable, '-m', 'pip', 'install', '--break-system-packages'])
        strategies.append([sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages'])
    if check_command('pip3'):
        strategies.append(['pip3', 'install'])
        if system == 'linux':
            strategies.append(['pip3', 'install', '--break-system-packages'])
            strategies.append(['pip3', 'install', '--user'])
    if check_command('pip'):
        strategies.append(['pip', 'install'])
    
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
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}  Timeout{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}  Error: {str(e)[:100]}{Colors.END}")
    return False

def install_dependencies(missing):
    if not missing:
        return True
    print(f"\n{Colors.BOLD}Installing missing dependencies...{Colors.END}")
    if install_with_pip(missing):
        print(f"{Colors.GREEN}All dependencies installed!{Colors.END}")
        return True
    print(f"{Colors.RED}Automatic installation failed.{Colors.END}")
    return False

def check_command(command):
    return shutil.which(command) is not None

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
# Función principal
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
    
    if not check_python():
        print(f"\n{Colors.RED}Error: Python is not installed{Colors.END}")
        sys.exit(1)
    
    python_version = subprocess.run(get_python_command() + ['--version'], capture_output=True, text=True).stdout.strip()
    print(f"{Colors.BOLD}Python:{Colors.END} {python_version}")
    
    if not check_pip() and get_system() == 'linux':
        print(f"\n{Colors.YELLOW}pip not found. Installing...{Colors.END}")
        if not install_pip_linux():
            print(f"{Colors.RED}Could not install pip automatically.{Colors.END}")
            sys.exit(1)
    
    missing = check_dependencies()
    if missing:
        print(f"\n{Colors.YELLOW}Missing dependencies: {', '.join(missing)}{Colors.END}")
        resp = input("Install automatically? (y/n): ")
        if resp.lower() == 'y':
            if not install_dependencies(missing):
                print(f"{Colors.YELLOW}Manual installation required.{Colors.END}")
                sys.exit(1)
    
    xoniter_path = get_xoniter_path()
    if not xoniter_path:
        print(f"\n{Colors.RED}Error: xoniter.py not found{Colors.END}")
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

if __name__ == '__main__':
    try:
        create_shortcuts()
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
