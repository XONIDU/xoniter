#!/usr/bin/env python3

#by: XONIDU

from flask import Flask, request, render_template_string
import subprocess
import argparse
import html
import os
import time
import getpass

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5000
DEFAULT_TIMEOUT = None  # seconds; None = no timeout

app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Xoniter Simple</title>
  {% raw %}
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 18px; background:#f7f7f9; color:#222; }
    .container { max-width:900px; margin:0 auto; background:#fff; padding:18px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.08); }
    textarea { width:100%; height:160px; padding:10px; font-family: monospace; font-size:14px; }
    pre { background:#0b0b0b; color:#e6e6e6; padding:12px; border-radius:6px; overflow:auto; }
    input[type=text], input[type=number], button { padding:10px; margin-top:8px; }
    .warn { background:#fff3cd; padding:10px; border-radius:6px; color:#856404; }
    .meta { color:#555; font-size:0.9rem; }
  </style>
  {% endraw %}
</head>
<body>
  <div class="container">
    <h1>Xoniter Simple</h1>
    <p class="warn"><strong>Warning:</strong> This page runs commands on the host. Do not expose to untrusted networks.</p>
    <p class="meta">Host: <strong>{{ host }}:{{ port }}</strong> &nbsp; • &nbsp; Running as: <strong>{{ user }}</strong></p>

    <form method="post">
      <label for="cmd">Command (paste the full command or multiple commands):</label><br>
      <textarea name="cmd" id="cmd" placeholder="e.g. ls -la /home or uname -a">{{ cmd_escaped }}</textarea><br>
      <label for="timeout">Timeout (seconds, empty = no timeout):</label>
      <input type="number" name="timeout" id="timeout" min="1" value="{{ timeout_value }}"><br>
      <button type="submit">Run</button>
    </form>

    {% if ran %}
      <h3>Executed:</h3>
      <pre>{{ command }}</pre>

      {% if error %}
        <h3 style="color:crimson">Error:</h3>
        <pre style="color:crimson">{{ error }}</pre>
      {% endif %}

      <h3>STDOUT:</h3>
      <pre>{{ stdout }}</pre>

      <h3>STDERR:</h3>
      <pre>{{ stderr }}</pre>

      <p class="meta">Return code: <strong>{{ rc }}</strong> — Time: <strong>{{ elapsed }}</strong></p>
    {% endif %}

    <p class="meta">Tip: To limit exposure bind to 127.0.0.1 or use a firewall. Do not run as root.</p>
  </div>
</body>
</html>
"""

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
            try:
                start = time.time()
                # Execute the exact text the user provided in a shell
                proc = subprocess.run(
                    cmd_text,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout
                )
                elapsed = f"{time.time() - start:.2f}s"
                stdout = proc.stdout or ""
                stderr = proc.stderr or ""
                rc = proc.returncode
            except subprocess.TimeoutExpired:
                error = f"Command timed out after {timeout} seconds."
            except Exception as e:
                error = str(e)

    # Escape outputs for safe HTML rendering
    cmd_escaped = html.escape(cmd_text)
    stdout_esc = html.escape(stdout)
    stderr_esc = html.escape(stderr)
    error_esc = html.escape(error)

    try:
        user = getpass.getuser()
    except Exception:
        user = os.getenv("USER") or "unknown"

    return render_template_string(
        PAGE,
        host=app.config.get("HOST", DEFAULT_HOST),
        port=app.config.get("PORT", DEFAULT_PORT),
        user=user,
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

def main():
    parser = argparse.ArgumentParser(description="Prueba - run shell commands from a web page (no auth).")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind (default 0.0.0.0 to expose on LAN).")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind (default 5000).")
    parser.add_argument("--timeout", type=int, default=0, help="Default timeout for commands in seconds (0 = no timeout).")
    args = parser.parse_args()

    # configure app for templates
    app.config["HOST"] = args.host
    app.config["PORT"] = args.port
    global DEFAULT_TIMEOUT
    if args.timeout and args.timeout > 0:
        DEFAULT_TIMEOUT = args.timeout
    else:
        DEFAULT_TIMEOUT = None

    print("="*60)
    print("Xoniter Simple - no-auth command runner (fixed template)")
    print("WARNING: This service runs arbitrary commands as the user running it.")
    print("Do NOT expose to untrusted networks. Run as a non-root user.")
    print(f"Serving on http://{args.host}:{args.port}/  (open from your phone or other device on the same LAN)")
    print("="*60)

    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
