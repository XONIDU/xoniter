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

## 🛠️ Quick Installation

Install Python 3 and Flask:

### Arch Linux
```bash
sudo pacman -S python-pip
pip install flask
```

### Ubuntu / Debian
```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install flask
```

### Windows
```bash
pip install flask
```

### macOS (Homebrew)
```bash
brew install python3
pip3 install flask
```

### Optional: QR Code Support
To generate QR codes in the terminal, install the qrcode library:
```bash
pip install qrcode  # or pip3 install qrcode
```

## ▶️ Execution

From the project folder:

### Expose on LAN (accessible from other devices)
```bash
python start.py
# or
python3 start.py --host 0.0.0.0 --port 5100
```

### Restrict to local machine only (safer for testing)
```bash
python start.py --host 127.0.0.1 --port 5100
```

### Run without sudo
```bash
python start.py --no-sudo
```

### Disable QR code
```bash
python start.py --no-qr
```

## 🧾 Usage

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

## 📸 Features

| Feature | Description |
|---------|-------------|
| **Clean web interface** | Simple, mobile-friendly design |
| **Sudo support** | Optional password elevation |
| **Command timeout** | Prevent runaway processes |
| **QR code generation** | Scan from phone for instant access |
| **Command filtering** | Blocks dangerous commands (rm by default) |
| **Pacman safety** | Auto-adds --noconfirm for Arch Linux |
| **Cross-platform** | Works on any Linux with Python 3 |

## 📁 Project Structure

```
xoniter/
├── start.py          # Main application
└── templates/
    └── index.html      # Web interface template
```

## 🔧 Command Line Options

| Option | Description |
|--------|-------------|
| `--host HOST` | Host to bind to (default: 0.0.0.0) |
| `--port PORT` | Port to bind to (default: 5100) |
| `--no-sudo` | Disable sudo mode (run without privileges) |
| `--no-qr` | Disable QR code display |

## ⚡ Example Commands to Try

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
1. **Use a firewall** to restrict access to specific IPs
2. **Run with --no-sudo** when possible
3. **Bind to 127.0.0.1** and use SSH tunneling
4. **Add HTTP Basic Authentication** (modify the code)
5. **Use a reverse proxy** with SSL/TLS
6. **Run in a container** with limited permissions

## ❓ Questions or Suggestions?

Contact the XONIDU team through:

- 📸 **Instagram:** [@xonidu](https://instagram.com/xonidu)
- 📘 **Facebook:** [xonidu](https://facebook.com/xonidu)
- 📧 **Email:** xonidu@gmail.com
- 👤 **Creator:** Darian Alberto Camacho Salas
