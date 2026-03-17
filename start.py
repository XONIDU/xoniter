#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONITER 2026 - Lightweight Remote Command Executor
This script runs xoniter.py and verifies dependencies
Developed by: Darian Alberto Camacho Salas
#Somos XONIDU
"""

import subprocess
import sys
import os
import platform
import shutil
import importlib.util

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
        """Check if terminal supports colors"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                return kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                return False
        return True

# Disable colors if not supported
if not Colors.supports_color():
    for attr in dir(Colors):
        if not attr.startswith('_') and attr != 'supports_color':
            setattr(Colors, attr, '')

def get_system():
    """Detect operating system"""
    return platform.system().lower()

def get_linux_distro():
    """Detect Linux distribution"""
    if get_system() != 'linux':
        return None    
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content:
                    return 'ubuntu'
                elif 'debian' in content:
                    return 'debian'
                elif 'fedora' in content:
                    return 'fedora'
                elif 'centos' in content:
                    return 'centos'
                elif 'arch' in content:
                    return 'arch'
                elif 'manjaro' in content:
                    return 'manjaro'
                elif 'mint' in content:
                    return 'mint'
        return 'linux-generic'
    except:
        return 'linux-generic'

def get_python_command():
    """Get correct Python command"""
    if get_system() == 'windows':
        return ['python']
    else:
        try:
            subprocess.run(['python3', '--version'], capture_output=True, check=True)
            return ['python3']
        except:
            return ['python']

def print_banner():
    """Display XONITER banner"""
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
    """Verify Python is installed"""
    try:
        cmd = get_python_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def check_command(command):
    """Check if a command exists"""
    return shutil.which(command) is not None

def check_python_module(module_name):
    """Check if a Python module is installed"""
    return importlib.util.find_spec(module_name) is not None

def check_dependencies():
    """Check required Python dependencies"""
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
    
    # Check system dependencies for Linux
    if get_system() == 'linux':
        # XONITER doesn't require system dependencies like xdotool/scrot
        # But we check if the system is ready for network binding
        pass
    
    return missing

def install_dependencies(missing):
    """Install missing dependencies"""
    if not missing:
        return True
    
    print(f"\n{Colors.BOLD}Installing missing dependencies...{Colors.END}")
    
    system = get_system()
    distro = get_linux_distro()
    
    # Python packages to install
    python_packages = [p for p in missing if not p.startswith('system-')]
    
    # Install Python packages
    if python_packages:
        print(f"Python packages to install: {', '.join(python_packages)}")
        
        # Build installation command
        cmd = [sys.executable, '-m', 'pip', 'install']
        
        # Add options based on system
        if system == 'linux':
            if distro in ['arch', 'manjaro', 'fedora']:
                cmd.append('--break-system-packages')
                print(f"{Colors.YELLOW}Using --break-system-packages for {distro}{Colors.END}")
            else:
                cmd.append('--user')
        elif system == 'darwin':
            cmd.append('--user')
        
        cmd.extend(python_packages)
        
        # Attempt installation
        try:
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print(f"{Colors.GREEN}Python dependencies installed successfully{Colors.END}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}Error installing dependencies: {e}{Colors.END}")
            print(f"\n{Colors.YELLOW}Trying alternative method...{Colors.END}")
            
            # Second attempt: just --user
            try:
                cmd2 = [sys.executable, '-m', 'pip', 'install', '--user'] + python_packages
                subprocess.run(cmd2, check=True)
                print(f"{Colors.GREEN}Installed with --user{Colors.END}")
            except:
                print(f"{Colors.RED}Installation failed{Colors.END}")
                print(f"\nInstall manually:")
                print(f"  pip install {' '.join(python_packages)}")
                if system == 'linux' and distro in ['arch', 'manjaro', 'fedora']:
                    print(f"  Or with: pip install --break-system-packages {' '.join(python_packages)}")
    
    return True

def show_help():
    """Show usage help"""
    help_text = f"""
{Colors.BOLD}XONITER USAGE:{Colors.END}

  python xoniter.py [options]

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
    python xoniter.py

  Expose on local network:
    python xoniter.py --host 0.0.0.0 --port 5100

  Secure mode (local only, no sudo):
    python xoniter.py --host 127.0.0.1 --port 5100 --no-sudo

  Disable QR code:
    python xoniter.py --no-qr

{Colors.BOLD}WARNING:{Colors.END}

  This tool is for TRUSTED LOCAL NETWORKS ONLY.
  It provides no authentication and executes arbitrary commands.
  Never expose it to the internet or untrusted networks.
    """
    print(help_text)

