import logging
import os
from flask import Flask, request, session, redirect, render_template_string, jsonify
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "auditlog-compliance-2024"

LOG_FILE = "/tmp/auditlog.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("auditlog")

USERS = {
    "alice":   "password123",
    "admin":   "S3cr3t!",
    "bob":     "qwerty",
    "jmoreno": "Welcome1",
}

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AuditLog &mdash; Compliance &amp; Audit Management</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',Arial,sans-serif;background:#f3f4f8;color:#1c2238;min-height:100vh}
    header{background:#1c2238;color:#fff;padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:62px;box-shadow:0 2px 8px rgba(0,0,0,.4)}
    header .logo{font-size:1.4rem;font-weight:700}
    header .logo span{color:#26c6da}
    header .tagline{font-size:.8rem;color:#90caf9}
    nav{background:#253050;border-bottom:3px solid #26c6da}
    nav a{color:#a8c5da;text-decoration:none;padding:.75rem 1.2rem;display:inline-block;font-size:.87rem;transition:background .2s}
    nav a:hover{background:#1c2238;color:#fff}
    .container{max-width:1050px;margin:0 auto;padding:2rem 1.5rem}
    .page-title{font-size:1.4rem;font-weight:600;color:#1c2238;margin-bottom:1.4rem;border-bottom:2px solid #e0e5f0;padding-bottom:.5rem}
    .card{background:#fff;border-radius:8px;box-shadow:0 1px 5px rgba(0,0,0,.09);padding:1.6rem;margin-bottom:1.4rem}
    .card h3{color:#1c2238;font-size:1.05rem;margin-bottom:1rem}
    .btn{display:inline-block;padding:.55rem 1.5rem;border-radius:5px;border:none;cursor:pointer;font-size:.9rem;font-weight:600;transition:background .2s;text-decoration:none}
    .btn-primary{background:#0077b6;color:#fff}.btn-primary:hover{background:#006094}
    .btn-outline{background:#fff;color:#1c2238;border:1px solid #b0bec5}.btn-outline:hover{background:#f3f4f8}
    .btn-danger{background:#c62828;color:#fff}.btn-danger:hover{background:#ad1f1f}
    input,textarea{border:1px solid #b0bec5;border-radius:5px;padding:.55rem .85rem;font-size:.9rem;width:100%;background:#fafbfc;color:#1c2238;font-family:inherit}
    input:focus,textarea:focus{outline:none;border-color:#0077b6;box-shadow:0 0 0 2px rgba(0,119,182,.15)}
    .form-group{margin-bottom:1rem}
    .form-group label{display:block;margin-bottom:.3rem;font-weight:500;color:#455a64;font-size:.88rem}
    .alert{padding:.75rem 1.1rem;border-radius:5px;margin:.8rem 0;font-size:.9rem}
    .alert-success{background:#e8f5e9;color:#1b5e20;border-left:4px solid #27ae60}
    .alert-danger{background:#fce4ec;color:#b71c1c;border-left:4px solid #e53935}
    .alert-warning{background:#fff8e1;color:#f57f17;border-left:4px solid #f9a825}
    .alert-info{background:#e3f2fd;color:#0d47a1;border-left:4px solid #1565c0}
    table{width:100%;border-collapse:collapse;font-size:.88rem}
    th{background:#1c2238;color:#fff;padding:.65rem .9rem;text-align:left}
    td{padding:.6rem .9rem;border-bottom:1px solid #e8edf2}
    tr:hover td{background:#f5f8fc}
    .badge{display:inline-block;padding:.2rem .65rem;border-radius:12px;font-size:.75rem;font-weight:600}
    .badge-green{background:#e8f5e9;color:#2e7d32}
    .badge-blue{background:#e3f2fd;color:#1565c0}
    .badge-orange{background:#fff3e0;color:#e65100}
    .badge-red{background:#fce4ec;color:#b71c1c}
    pre{background:#1a1f2e;color:#a8d8a8;padding:1.2rem;border-radius:6px;overflow:auto;max-height:420px;font-size:.78rem;line-height:1.6;font-family:'Courier New',monospace}
    code{background:#f0f4f8;border:1px solid #dde3ed;border-radius:3px;padding:.15rem .4rem;font-size:.85em}
    .login-wrap{min-height:calc(100vh - 130px);display:flex;align-items:center;justify-content:center}
    .login-box{background:#fff;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,.12);padding:2.5rem;width:100%;max-width:420px}
    .login-box h2{color:#1c2238;margin-bottom:1.5rem;text-align:center}
    .stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin-bottom:1.5rem}
    .stat-card{background:#fff;border-radius:8px;padding:1.2rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.1);border-left:4px solid #0077b6}
    .stat-card .num{font-size:1.9rem;font-weight:700;color:#1c2238}
    .stat-card .lbl{color:#78909c;font-size:.82rem;margin-top:.2rem}
    footer{background:#1c2238;color:#78909c;text-align:center;padding:1rem;font-size:.8rem;margin-top:3rem}
  </style>
</head>
<body>
<header>
  <div class="logo">Audit<span>Log</span></div>
  <div class="tagline">Compliance &amp; Audit Management Platform</div>
</header>
<nav>
  <a href="/">Dashboard</a>
  <a href="/login">Sign In</a>
  <a href="/logs">Audit Logs</a>
  <a href="/report">Submit Report</a>
  <a href="/transfer">Transactions</a>
  <a href="/logout">Sign Out</a>
</nav>
<div class="container">
CONTENT_PLACEHOLDER
</div>
<footer>AuditLog &copy; 2024 &mdash; Compliance &amp; Audit Management &mdash; All rights reserved</footer>
</body>
</html>"""

def render(content):
    return BASE.replace("CONTENT_PLACEHOLDER", content)

@app.route("/")
def index():
    user = session.get("user")
    greeting = f"<div class='alert alert-info'>Signed in as <strong>{user}</strong>. <a href='/logs'>View audit logs</a></div>" if user else ""
    content = f"""
    <div class="page-title">Compliance Dashboard</div>
    {greeting}
    <div class="stat-grid">
      <div class="stat-card"><div class="num">4,821</div><div class="lbl">Log Entries Today</div></div>
      <div class="stat-card" style="border-color:#27ae60"><div class="num">99.2%</div><div class="lbl">Compliance Score</div></div>
      <div class="stat-card" style="border-color:#f9a825"><div class="num">2</div><div class="lbl">Open Findings</div></div>
      <div class="stat-card" style="border-color:#c62828"><div class="num">0</div><div class="lbl">Critical Alerts</div></div>
    </div>
    <div class="card">
      <h3>Welcome to AuditLog</h3>
      <p style="color:#546e7a;line-height:1.8">Centralized audit and compliance management platform. Monitor system events, review audit trails, and submit compliance reports from a single interface.</p>
      <div style="margin-top:1rem;display:flex;gap:.8rem;flex-wrap:wrap">
        <a href="/login" class="btn btn-primary">Sign In</a>
        <a href="/logs" class="btn btn-outline">Audit Logs</a>
        <a href="/report" class="btn btn-outline">Submit Report</a>
      </div>
    </div>
    <div class="card">
      <h3>Recent Compliance Events</h3>
      <table>
        <tr><th>Timestamp</th><th>Event</th><th>Severity</th><th>Status</th></tr>
        <tr><td>2024-12-01 09:00</td><td>Quarterly access review completed</td><td><span class="badge badge-green">Low</span></td><td><span class="badge badge-green">Closed</span></td></tr>
        <tr><td>2024-11-30 16:45</td><td>Privileged account activity detected</td><td><span class="badge badge-orange">Medium</span></td><td><span class="badge badge-blue">Open</span></td></tr>
        <tr><td>2024-11-29 11:20</td><td>Policy exception approved — Finance dept</td><td><span class="badge badge-green">Low</span></td><td><span class="badge badge-green">Closed</span></td></tr>
      </table>
    </div>"""
    return render(content)

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        ip = request.remote_addr

        if USERS.get(username) == password:
            session["user"] = username
            logger.info(f"AUTH_SUCCESS user={username} pass={password} ip={ip} flag={_flag('a09_passwd')}")
            return redirect("/logs")
        else:
            logger.warning(f"AUTH_FAILURE user={username} ip={ip}")
            msg = "<div class='alert alert-danger'>Invalid credentials. Please try again.</div>"

    content = f"""
    <div class="login-wrap">
      <div class="login-box">
        <h2>Compliance Portal Sign In</h2>
        {msg}
        <form method="POST">
          <div class="form-group">
            <label>Username</label>
            <input name="username" type="text" placeholder="username" autocomplete="username">
          </div>
          <div class="form-group">
            <label>Password</label>
            <input name="password" type="password" placeholder="Password" autocomplete="current-password">
          </div>
          <button class="btn btn-primary" type="submit" style="width:100%;margin-top:.5rem">Sign In</button>
        </form>
      </div>
    </div>"""
    return render(content)

@app.route("/logs")
def view_logs():
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        log_content = "".join(lines[-100:]) if lines else "(no log entries yet)"
    except Exception:
        log_content = "(log file not available)"

    content = f"""
    <div class="page-title">Audit Log Viewer</div>
    <div class="card">
      <h3>System Event Log &mdash; Last 100 entries</h3>
      <p style="color:#546e7a;margin-bottom:1rem">Real-time view of application audit events. Log file: <code>{LOG_FILE}</code></p>
      <pre>{log_content}</pre>
    </div>"""
    return render(content)

@app.route("/report", methods=["GET", "POST"])
def report():
    msg = ""
    if request.method == "POST":
        report_text = request.form.get("report_text", "")
        user = session.get("user", "anonymous")
        logger.warning(f"COMPLIANCE_REPORT user={user} content={report_text}")
        msg = f"""
        <div class="alert alert-success">
          Report submitted and logged.<br>
          <strong>Confirmation code: {_flag('a09_inject')}</strong>
        </div>"""

    content = f"""
    <div class="page-title">Submit Compliance Report</div>
    <div class="card">
      <h3>Incident or Compliance Report</h3>
      <p style="color:#546e7a;margin-bottom:1rem">Use this form to report compliance incidents, policy violations, or security observations. All submissions are logged for audit purposes.</p>
      {msg}
      <form method="POST">
        <div class="form-group">
          <label>Report Details</label>
          <textarea name="report_text" rows="6" placeholder="Describe the compliance incident or observation..."></textarea>
        </div>
        <button class="btn btn-primary" type="submit">Submit Report</button>
      </form>
    </div>"""
    return render(content)

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    msg = ""
    if request.method == "POST":
        amount = request.form.get("amount", "0")
        dest = request.form.get("dest", "")
        msg = f"<div class='alert alert-success'>Transaction of <strong>${amount}</strong> to account <strong>{dest}</strong> processed successfully.</div>"

    content = f"""
    <div class="page-title">Financial Transactions</div>
    <div class="card">
      <h3>Initiate Transfer</h3>
      {msg}
      <form method="POST">
        <div class="form-group">
          <label>Destination Account</label>
          <input name="dest" placeholder="Account number or IBAN">
        </div>
        <div class="form-group">
          <label>Amount (USD)</label>
          <input name="amount" type="number" step="0.01" placeholder="0.00">
        </div>
        <button class="btn btn-primary" type="submit">Process Transfer</button>
      </form>
    </div>
    <div class="card">
      <h3>Recent Transactions</h3>
      <table>
        <tr><th>Date</th><th>Account</th><th>Amount</th><th>Status</th></tr>
        <tr><td>2024-12-01</td><td>ACC-4821</td><td>$12,500.00</td><td><span class="badge badge-green">Completed</span></td></tr>
        <tr><td>2024-11-30</td><td>ACC-0093</td><td>$3,200.00</td><td><span class="badge badge-green">Completed</span></td></tr>
        <tr><td>2024-11-29</td><td>ACC-7742</td><td>$890.00</td><td><span class="badge badge-orange">Pending</span></td></tr>
      </table>
    </div>"""
    return render(content)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    try:
        os.remove(LOG_FILE)
    except FileNotFoundError:
        pass
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
