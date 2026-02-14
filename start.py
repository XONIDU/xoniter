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

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5100
DEFAULT_TIMEOUT = None

app = Flask(__name__)
sudo_password = None


# =========================
# 🔐 SECURITY
# =========================

def is_command_blocked(command):
    """
    Check if the command contains dangerous patterns.
    Currently blocks rm commands - can be extended.
    """
    forbidden_patterns = [
        r'\brm\b',
        r'/bin/rm',
        r';\s*rm',
        r'&&\s*rm',
        r'\|\s*rm',
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, command):
            return True
    return False


def auto_add_noconfirm(command):
    """
    Automatically add --noconfirm to pacman commands to prevent
    interactive prompts when running remotely.
    """
    if "pacman" in command and "--noconfirm" not in command:
        parts = command.split()
        for i, part in enumerate(parts):
            if part == "pacman":
                parts.insert(i + 1, "--noconfirm")
                break
        return " ".join(parts)
    return command


# =========================
# 🧠 SYSTEM
# =========================

def get_ip_address():
    """
    Get the actual IP address of the server (not localhost).
    Uses UDP connection trick to determine the primary IP.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def escape_single_quotes(command):
    """
    Properly escape single quotes for safe shell execution with sudo.
    This prevents command injection attacks.
    """
    return command.replace("'", "'\"'\"'")


def generate_terminal_qr(url):
    """
    Generate an ASCII QR code in the terminal for easy mobile access.
    Requires the 'qrcode' Python library.
    """
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_L

        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_L,
            box_size=1,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)

        matrix = qr.get_matrix()
        ascii_qr = ""
        for row in matrix:
            for col in row:
                ascii_qr += "██" if col else "  "
            ascii_qr += "\n"

        return ascii_qr
    except Exception as e:
        return f"Could not generate QR code: {e}"


def run_with_sudo(command, timeout=None):
    """
    Execute a command, optionally with sudo privileges.
    Handles timeout, command blocking, and error cases.
    """
    global sudo_password

    # Security check: block dangerous commands
    if is_command_blocked(command):
        return "", "🚫 Command blocked for security reasons.", -1, None

    # Safety: auto-add --noconfirm for pacman
    command = auto_add_noconfirm(command)

    # Case 1: No sudo password provided - run as current user
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

    # Case 2: Sudo password provided - run with elevated privileges
    escaped = escape_single_quotes(command)
    sudo_cmd = f"sudo -S bash -c '{escaped}'"

    try:
        proc = subprocess.Popen(
            sudo_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )

        stdout, stderr = proc.communicate(
            input=f"{sudo_password}\n",
            timeout=timeout
        )

        return stdout, stderr, proc.returncode, None

    except subprocess.TimeoutExpired:
        # Kill the entire process group if timeout occurs
        if hasattr(os, 'setsid'):
            os.killpg(os.getpgid(proc.pid), 9)
        else:
            proc.terminate()
        return "", "", -1, f"Timeout after {timeout} seconds."
    except Exception as e:
        return "", "", -1, str(e)


# =========================
# 🌐 WEB INTERFACE
# =========================

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route: displays the command form and handles submissions.
    """
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

        # Parse timeout value
        if timeout_field:
            try:
                timeout = float(timeout_field)
                timeout_value = timeout_field
            except ValueError:
                timeout = None

        if cmd_text:
            ran = True
            start = time.time()
            stdout, stderr, rc, error_msg = run_with_sudo(cmd_text, timeout)
            elapsed = f"{time.time() - start:.2f}s"
            if error_msg:
                error = error_msg

    # Get system information for display
    try:
        user = getpass.getuser()
    except Exception:
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


# =========================
# 🚀 MAIN ENTRY POINT
# =========================

def main():
    """
    Main function: parses arguments, requests sudo password if needed,
    and starts the Flask server.
    """
    global sudo_password

    parser = argparse.ArgumentParser(description="XONITER - Web-based remote command executor")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind to (default: {DEFAULT_PORT})")
    parser.add_argument("--no-sudo", action="store_true", help="Disable sudo mode (run without privileges)")
    parser.add_argument("--no-qr", action="store_true", help="Disable QR code display")
    args = parser.parse_args()

    # Ask for sudo password unless disabled
    if not args.no_sudo:
        sudo_password = getpass.getpass("Enter your sudo password: ")

    server_ip = get_ip_address()
    full_url = f"http://{server_ip}:{args.port}/"

    # Display startup information
    print("\n" + "="*60)
    print("XONITER - Server Started")
    print("="*60)
    print(f"URL: {full_url}")
    print("="*60)

    # Show QR code for mobile access
    if not args.no_qr:
        print(generate_terminal_qr(full_url))
        print("Scan the QR code to access from your phone.")
        print("="*60)

    print("Security filters: rm commands blocked")
    print("Pacman auto --noconfirm enabled")
    print("Press Ctrl+C to stop\n")

    app.config["HOST"] = args.host
    app.config["PORT"] = args.port

    try:
        app.run(host=args.host, port=args.port, debug=False)
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sudo_password = None
        sys.exit(0)


if __name__ == "__main__":
    main()