def verify_imports():
    """Verify that all required imports work"""
    print(f"\n{Colors.BOLD}Verifying imports...{Colors.END}")
    
    modules = [
        ('flask', 'flask'),
        ('qrcode', 'qrcode'),
        ('PIL', 'Pillow'),
    ]
    
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
    """Create shortcuts for each system"""
    system = get_system()
    
    if system == 'windows':
        # Create .bat for Windows
        with open('START_XONITER.bat', 'w') as f:
            f.write("""@echo off
title XONITER 2026 - Remote Command Executor
color 1F
echo ========================================
echo      XONITER 2026 - Remote Executor
echo      Developed by Darian Alberto
echo ========================================
echo.
python xoniter.py
pause
""")
        print(f"{Colors.GREEN}Created START_XONITER.bat - Double-click to run{Colors.END}")
    
    elif system == 'linux':
        # Create .sh for Linux
        with open('START_XONITER.sh', 'w') as f:
            f.write("""#!/bin/bash
echo "========================================"
echo "      XONITER 2026 - Remote Executor"
echo "      Developed by Darian Alberto"
echo "========================================"
echo ""
python3 xoniter.py
read -p "Press Enter to exit"
""")
        os.chmod('START_XONITER.sh', 0o755)
        print(f"{Colors.GREEN}Created START_XONITER.sh - Run with: ./START_XONITER.sh{Colors.END}")
    
    elif system == 'darwin':
        # Create .command for Mac
        with open('START_XONITER.command', 'w') as f:
            f.write("""#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "      XONITER 2026 - Remote Executor"
echo "      Developed by Darian Alberto"
echo "========================================"
echo ""
python3 xoniter.py
""")
        os.chmod('START_XONITER.command', 0o755)
        print(f"{Colors.GREEN}Created START_XONITER.command - Double-click to run{Colors.END}")

def main():
    """Main function"""
    # Clear screen
    if get_system() == 'windows':
        os.system('cls')
    else:
        os.system('clear')
    
    # Show banner
    print_banner()
    
    # Check for help argument
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', '/?']:
        show_help()
        input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
        return
    
    # Verify Python
    if not check_python():
        print(f"\n{Colors.RED}Error: Python is not installed{Colors.END}")
        print("Install Python from: https://www.python.org/downloads/")
        input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
        return
    
    python_version = subprocess.run(get_python_command() + ['--version'], 
                                   capture_output=True, text=True).stdout.strip()
    print(f"{Colors.BOLD}Python:{Colors.END} {python_version}")
    print(f"{Colors.BOLD}Directory:{Colors.END} {os.path.dirname(os.path.abspath(__file__))}")
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"\n{Colors.YELLOW}Missing dependencies{Colors.END}")
        response = input("Install automatically? (y/n): ")
        
        if response.lower() == 'y':
            install_dependencies(missing)
        else:
            print(f"\nYou can install them manually with:")
            print("  pip install flask qrcode[pil] pillow")
            system = get_system()
            distro = get_linux_distro()
            if system == 'linux' and distro in ['arch', 'manjaro', 'fedora']:
                print("  Or with: pip install --break-system-packages flask qrcode[pil] pillow")
    
    # Verify that xoniter.py exists
    if not os.path.exists('xoniter.py'):
        print(f"\n{Colors.RED}Error: xoniter.py not found{Colors.END}")
        print("Make sure xoniter.py is in the same directory")
        print("\nYou can download it from:")
        print("  https://github.com/XONIDU/xoniter")
        input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
        return
    
    # Verify that imports work
    print(f"\n{Colors.BOLD}Verifying everything works...{Colors.END}")
    if not verify_imports():
        print(f"\n{Colors.RED}Error: Cannot import required modules{Colors.END}")
        print("The program cannot continue without these dependencies")
        response = input("\nTry to fix imports by reinstalling? (y/n): ")
        if response.lower() == 'y':
            missing = ['flask', 'qrcode[pil]', 'pillow']
            install_dependencies(missing)
            if not verify_imports():
                print(f"\n{Colors.RED}Still having issues. Please install manually.{Colors.END}")
                input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
                return
        else:
            input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
            return
    
    print(f"\n{Colors.BOLD}Starting XONITER...{Colors.END}")
    print(f"{Colors.BOLD}To exit at any time:{Colors.END} Ctrl+C")
    print("-" * 60)
    
    # EXECUTE xoniter.py - THIS IS THE IMPORTANT PART
    try:
        python_cmd = get_python_command()
        
        # Pass through any command line arguments
        cmd = python_cmd + ['xoniter.py'] + sys.argv[1:]
        
        print(f"Running: {' '.join(cmd)}")
        print("-" * 60)
        
        # Execute xoniter.py
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print(f"\n{Colors.RED}Error: xoniter.py exited with code {result.returncode}{Colors.END}")
            
    except FileNotFoundError:
        print(f"\n{Colors.RED}Error: Could not find xoniter.py{Colors.END}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Program stopped by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error running xoniter.py: {e}{Colors.END}")
    
    print(f"\n{Colors.BLUE}Thank you for using XONITER 2026{Colors.END}")
    print(f"{Colors.BLUE}Developed by Darian Alberto Camacho Salas{Colors.END}")
    print(f"{Colors.BLUE}#Somos XONIDU{Colors.END}")
    
    # Pause at the end (except Windows which already has pause from .bat)
    if get_system() != 'windows':
        input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")

if __name__ == '__main__':
    try:
        # Create shortcuts
        create_shortcuts()
        
        # Run main program
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
