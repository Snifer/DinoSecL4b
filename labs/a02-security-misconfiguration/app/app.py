import os
from flask import Flask, request, session, redirect, render_template_string, send_from_directory
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "dev-secret-do-not-use"
app.debug = True

# Hardcoded credentials and secrets
ADMIN_USER = "admin"
ADMIN_PASS = "admin"
DB_PASSWORD = "Passw0rd_DB_2024!"
API_KEY = "sk-prod-9f3a1b2c4d5e6f7a8b9c0d1e2f3a4b5c"
JWT_SECRET = "jwt-weak-secret-123"
STRIPE_KEY = "sk_live_FAKE_STRIPE_KEY_DO_NOT_USE"
SMTP_PASS = "smtp_pass_2024!"
SECRET_FLAG = _flag('a02_secrets')

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DevPortal — Internal Operations</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Courier New', Courier, monospace; background: #0d1117; color: #e6edf3; min-height: 100vh; }
    header { background: #161b22; border-bottom: 1px solid #30363d; padding: .75rem 2rem; display: flex; align-items: center; justify-content: space-between; }
    .brand { font-size: 1.1rem; font-weight: bold; color: #58a6ff; }
    .brand span { color: #e6edf3; }
    header nav a { color: #8b949e; text-decoration: none; margin-left: 1.5rem; font-size: .85rem; }
    header nav a:hover { color: #e6edf3; }
    main { max-width: 1020px; margin: 2rem auto; padding: 0 1.5rem; }
    h2 { color: #58a6ff; margin-bottom: 1rem; font-size: 1rem; text-transform: uppercase; letter-spacing: .08em; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1.25rem; margin-bottom: 1.25rem; }
    .card-title { font-size: .8rem; color: #8b949e; text-transform: uppercase; letter-spacing: .1em; margin-bottom: .75rem; border-bottom: 1px solid #21262d; padding-bottom: .5rem; }
    .stats-row { display: flex; gap: 1rem; }
    .stats-row .card { flex: 1; text-align: center; }
    .stat-value { font-size: 1.6rem; color: #58a6ff; }
    .stat-label { font-size: .7rem; color: #8b949e; text-transform: uppercase; margin-top: .2rem; }
    .stat-ok { color: #3fb950; }
    table { width: 100%; border-collapse: collapse; font-size: .85rem; }
    th { text-align: left; padding: .5rem .75rem; color: #8b949e; border-bottom: 1px solid #30363d; font-weight: normal; font-size: .75rem; text-transform: uppercase; }
    td { padding: .5rem .75rem; border-bottom: 1px solid #21262d; }
    input { background: #21262d; border: 1px solid #30363d; color: #e6edf3; padding: .4rem .75rem; border-radius: 4px; font-family: inherit; font-size: .875rem; }
    button { background: #238636; border: 1px solid #2ea043; color: #fff; padding: .4rem 1rem; border-radius: 4px; font-family: inherit; font-size: .875rem; cursor: pointer; }
    button:hover { background: #2ea043; }
    .alert-error { background: rgba(248,81,73,.1); border: 1px solid rgba(248,81,73,.3); color: #f85149; padding: .6rem 1rem; border-radius: 4px; margin-bottom: 1rem; font-size: .85rem; }
    .form-row { display: flex; align-items: center; gap: .75rem; margin-bottom: .75rem; }
    .form-row label { color: #8b949e; font-size: .8rem; min-width: 80px; }
    pre { background: #0d1117; padding: 1rem; border-radius: 4px; overflow: auto; font-size: .8rem; line-height: 1.6; max-height: 450px; border: 1px solid #21262d; }
    .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: .4rem; }
    .dot-green { background: #3fb950; }
    .dot-yellow { background: #d29922; }
    .dot-red { background: #f85149; }
    a { color: #58a6ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    footer { text-align: center; font-size: .7rem; color: #484f58; margin: 3rem 0 1rem; }
  </style>
</head>
<body>
<header>
  <div class="brand">Dev<span>Portal</span></div>
  <nav>
    <a href="/">Dashboard</a>
    <a href="/services">Services</a>
    <a href="/admin">Admin</a>
  </nav>
</header>
<main>
{{ content | safe }}
</main>
<footer>DevPortal v2.1.0 &mdash; Internal Operations Platform &mdash; &copy; 2024</footer>
</body>
</html>"""

def render(content, **ctx):
    return render_template_string(BASE, content=content, **ctx)

SERVICES = [
    {"name": "api-gateway",    "host": "10.0.1.10", "port": 8080, "status": "running", "uptime": "42d 7h"},
    {"name": "auth-service",   "host": "10.0.1.11", "port": 9000, "status": "running", "uptime": "42d 7h"},
    {"name": "worker-pool",    "host": "10.0.1.12", "port": 5672, "status": "running", "uptime": "12d 3h"},
    {"name": "metrics-agent",  "host": "10.0.1.13", "port": 9090, "status": "stopped", "uptime": "0d 0h"},
    {"name": "postgres-main",  "host": "10.0.1.20", "port": 5432, "status": "running", "uptime": "42d 7h"},
]

@app.route("/")
def index():
    running = sum(1 for s in SERVICES if s["status"] == "running")
    stopped = len(SERVICES) - running
    rows = ""
    for s in SERVICES:
        dot = "dot-green" if s["status"] == "running" else "dot-red"
        rows += f"<tr><td>{s['name']}</td><td>{s['host']}</td><td>{s['port']}</td><td><span class='dot {dot}'></span>{s['status']}</td><td>{s['uptime']}</td></tr>"
    content = f"""
    <div class="stats-row">
      <div class="card"><div class="stat-value stat-ok">{running}</div><div class="stat-label">Services Running</div></div>
      <div class="card"><div class="stat-value" style="color:#f85149">{stopped}</div><div class="stat-label">Services Stopped</div></div>
      <div class="card"><div class="stat-value">{len(SERVICES)}</div><div class="stat-label">Total Services</div></div>
      <div class="card"><div class="stat-value">99.1%</div><div class="stat-label">Avg Uptime</div></div>
    </div>
    <div class="card">
      <div class="card-title">Service Registry</div>
      <table>
        <thead><tr><th>Service</th><th>Host</th><th>Port</th><th>Status</th><th>Uptime</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""
    return render(content)

@app.route("/services")
def services():
    rows = ""
    for s in SERVICES:
        dot = "dot-green" if s["status"] == "running" else "dot-red"
        restart_btn = "<button style='font-size:.7rem;padding:.2rem .5rem;background:#21262d;border-color:#30363d'>Restart</button>" if s['status'] == 'stopped' else ''
        rows += f"<tr><td>{s['name']}</td><td>{s['host']}:{s['port']}</td><td><span class='dot {dot}'></span>{s['status']}</td><td>{s['uptime']}</td><td>{restart_btn}</td></tr>"
    content = f"""
    <div class="card">
      <div class="card-title">All Services</div>
      <table>
        <thead><tr><th>Name</th><th>Endpoint</th><th>Status</th><th>Uptime</th><th>Actions</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""
    return render(content)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    msg = ""
    authed = session.get("admin_authed", False)
    if request.method == "POST" and not authed:
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["admin_authed"] = True
            authed = True
        else:
            msg = "<div class='alert-error'>Authentication failed.</div>"
    if authed:
        env_rows = "".join(f"<tr><td style='color:#8b949e'>{k}</td><td>{v}</td></tr>" for k, v in sorted(os.environ.items()))
        content = f"""
        <div class="card">
          <div class="card-title">Administration Panel</div>
          <div class="stats-row" style="margin-bottom:1rem">
            <div class="card"><div class="stat-value stat-ok">OK</div><div class="stat-label">System Health</div></div>
            <div class="card"><div class="stat-value">Python</div><div class="stat-label">Runtime</div></div>
            <div class="card"><div class="stat-value">{os.getcwd()}</div><div class="stat-label">Working Dir</div></div>
          </div>
          <div class="card-title" style="margin-top:.5rem">Process Environment</div>
          <table>
            <thead><tr><th>Variable</th><th>Value</th></tr></thead>
            <tbody>{env_rows}</tbody>
          </table>
        </div>"""
    else:
        content = f"""
        <div class="card" style="max-width:400px;margin:3rem auto">
          <div class="card-title">Admin Authentication</div>
          {msg}
          <form method="POST">
            <div class="form-row"><label>Username</label><input name="username" style="flex:1"></div>
            <div class="form-row"><label>Password</label><input name="password" type="password" style="flex:1"></div>
            <div style="text-align:right;margin-top:.5rem"><button type="submit">Authenticate</button></div>
          </form>
        </div>"""
    return render(content)

@app.route("/config")
def config():
    content = f"""
    <div class="card">
      <div class="card-title">Application Configuration</div>
      <pre>APP_ENV=production
APP_VERSION=2.1.0
SECRET_KEY={app.secret_key}
DB_HOST=postgres.internal.corp.com
DB_PORT=5432
DB_USER=app_user
DB_PASS={DB_PASSWORD}
DB_NAME=devportal_production
API_KEY={API_KEY}
JWT_SECRET={JWT_SECRET}
STRIPE_SECRET={STRIPE_KEY}
SMTP_HOST=mail.corp.com
SMTP_PORT=587
SMTP_USER=noreply@corp.com
SMTP_PASS={SMTP_PASS}
ADMIN_EMAIL=devops@corp.com
SECRET_FLAG={SECRET_FLAG}</pre>
    </div>"""
    return render(content)

@app.route("/backup/")
@app.route("/backup/<path:filename>")
def backup(filename=None):
    backup_dir = "/app/backup_files"
    os.makedirs(backup_dir, exist_ok=True)

    _files = {
        "db_dump_2024-03-01.sql": (
            "-- PostgreSQL dump\n"
            "-- Generated: 2024-03-01 03:00:01\n\n"
            "INSERT INTO users VALUES (1,'admin','$2b$12$hashed_pw','admin@corp.com','admin');\n"
            "INSERT INTO users VALUES (2,'alice','$2b$12$hashed_pw2','alice@corp.com','user');\n"
        ),
        "config_snapshot_2024-02-28.json": (
            '{"db_host":"postgres.internal","db_pass":"' + DB_PASSWORD + '",'
            '"api_key":"' + API_KEY + '","jwt_secret":"' + JWT_SECRET + '"}'
        ),
        "users_2024-03-01.csv": (
            "id,username,email,role,internal_token\n"
            f"1,admin,admin@corp.com,admin,{_flag('a02_backup')}\n"
            "2,alice,alice@corp.com,user,tok_user_abc123\n"
            "3,bob,bob@corp.com,user,tok_user_def456\n"
        ),
        "deploy_log_2024-02-27.txt": (
            "2024-02-27 09:12:01 INFO  Deploy started by jenkins\n"
            "2024-02-27 09:12:45 INFO  Container devportal:2.1.0 pulled\n"
            "2024-02-27 09:13:02 INFO  Health check passed\n"
            "2024-02-27 09:13:03 INFO  Deploy complete\n"
        ),
    }
    for fname, fcontent in _files.items():
        fpath = os.path.join(backup_dir, fname)
        if not os.path.exists(fpath):
            with open(fpath, "w") as f:
                f.write(fcontent)

    if filename:
        try:
            with open(os.path.join(backup_dir, filename)) as f:
                file_content = f.read()
            content = f"""
            <div class="card">
              <div class="card-title">Backup File: {filename}</div>
              <pre>{file_content}</pre>
            </div>
            <a href="/backup/">← Back to listing</a>"""
        except Exception as e:
            content = f"<div class='card'><p>Error: {e}</p></div>"
    else:
        flist = os.listdir(backup_dir)
        links = "".join(
            f"<tr><td><a href='/backup/{fn}'>{fn}</a></td><td>{os.path.getsize(os.path.join(backup_dir,fn))} B</td></tr>"
            for fn in sorted(flist)
        )
        content = f"""
        <div class="card">
          <div class="card-title">Backup Storage — /backup/</div>
          <table>
            <thead><tr><th>Filename</th><th>Size</th></tr></thead>
            <tbody>{links}</tbody>
          </table>
        </div>"""
    return render(content)

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    from flask import jsonify
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
