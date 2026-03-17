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

## 📋 Requirements

- **Operating System**: Linux (any distribution), Windows, or macOS
- **Python**: Version 3.6 or higher
- **Dependencies**: Flask, qrcode, Pillow (automatically installed by xoniter.py)

## 🚀 Quick Start

### Option 1: Using the Installer (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/XONIDU/xoniter.git
   cd xoniter
   ```

2. Run the installer script:
   ```bash
   python xoniter.py
   ```

   The installer will:
   - Check your Python version
   - Detect your operating system and Linux distribution
   - Install all required dependencies automatically
   - Create platform-specific shortcuts
   - Launch the main XONITER application

### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/XONIDU/xoniter.git
   cd xoniter
   ```

2. Install dependencies:
   ```bash
   # For most Linux distributions (Ubuntu, Debian, Mint)
   pip install --user flask qrcode[pil] pillow

   # For Arch Linux, Manjaro, Fedora
   pip install --break-system-packages flask qrcode[pil] pillow

   # For Windows/macOS
   pip install flask qrcode[pil] pillow
   ```

3. Run XONITER:
   ```bash
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
| `--no-sudo` | Disable sudo mode | Enabled |
| `--no-qr` | Disable QR code display | Enabled |
| `-h, --help` | Show help message | - |

### How to Use

1. **Start the server** using one of the commands above
2. **Note the URL** displayed in the terminal (e.g., `http://192.168.1.100:5100/`)
3. **Open the URL** in a browser on any device on the same network
4. **Enter your sudo password** when prompted (if using sudo mode)
5. **Paste or type a command** in the text area and click "Execute Command"
6. **Review the output**:
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
| **Command filtering** | Blocks dangerous commands (rm by default) |
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

# List home directory
ls -la /home

# Check disk usage
df -h

# Check memory
free -h

# Network info
ip addr show

# Update package list (Debian/Ubuntu)
sudo apt update

# Update system (Arch)
sudo pacman -Syu
```

## ⚠️ Known Limitations

- ❌ No authentication (trusted networks only)
- ❌ Basic command filtering only (can be bypassed)
- ❌ No HTTPS (use a reverse proxy for encryption)
- ❌ Sudo password stored in memory
- ❌ Not suitable for multi-user environments

## 🔒 Security Recommendations

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
python xoniter.py
```

### Permission denied for binding to port
Use a port above 1024 (default is 5100) or run with sudo:
```bash
sudo python xoniter.py --host 0.0.0.0 --port 80
```

## 📞 Questions or Suggestions?

Contact the XONIDU team through:

- 📸 Instagram: [@xonidu](https://instagram.com/xonidu)
- 📘 Facebook: [xonidu](https://facebook.com/xonidu)
- 📧 Email: xonidu@gmail.com
- 👤 Creator: Darian Alberto Camacho Salas
