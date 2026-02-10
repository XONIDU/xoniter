from flask import Flask, request, render_template_string
import subprocess
import argparse
import html
import os
import time
import getpass
import qrcode
import socket
import sys

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5100
DEFAULT_TIMEOUT = None  # segundos; None = sin tiempo límite

app = Flask(__name__)

# Variable global para almacenar la contraseña de sudo
sudo_password = None

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Xoniter Simple - Español</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 18px; background:#f7f7f9; color:#222; }
    .container { max-width:900px; margin:0 auto; background:#fff; padding:18px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.08); }
    textarea { width:100%; height:160px; padding:10px; font-family: monospace; font-size:14px; }
    pre { background:#0b0b0b; color:#e6e6e6; padding:12px; border-radius:6px; overflow:auto; }
    input[type=text], input[type=number], button { padding:10px; margin-top:8px; }
    .warn { background:#fff3cd; padding:10px; border-radius:6px; color:#856404; }
    .info { background:#d1ecf1; padding:10px; border-radius:6px; color:#0c5460; }
    .success { background:#d4edda; padding:10px; border-radius:6px; color:#155724; }
    .meta { color:#555; font-size:0.9rem; }
    .btn { display:inline-block; padding:10px 20px; background:#007bff; color:white; border:none; border-radius:5px; cursor:pointer; text-decoration:none; }
    .btn:hover { background:#0056b3; }
    .url-box { background:#e9ecef; padding:10px; border-radius:6px; font-family:monospace; word-break:break-all; margin:10px 0; }
  </style>
</head>
<body>                                                                                                                                                                                        
  <div class="container">                                                                                                                                                                     
    <h1>Xoniter Simple - Español</h1>                                                                                                                                                                   
    <p class="warn"><strong>Advertencia:</strong> Esta página ejecuta comandos en el sistema. No expongas a redes no confiables.</p>
    
    {% if sudo_active %}
    <div class="success">
      <strong>✓ Modo Sudo Activado:</strong> Ejecutando con privilegios elevados<br>
      <small>Todos los comandos se ejecutan automáticamente con sudo</small>
    </div>
    {% else %}
    <div class="warn">
      <strong>⚠ Modo Sudo NO Activado:</strong> Ejecutando sin privilegios elevados<br>
      <small>Los comandos no tendrán permisos de sudo</small>
    </div>
    {% endif %}
    
    <!-- Información de acceso -->
    <div class="info">
      <h3>Acceso al Servidor</h3>
      <p>Usa una de estas URLs para acceder desde otros dispositivos:</p>
      <div class="url-box">{{ full_url }}</div>
      <p><small>Red: {{ network_info }}</small></p>
      <p><em>Nota: Escanea el código QR mostrado en la terminal para acceso rápido</em></p>
    </div>
    
    <p class="meta">Servidor: <strong>{{ host }}:{{ port }}</strong> &nbsp; • &nbsp; Usuario: <strong>{{ user }}</strong> &nbsp; • &nbsp; Sudo: <strong>{{ sudo_status }}</strong></p>                                                                  
                                                                                                                                                                                              
    <form method="post">                                                                                                                                                                      
      <label for="cmd">Comando (pega el comando completo o múltiples comandos):</label><br>                                                                                                     
      <textarea name="cmd" id="cmd" placeholder="Ejemplo: ls -la /home o uname -a">{{ cmd_escaped }}</textarea><br>                                                                              
      <label for="timeout">Tiempo límite (segundos, vacío = sin límite):</label>                                                                                                                     
      <input type="number" name="timeout" id="timeout" min="1" value="{{ timeout_value }}"><br>                                                                                               
      <button type="submit" class="btn">Ejecutar con Sudo</button>                                                                                                                                                      
    </form>

    {% if ran %}
      <h3>Comando Ejecutado:</h3>
      <pre>{{ command }}</pre>

      {% if error %}
        <h3 style="color:crimson">Error:</h3>
        <pre style="color:crimson">{{ error }}</pre>
      {% endif %}

      <h3>Salida STDOUT:</h3>
      <pre>{{ stdout }}</pre>

      <h3>Salida STDERR:</h3>
      <pre>{{ stderr }}</pre>

      <p class="meta">Código de retorno: <strong>{{ rc }}</strong> — Tiempo: <strong>{{ elapsed }}</strong></p>
    {% endif %}

    <p class="meta">Consejo: Para limitar la exposición, vincula a 127.0.0.1 o usa un firewall. Todos los comandos se ejecutan con sudo si está activado.</p>
  </div>
</body>
</html>
"""

def get_ip_address():
    """Obtiene la dirección IP de la interfaz de red principal"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # Conectar a una IP dummy para obtener nuestra IP local
            s.connect(('10.254.254.254', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())

def escape_single_quotes(command):
    """Escapa las comillas simples en un comando para bash -c"""
    return command.replace("'", "'\"'\"'")

def run_with_sudo(command, timeout=None):
    """Ejecuta un comando con privilegios sudo usando la contraseña almacenada"""
    global sudo_password
    
    # Verificar si tenemos contraseña de sudo
    if not sudo_password:
        # Intentar ejecutar sin sudo
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
            return "", "", -1, f"Comando expirado después de {timeout} segundos."
        except Exception as e:
            return "", "", -1, str(e)
    
    # Escapar comillas simples para bash -c
    escaped_command = escape_single_quotes(command)
    
    # Construir el comando sudo correctamente
    sudo_cmd = f"sudo -S bash -c '{escaped_command}'"
    
    try:
        start = time.time()
        # Crear el proceso con subprocess
        proc = subprocess.Popen(
            sudo_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )
        
        try:
            # Enviar la contraseña de sudo y capturar salida
            stdout, stderr = proc.communicate(input=f"{sudo_password}\n", timeout=timeout)
            rc = proc.returncode
            elapsed = time.time() - start
            
            return stdout, stderr, rc, None
        except subprocess.TimeoutExpired:
            # Terminar el proceso y todos sus hijos
            if hasattr(os, 'setsid'):
                os.killpg(os.getpgid(proc.pid), 9)
            else:
                proc.terminate()
                proc.wait(timeout=2)
            return "", "", -1, f"Comando expirado después de {timeout} segundos."
            
    except Exception as e:
        return "", "", -1, f"Error ejecutando comando: {str(e)}"

def generate_terminal_qr(url):
    """Genera un código QR en formato ASCII para la terminal"""
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_L
        
        # Crear código QR
        qr = qrcode.QRCode(
            version=2,
            error_correction=ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Obtener el código QR como texto
        qr_text = qr.get_matrix()
        
        # Construir representación ASCII
        ascii_qr = ""
        for row in qr_text:
            for pixel in row:
                if pixel:
                    ascii_qr += "██"
                else:
                    ascii_qr += "  "
            ascii_qr += "\n"
        
        return ascii_qr
    except ImportError:
        return ""

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
                timeout_value = ""
        else:
            timeout = DEFAULT_TIMEOUT
            timeout_value = ""

        if cmd_text:
            ran = True
            start_time = time.time()
            
            # Ejecutar con privilegios sudo
            stdout, stderr, rc, error_msg = run_with_sudo(cmd_text, timeout)
            elapsed = f"{time.time() - start_time:.2f}s"
            
            if error_msg:
                error = error_msg

    # Escapar salidas para renderizado HTML seguro
    cmd_escaped = html.escape(cmd_text)
    stdout_esc = html.escape(stdout)
    stderr_esc = html.escape(stderr)
    error_esc = html.escape(error)

    try:
        user = getpass.getuser()
    except Exception:
        user = os.getenv("USER") or "desconocido"
    
    # Obtener la IP real del servidor
    server_ip = get_ip_address()
    full_url = f"http://{server_ip}:{app.config.get('PORT', DEFAULT_PORT)}/"
    
    # Información de red
    network_info = f"{server_ip} (puerto {app.config.get('PORT', DEFAULT_PORT)})"
    
    # Estado de sudo
    sudo_active = sudo_password is not None
    sudo_status = "Activado" if sudo_active else "No activado"

    return render_template_string(
        PAGE,
        host=app.config.get("HOST", DEFAULT_HOST),
        port=app.config.get("PORT", DEFAULT_PORT),
        full_url=full_url,
        network_info=network_info,
        user=user,
        sudo_status=sudo_status,
        sudo_active=sudo_active,
        cmd_escaped=cmd_escaped,
        ran=ran,
        command=cmd_escaped,
        stdout=stdout_esc,
        stderr=stderr_esc,
        rc=rc,
        elapsed=elapsed,
        error=error_esc,
        timeout_value=timeout_value
    )

def verify_sudo_password(password):
    """Verifica si la contraseña de sudo es correcta"""
    try:
        # Comando para verificar la contraseña de sudo
        test_cmd = "sudo -S -v"
        proc = subprocess.Popen(
            test_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(input=f"{password}\n", timeout=5)
        
        # Si el comando sudo -v tiene éxito, la contraseña es correcta
        return proc.returncode == 0
    except Exception:
        return False

def get_sudo_password():
    """Solicita la contraseña de sudo al usuario"""
    import getpass
    
    print("\n" + "="*60)
    print("XONITER SIMPLE - MODO SUDO")
    print("="*60)
    print("Esta aplicación requiere privilegios sudo para ejecutar comandos.")
    print("Tu contraseña se mantendrá en memoria durante la sesión.")
    print("No se guardará en disco.")
    print("="*60)
    
    intentos = 0
    max_intentos = 3
    
    while intentos < max_intentos:
        try:
            password = getpass.getpass("Ingresa tu contraseña de sudo: ")
            
            if not password:
                print("La contraseña no puede estar vacía. Intenta nuevamente.")
                intentos += 1
                continue
            
            print("Verificando contraseña...")
            
            # Verificar la contraseña
            if verify_sudo_password(password):
                print("✓ Contraseña de sudo verificada correctamente!")
                return password
            else:
                intentos += 1
                if intentos < max_intentos:
                    print(f"✗ Contraseña incorrecta. Intentos restantes: {max_intentos - intentos}")
                else:
                    print("✗ Demasiados intentos fallidos.")
        
        except KeyboardInterrupt:
            print("\n\nOperación cancelada por el usuario.")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            intentos += 1
    
    # Si llegamos aquí, no se pudo verificar la contraseña
    print("\nNo se pudo verificar la contraseña de sudo.")
    print("Ejecutando sin privilegios elevados...")
    return None

def display_qr_in_terminal(url):
    """Muestra el código QR en la terminal"""
    print("\n" + "="*60)
    print("CÓDIGO QR PARA ACCESO RÁPIDO")
    print("="*60)
    print(f"URL: {url}")
    print()
    
    qr_ascii = generate_terminal_qr(url)
    if qr_ascii:
        print(qr_ascii)
        print("Escanea este código QR con tu teléfono para acceder rápidamente")
    else:
        print("No se pudo generar el código QR en la terminal.")
        print("Instala qrcode[pil] para ver el código QR: pip install qrcode[pil]")
    
    print("="*60)

def main():
    global sudo_password
    
    parser = argparse.ArgumentParser(description="Xoniter Simple - ejecuta comandos desde una página web con sudo.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host para vincular (por defecto 0.0.0.0 para exponer en LAN).")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Puerto para vincular (por defecto 5100).")
    parser.add_argument("--timeout", type=int, default=0, help="Tiempo límite por defecto para comandos en segundos (0 = sin límite).")
    parser.add_argument("--no-sudo", action="store_true", help="Ejecutar sin privilegios sudo (modo normal).")
    parser.add_argument("--no-qr", action="store_true", help="No mostrar código QR en la terminal.")
    args = parser.parse_args()
    
    # Solicitar contraseña de sudo si no se especifica --no-sudo
    if not args.no_sudo:
        sudo_password = get_sudo_password()
    else:
        print("\nEjecutando en modo normal sin privilegios sudo...")
    
    # Configurar la aplicación
    app.config["HOST"] = args.host
    app.config["PORT"] = args.port
    global DEFAULT_TIMEOUT
    if args.timeout and args.timeout > 0:
        DEFAULT_TIMEOUT = args.timeout
    else:
        DEFAULT_TIMEOUT = None
    
    # Obtener información de red
    server_ip = get_ip_address()
    full_url = f"http://{server_ip}:{args.port}/"
    
    print("\n" + "="*60)
    print("Xoniter Simple - Ejecutor de Comandos con Sudo")
    print("="*60)
    # Mostrar código QR en terminal si no se especifica --no-qr
    if not args.no_qr:
        display_qr_in_terminal(full_url)
    else:
        print("Código QR desactivado (--no-qr)")
        print("Escanea el código QR desde la interfaz web para acceder desde tu teléfono")
        print("="*60)
    
    print("Presiona Ctrl+C para detener el servidor")
    print("="*60 + "\n")
    
    try:
        app.run(host=args.host, port=args.port, debug=False)
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario.")
        sys.exit(0)
    finally:
        # Limpiar la contraseña de memoria
        sudo_password = None
        print("Contraseña limpiada de memoria.")

if __name__ == "__main__":
    main()
