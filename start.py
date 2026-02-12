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
# 🔐 SEGURIDAD
# =========================

def is_command_blocked(command):
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
    if "pacman" in command and "--noconfirm" not in command:
        parts = command.split()
        for i, part in enumerate(parts):
            if part == "pacman":
                parts.insert(i + 1, "--noconfirm")
                break
        return " ".join(parts)
    return command


# =========================
# 🧠 SISTEMA
# =========================

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


def generate_terminal_qr(url):
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
        return f"No se pudo generar QR: {e}"


def run_with_sudo(command, timeout=None):
    global sudo_password

    if is_command_blocked(command):
        return "", "🚫 Comando bloqueado por seguridad.", -1, None

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
            return "", "", -1, f"Timeout después de {timeout} segundos."
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
            text=True,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )

        stdout, stderr = proc.communicate(
            input=f"{sudo_password}\n",
            timeout=timeout
        )

        return stdout, stderr, proc.returncode, None

    except subprocess.TimeoutExpired:
        if hasattr(os, 'setsid'):
            os.killpg(os.getpgid(proc.pid), 9)
        else:
            proc.terminate()
        return "", "", -1, f"Timeout después de {timeout} segundos."
    except Exception as e:
        return "", "", -1, str(e)


# =========================
# 🌐 WEB
# =========================

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

    try:
        user = getpass.getuser()
    except Exception:
        user = "desconocido"

    server_ip = get_ip_address()
    full_url = f"http://{server_ip}:{app.config.get('PORT', DEFAULT_PORT)}/"
    network_info = f"{server_ip} (puerto {app.config.get('PORT', DEFAULT_PORT)})"

    sudo_active = sudo_password is not None
    sudo_status = "Activado" if sudo_active else "No activado"

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
# 🚀 MAIN
# =========================

def main():
    global sudo_password

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-sudo", action="store_true")
    parser.add_argument("--no-qr", action="store_true")
    args = parser.parse_args()

    if not args.no_sudo:
        sudo_password = getpass.getpass("Ingresa tu contraseña sudo: ")

    server_ip = get_ip_address()
    full_url = f"http://{server_ip}:{args.port}/"

    print("\n" + "="*60)
    print("XONITER SIMPLE - SERVIDOR INICIADO")
    print("="*60)
    print(f"URL: {full_url}")
    print("="*60)

    if not args.no_qr:
        print(generate_terminal_qr(full_url))
        print("Escanea el QR para acceder desde tu teléfono.")
        print("="*60)

    print("Filtro activo: rm bloqueado")
    print("Pacman auto --noconfirm activado")
    print("Presiona Ctrl+C para detener\n")

    app.config["HOST"] = args.host
    app.config["PORT"] = args.port

    try:
        app.run(host=args.host, port=args.port, debug=False)
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        sudo_password = None
        sys.exit(0)


if __name__ == "__main__":
    main()
