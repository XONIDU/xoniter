# XONITER - Lightweight Remote Command Executor

XONITER provides a minimal web interface to send and execute commands on a Linux machine from another device on the same local network. It is designed to streamline command input on systems without a graphical environment (pure terminal) from a mobile phone or laptop on the LAN.

## 🎯 Goal

Make it easy to run Linux commands remotely when:

- You're working on a headless server
- SSH is not practical at the moment
- You want to quickly test something from your phone
- You need to help someone else run commands on their system

## ⚠️ Security Warning

**This tool is for TRUSTED LOCAL NETWORKS ONLY.** It provides no authentication and executes arbitrary commands. Never expose it to the internet or untrusted networks.

**The tool will ALWAYS ask for confirmation in the terminal before executing any command.** No command runs without your explicit approval (y/n).

## 📋 Requirements

- **Operating System**: Linux (any distribution), Windows, or macOS
- **Python**: Version 3.6 or higher
- **Dependencies**: Flask, qrcode, Pillow (automatically installed)

## 🚀 Quick Start

### Option 1: Install from AUR (Arch Linux / EndeavourOS / Manjaro)

```bash
yay -S xoniter
```

### Option 2: Using the Installer (Recommended for other distros)

```bash
git clone https://github.com/XONIDU/xoniter.git
cd xoniter
python start.py
```

The installer will:
- Check your Python version
- Detect your operating system and Linux distribution
- Install all required dependencies automatically
- Create platform-specific shortcuts
- Launch the main XONITER application

### Option 3: Manual Installation

```bash
git clone https://github.com/XONIDU/xoniter.git
cd xoniter

# Install dependencies
# For Ubuntu/Debian/Mint
pip install --user flask qrcode pillow

# For Arch Linux/Manjaro/Fedora
pip install --break-system-packages flask qrcode pillow

# For Windows/macOS
pip install flask qrcode pillow

# Run XONITER
python xoniter.py --host 0.0.0.0 --port 5100
```

## 📖 Usage

### Basic Execution

```bash
# Run with default settings (localhost only)
python xoniter.py

# Expose on local network
python xoniter.py --host 0.0.0.0 --port 5100

# Secure mode (local only, no sudo)
python xoniter.py --host 127.0.0.1 --port 5100 --no-sudo

# Disable QR code
python xoniter.py --no-qr
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host HOST` | Host to bind to | `0.0.0.0` |
| `--port PORT` | Port to bind to | `5100` |
| `--no-sudo` | Disable sudo mode (run without privileges) | Enabled |
| `--no-qr` | Disable QR code display | Enabled |
| `-h, --help` | Show help message | - |

### How to Use

1. **Start the server** using one of the commands above
2. **Note the URL** displayed in the terminal (e.g., `http://192.168.1.100:5100/`)
3. **Open the URL** in a browser on any device on the same network
4. **Enter your sudo password** when prompted (if using sudo mode)
5. **Paste or type a command** in the text area and click "Execute Command"
6. **Check the terminal** - XONITER will ask: `[CONFIRM] Allow this command? (y/n):`
7. **Type `y` and press Enter** to execute, or `n` to cancel
8. **Review the output**:
   - STDOUT (standard output)
   - STDERR (standard error)
   - Return code
   - Execution time

### Optional Timeout

Use the timeout field to limit how long a command can run (in seconds). This prevents commands from hanging indefinitely.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Clean web interface** | Simple, mobile-friendly design |
| **Sudo support** | Optional password elevation |
| **Command timeout** | Prevent runaway processes |
| **QR code generation** | Scan from phone for instant access |
| **No command restrictions** | Execute any command you need |
| **Confirmation before execution** | Always asks "Allow this command? (y/n)" in terminal |
| **Pacman safety** | Auto-adds --noconfirm for Arch Linux |
| **Cross-platform** | Works on Linux, Windows, and macOS |
| **Automatic IP detection** | Detects and displays local IP |
| **Platform shortcuts** | Creates .bat (Windows), .sh (Linux), .command (macOS) |

## 📁 Project Structure

```
xoniter/
├── xoniter.py           # Main application (Python/Flask)
├── start.py             # Installer/launcher script
├── templates/
│   └── index.html       # Web interface template
├── README.md            # This file
└── requirements.txt     # Dependencies (optional)
```

## 🛠️ Platform-Specific Notes

### Linux
- **Arch/Manjaro/Fedora**: The installer automatically uses `--break-system-packages`
- **Ubuntu/Debian/Mint**: Uses `--user` flag for safe installation
- All distributions: Creates `START_XONITER.sh` launcher

### Windows
- Creates `START_XONITER.bat` for easy double-click execution
- No special package manager flags needed

### macOS
- Creates `START_XONITER.command` launcher
- Uses `--user` flag for installations

## 🔧 Example Commands to Try

```bash
# Basic system info
uname -a
df -h
free -h
ip addr show

# Fastfetch (if installed)
fastfetch
neofetch

# File operations
ls -la /home
cat /var/log/syslog | tail -20

# Package management
sudo apt update && sudo apt upgrade -y  # Debian/Ubuntu
sudo pacman -Syu                         # Arch Linux (auto-adds --noconfirm)

# Service management
systemctl status sshd
sudo systemctl restart networking

# Network tools
ping -c 4 google.com
ss -tuln
```

## ⚠️ Known Limitations

- ❌ No authentication (trusted networks only)
- ❌ No HTTPS (use a reverse proxy for encryption)
- ❌ Sudo password stored in memory
- ❌ Not suitable for multi-user environments

## 🔒 Security Model

XONITER uses a **confirmation-first approach**:

1. All commands are allowed (no restrictions)
2. **Every command requires confirmation** in the terminal before execution
3. You must type `y` and press Enter for each command
4. Commands are cancelled if you type `n` or don't respond

This means:
- ✅ You are always in control
- ✅ No accidental command execution
- ✅ You can see what will run before it runs
- ⚠️ Only use on trusted networks

### Security Recommendations

For safer deployment:

- Use a firewall to restrict access to specific IPs
- Run with `--no-sudo` when possible
- Bind to `127.0.0.1` and use SSH tunneling
- Add HTTP Basic Authentication (modify the code)
- Use a reverse proxy with SSL/TLS
- Run in a container with limited permissions

## 🐛 Troubleshooting

### "Command not found" for pip/pip3

```bash
# Ubuntu/Debian
sudo apt install python3-pip

# Arch/Manjaro
sudo pacman -S python-pip

# Fedora
sudo dnf install python3-pip
```

### Import errors

Run the installer again:

```bash
python start.py
```

### Permission denied for binding to port

Use a port above 1024 (default is 5100) or run with sudo:

```bash
sudo python xoniter.py --host 0.0.0.0 --port 80
```

### "Command not allowed" error

If you see this error, your configuration may have restrictions. Edit `~/.xoniter/config.json`:

```json
{
    "allowed_commands": [],
    "blocked_patterns": [],
    "ask_for_confirmation": true
}
```

## 📞 Questions or Suggestions?

Contact the XONIDU team through:

- 📸 Instagram: [@xonidu](https://instagram.com/xonidu)
- 📘 Facebook: [xonidu](https://facebook.com/xonidu)
- 📧 Email: xonidu@gmail.com
- 👤 Creator: Darian Alberto Camacho Salas

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Flask framework for the web interface
- Python community for the amazing libraries
- Arch Linux community for AUR support
- UNAM FESC for the educational environment

---

**#Somos XONIDU
