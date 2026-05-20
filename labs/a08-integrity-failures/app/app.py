import pickle
import base64
import os
import hashlib
from flask import Flask, request, session, redirect, render_template_string, make_response, jsonify
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "updatehub-prod-k9x2024"

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UpdateHub &mdash; Enterprise Software Distribution</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;color:#1a1a2e;min-height:100vh}
    header{background:#16213e;color:#fff;padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:64px;box-shadow:0 2px 8px rgba(0,0,0,.4)}
    header .logo{font-size:1.4rem;font-weight:700}
    header .logo span{color:#0f9b8e}
    header .tagline{font-size:.8rem;color:#90caf9}
    nav{background:#0f3460;border-bottom:3px solid #0f9b8e}
    nav a{color:#a8c5da;text-decoration:none;padding:.75rem 1.2rem;display:inline-block;font-size:.87rem;transition:background .2s}
    nav a:hover{background:#16213e;color:#fff}
    .container{max-width:1050px;margin:0 auto;padding:2rem 1.5rem}
    .page-title{font-size:1.4rem;font-weight:600;color:#16213e;margin-bottom:1.4rem;border-bottom:2px solid #dde3ed;padding-bottom:.5rem}
    .card{background:#fff;border-radius:8px;box-shadow:0 1px 5px rgba(0,0,0,.1);padding:1.6rem;margin-bottom:1.4rem}
    .card h3{color:#16213e;font-size:1.05rem;margin-bottom:1rem}
    .btn{display:inline-block;padding:.55rem 1.5rem;border-radius:5px;border:none;cursor:pointer;font-size:.9rem;font-weight:600;transition:background .2s;text-decoration:none}
    .btn-primary{background:#0f9b8e;color:#fff}.btn-primary:hover{background:#0c8578}
    .btn-outline{background:#fff;color:#16213e;border:1px solid #b0bec5}.btn-outline:hover{background:#f0f2f5}
    .btn-warning{background:#e67e22;color:#fff}.btn-warning:hover{background:#ca6f1e}
    input,textarea,select{border:1px solid #b0bec5;border-radius:5px;padding:.55rem .85rem;font-size:.9rem;width:100%;background:#fafbfc;color:#1a1a2e;font-family:inherit}
    input:focus,textarea:focus{outline:none;border-color:#0f9b8e;box-shadow:0 0 0 2px rgba(15,155,142,.15)}
    .form-group{margin-bottom:1rem}
    .form-group label{display:block;margin-bottom:.3rem;font-weight:500;color:#455a64;font-size:.88rem}
    .alert{padding:.75rem 1.1rem;border-radius:5px;margin:.8rem 0;font-size:.9rem}
    .alert-success{background:#e8f5e9;color:#1b5e20;border-left:4px solid #27ae60}
    .alert-danger{background:#fce4ec;color:#b71c1c;border-left:4px solid #e53935}
    .alert-warning{background:#fff8e1;color:#f57f17;border-left:4px solid #f9a825}
    .alert-info{background:#e3f2fd;color:#0d47a1;border-left:4px solid #1565c0}
    table{width:100%;border-collapse:collapse;font-size:.88rem}
    th{background:#16213e;color:#fff;padding:.65rem .9rem;text-align:left}
    td{padding:.6rem .9rem;border-bottom:1px solid #e8edf2}
    tr:hover td{background:#f5f8fc}
    .badge{display:inline-block;padding:.2rem .65rem;border-radius:12px;font-size:.75rem;font-weight:600}
    .badge-green{background:#e8f5e9;color:#2e7d32}
    .badge-blue{background:#e3f2fd;color:#1565c0}
    .badge-orange{background:#fff3e0;color:#e65100}
    code{background:#f0f4f8;border:1px solid #dce6f0;border-radius:3px;padding:.15rem .4rem;font-size:.8em;word-break:break-all}
    .mono{font-family:'Courier New',monospace;font-size:.82rem;background:#f8fafc;border:1px solid #dde3ed;border-radius:5px;padding:.8rem;word-break:break-all;line-height:1.6}
    .stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin-bottom:1.5rem}
    .stat-card{background:#fff;border-radius:8px;padding:1.2rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.1);border-left:4px solid #0f9b8e}
    .stat-card .num{font-size:1.9rem;font-weight:700;color:#16213e}
    .stat-card .lbl{color:#78909c;font-size:.82rem;margin-top:.2rem}
    footer{background:#16213e;color:#78909c;text-align:center;padding:1rem;font-size:.8rem;margin-top:3rem}
  </style>
</head>
<body>
<header>
  <div class="logo">Update<span>Hub</span></div>
  <div class="tagline">Enterprise Software Distribution &amp; Update Management</div>
</header>
<nav>
  <a href="/">Overview</a>
  <a href="/update/check">Check Updates</a>
  <a href="/update/apply">Apply Update</a>
  <a href="/profile">My Profile</a>
  <a href="/releases">Release Notes</a>
</nav>
<div class="container">
CONTENT_PLACEHOLDER
</div>
<footer>UpdateHub &copy; 2024 &mdash; Enterprise Software Distribution Platform &mdash; For authorized personnel only</footer>
</body>
</html>"""

def render(content):
    return BASE.replace("CONTENT_PLACEHOLDER", content)

def _generate_demo_payload():
    class WriteFlag:
        def __reduce__(self):
            return (os.system, (f"echo {_flag('a08_pickle')} > /tmp/flag_pickle.txt",))
    return base64.b64encode(pickle.dumps(WriteFlag())).decode()

@app.route("/")
def index():
    content = """
    <div class="page-title">UpdateHub Dashboard</div>
    <div class="stat-grid">
      <div class="stat-card"><div class="num">v4.2.1</div><div class="lbl">Current Release</div></div>
      <div class="stat-card" style="border-color:#27ae60"><div class="num">142</div><div class="lbl">Managed Endpoints</div></div>
      <div class="stat-card" style="border-color:#f9a825"><div class="num">3</div><div class="lbl">Pending Updates</div></div>
      <div class="stat-card" style="border-color:#1565c0"><div class="num">99.4%</div><div class="lbl">Deployment Success</div></div>
    </div>
    <div class="card">
      <h3>Welcome to UpdateHub</h3>
      <p style="color:#546e7a;line-height:1.8">Centralized enterprise update management. Distribute, verify, and apply software updates across your entire infrastructure from a single control plane.</p>
      <div style="margin-top:1rem;display:flex;gap:.8rem;flex-wrap:wrap">
        <a href="/update/check" class="btn btn-primary">Check for Updates</a>
        <a href="/update/apply" class="btn btn-outline">Apply Update Package</a>
        <a href="/profile" class="btn btn-outline">Profile Settings</a>
      </div>
    </div>
    <div class="card">
      <h3>Deployment Status</h3>
      <table>
        <tr><th>Package</th><th>Version</th><th>Endpoints</th><th>Status</th></tr>
        <tr><td>Core Agent</td><td>4.2.1</td><td>142/142</td><td><span class="badge badge-green">Deployed</span></td></tr>
        <tr><td>Security Pack</td><td>2.8.0</td><td>138/142</td><td><span class="badge badge-orange">In Progress</span></td></tr>
        <tr><td>Config Manager</td><td>1.5.3</td><td>142/142</td><td><span class="badge badge-green">Deployed</span></td></tr>
        <tr><td>Telemetry Module</td><td>3.1.0</td><td>0/142</td><td><span class="badge badge-blue">Scheduled</span></td></tr>
      </table>
    </div>"""
    return render(content)

@app.route("/update/check")
def update_check():
    content = """
    <div class="page-title">Check for Updates</div>
    <div class="card">
      <h3>Update Availability</h3>
      <div class="alert alert-info">Scanning update repository&hellip; Connection established.</div>
      <table>
        <tr><th>Component</th><th>Installed</th><th>Available</th><th>Action</th></tr>
        <tr><td>Core Agent</td><td>4.2.0</td><td>4.2.1</td><td><a href="/update/apply" class="btn btn-primary" style="padding:.3rem .9rem;font-size:.82rem">Update</a></td></tr>
        <tr><td>Security Pack</td><td>2.7.9</td><td>2.8.0</td><td><a href="/update/apply" class="btn btn-primary" style="padding:.3rem .9rem;font-size:.82rem">Update</a></td></tr>
        <tr><td>Config Manager</td><td>1.5.3</td><td>1.5.3</td><td><span class="badge badge-green">Up to date</span></td></tr>
      </table>
    </div>
    <div class="card">
      <h3>Repository Integrity</h3>
      <p style="color:#546e7a">Package metadata retrieved from distribution server. Apply updates via the <a href="/update/apply" style="color:#0f9b8e">Apply Update</a> panel.</p>
    </div>"""
    return render(content)

@app.route("/update/apply", methods=["GET", "POST"])
def update_apply():
    result = ""
    demo_payload = _generate_demo_payload()

    if request.method == "POST":
        data_b64 = request.form.get("package_data", "").strip()
        try:
            raw = base64.b64decode(data_b64)
            pickle.loads(raw)
            try:
                with open("/tmp/flag_pickle.txt") as f:
                    proof = f.read().strip()
            except Exception:
                proof = "(no output file found)"
            result = f"""
            <div class="alert alert-success">
              <strong>Update package processed.</strong><br>
              Execution output: <code>{proof}</code>
            </div>"""
        except Exception as e:
            result = f"""<div class="alert alert-danger">Package processing error: {e}</div>"""

    content = f"""
    <div class="page-title">Apply Update Package</div>
    <div class="card">
      <h3>Upload Update Package</h3>
      <p style="color:#546e7a;margin-bottom:1rem">Paste the base64-encoded update package received from the distribution server. Packages are applied immediately upon submission.</p>
      <form method="POST">
        <div class="form-group">
          <label>Package Data (Base64)</label>
          <textarea name="package_data" rows="5" placeholder="{demo_payload}">{demo_payload}</textarea>
        </div>
        <button class="btn btn-primary" type="submit">Apply Package</button>
      </form>
      {result}
    </div>
    <div class="card">
      <h3>Package Format</h3>
      <p style="color:#546e7a">Update packages are serialized bundles distributed by the central server. Paste the full base64 string as provided by your update coordinator.</p>
    </div>"""
    return render(content)

@app.route("/profile")
def profile():
    raw_cookie = request.cookies.get("user_data", "")
    user_info = {"username": "guest", "role": "viewer", "dept": "General"}
    flag_section = ""

    if raw_cookie:
        try:
            decoded = base64.b64decode(raw_cookie).decode()
            import ast
            user_info = ast.literal_eval(decoded)
        except Exception:
            pass

    if user_info.get("role") == "admin":
        flag_section = f"""
        <div class="alert alert-info" style="margin-top:1rem">
          <strong>Administrator session detected.</strong> Elevated access token: <code>{_flag('a08_tamper')}</code>
        </div>"""

    normal_cookie = base64.b64encode(b"{'username': 'jdoe', 'role': 'viewer', 'dept': 'Engineering'}").decode()
    resp = make_response(render(f"""
    <div class="page-title">My Profile</div>
    <div class="card">
      <h3>Account Information</h3>
      <table>
        <tr><th>Field</th><th>Value</th></tr>
        <tr><td>Username</td><td>{user_info.get('username', 'N/A')}</td></tr>
        <tr><td>Role</td><td><span class="badge badge-blue">{user_info.get('role', 'N/A')}</span></td></tr>
        <tr><td>Department</td><td>{user_info.get('dept', 'N/A')}</td></tr>
      </table>
      {flag_section}
    </div>
    <div class="card">
      <h3>Session Details</h3>
      <p style="color:#546e7a;margin-bottom:.5rem">Your session token (stored in browser cookie <code>user_data</code>):</p>
      <div class="mono">{raw_cookie or normal_cookie}</div>
    </div>"""))

    if not raw_cookie:
        resp.set_cookie("user_data", normal_cookie)
    return resp

@app.route("/releases")
def releases():
    content = """
    <div class="page-title">Release Notes</div>
    <div class="card">
      <h3>v4.2.1 &mdash; 2024-11-28</h3>
      <ul style="color:#546e7a;line-height:2;padding-left:1.2rem">
        <li>Improved update package validation performance</li>
        <li>Fixed edge case in rollback mechanism for partial deployments</li>
        <li>Added support for delta-package distribution</li>
      </ul>
    </div>
    <div class="card">
      <h3>v4.2.0 &mdash; 2024-10-15</h3>
      <ul style="color:#546e7a;line-height:2;padding-left:1.2rem">
        <li>New endpoint health monitoring dashboard</li>
        <li>Bandwidth throttling controls for large-scale rollouts</li>
        <li>Enhanced audit logging for compliance requirements</li>
      </ul>
    </div>"""
    return render(content)

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    try:
        os.remove("/tmp/flag_pickle.txt")
    except FileNotFoundError:
        pass
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
