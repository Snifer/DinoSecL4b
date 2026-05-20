import hashlib
import time
from flask import Flask, request, session, redirect, render_template_string, jsonify
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "empportal-hr-2024"

USERS = {
    "alice": {"password": "123",      "email": "alice@corp.internal", "role": "employee", "dept": "Engineering"},
    "bob":   {"password": "password", "email": "bob@corp.internal",   "role": "employee", "dept": "Finance"},
    "admin": {"password": "admin",    "email": "admin@corp.internal",  "role": "admin",    "dept": "IT"},
}

RESET_TOKENS = {}

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EmpPortal &mdash; Employee Self-Service</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',Arial,sans-serif;background:#eef2f7;color:#2c3e50;min-height:100vh}
    header{background:#003366;color:#fff;padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:62px;box-shadow:0 2px 6px rgba(0,0,0,.35)}
    header .logo{font-size:1.35rem;font-weight:700;letter-spacing:.5px}
    header .logo span{color:#64b5f6}
    header .tagline{font-size:.8rem;color:#90caf9}
    nav{background:#004080;border-bottom:3px solid #64b5f6}
    nav a{color:#b3cde0;text-decoration:none;padding:.75rem 1.2rem;display:inline-block;font-size:.87rem;transition:background .2s}
    nav a:hover{background:#003366;color:#fff}
    .container{max-width:960px;margin:0 auto;padding:2rem 1.5rem}
    .page-title{font-size:1.4rem;font-weight:600;color:#003366;margin-bottom:1.4rem;border-bottom:2px solid #dce6f0;padding-bottom:.5rem}
    .card{background:#fff;border-radius:8px;box-shadow:0 1px 5px rgba(0,0,0,.1);padding:1.6rem;margin-bottom:1.4rem}
    .card h3{color:#003366;font-size:1.05rem;margin-bottom:1rem}
    .btn{display:inline-block;padding:.55rem 1.5rem;border-radius:5px;border:none;cursor:pointer;font-size:.9rem;font-weight:600;transition:background .2s;text-decoration:none}
    .btn-primary{background:#0055aa;color:#fff}.btn-primary:hover{background:#004494}
    .btn-outline{background:#fff;color:#003366;border:1px solid #b0c4de}.btn-outline:hover{background:#eef2f7}
    .btn-danger{background:#c0392b;color:#fff}.btn-danger:hover{background:#a93226}
    input{border:1px solid #b0c4de;border-radius:5px;padding:.55rem .85rem;font-size:.9rem;width:100%;background:#f8fafc;color:#2c3e50}
    input:focus{outline:none;border-color:#0055aa;box-shadow:0 0 0 2px rgba(0,85,170,.15)}
    .form-group{margin-bottom:1rem}
    .form-group label{display:block;margin-bottom:.3rem;font-weight:500;color:#455a64;font-size:.88rem}
    .alert{padding:.75rem 1.1rem;border-radius:5px;margin:.8rem 0;font-size:.9rem}
    .alert-success{background:#e8f5e9;color:#1b5e20;border-left:4px solid #27ae60}
    .alert-danger{background:#fce4ec;color:#b71c1c;border-left:4px solid #e53935}
    .alert-warning{background:#fff8e1;color:#f57f17;border-left:4px solid #f9a825}
    .alert-info{background:#e3f2fd;color:#0d47a1;border-left:4px solid #1565c0}
    table{width:100%;border-collapse:collapse;font-size:.88rem}
    th{background:#003366;color:#fff;padding:.65rem .9rem;text-align:left}
    td{padding:.6rem .9rem;border-bottom:1px solid #e8edf2}
    tr:hover td{background:#f5f8fc}
    .badge{display:inline-block;padding:.2rem .65rem;border-radius:12px;font-size:.75rem;font-weight:600}
    .badge-blue{background:#e3f2fd;color:#1565c0}
    .badge-green{background:#e8f5e9;color:#2e7d32}
    .badge-red{background:#fce4ec;color:#b71c1c}
    .login-wrap{min-height:calc(100vh - 130px);display:flex;align-items:center;justify-content:center}
    .login-box{background:#fff;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,.12);padding:2.5rem;width:100%;max-width:420px}
    .login-box h2{color:#003366;margin-bottom:1.5rem;text-align:center}
    .divider{height:1px;background:#e8edf2;margin:1rem 0}
    footer{background:#003366;color:#90a4ae;text-align:center;padding:1rem;font-size:.8rem;margin-top:3rem}
    code{background:#f0f4f8;border:1px solid #dce6f0;border-radius:3px;padding:.15rem .4rem;font-size:.85em}
  </style>
</head>
<body>
<header>
  <div class="logo">Emp<span>Portal</span></div>
  <div class="tagline">Human Resources &amp; Employee Self-Service Platform</div>
</header>
<nav>
  <a href="/">Home</a>
  <a href="/login">Sign In</a>
  <a href="/dashboard">My Dashboard</a>
  <a href="/reset">Password Reset</a>
  <a href="/logout">Sign Out</a>
</nav>
<div class="container">
CONTENT_PLACEHOLDER
</div>
<footer>EmpPortal &copy; 2024 &mdash; Corporate HR Platform &mdash; All rights reserved &mdash; Internal use only</footer>
</body>
</html>"""

def render(content):
    return BASE.replace("CONTENT_PLACEHOLDER", content)

login_attempts = {}

@app.route("/")
def index():
    user = session.get("user")
    greeting = f"<div class='alert alert-info'>Signed in as <strong>{user}</strong>. <a href='/dashboard'>Go to Dashboard</a></div>" if user else ""
    content = f"""
    <div class="page-title">Welcome to EmpPortal</div>
    {greeting}
    <div class="card">
      <h3>Employee Self-Service</h3>
      <p style="color:#546e7a;line-height:1.8">Access your payslips, request time off, update personal information, and manage your employee profile — all in one place.</p>
      <div style="margin-top:1.2rem;display:flex;gap:.8rem;flex-wrap:wrap">
        <a href="/login" class="btn btn-primary">Sign In</a>
        <a href="/reset" class="btn btn-outline">Forgot Password</a>
      </div>
    </div>
    <div class="card">
      <h3>Quick Links</h3>
      <table>
        <tr><th>Service</th><th>Description</th></tr>
        <tr><td>My Dashboard</td><td>View personal information and company announcements</td></tr>
        <tr><td>Password Reset</td><td>Request a secure password reset link</td></tr>
        <tr><td>HR Policies</td><td>Access company policies and procedures</td></tr>
        <tr><td>Benefits</td><td>Review your benefits and enrollment options</td></tr>
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
        login_attempts[ip] = login_attempts.get(ip, 0) + 1

        user = USERS.get(username)
        if user is None:
            msg = f"<div class='alert alert-danger'>Account <strong>{username}</strong> was not found. Please check your username.</div>"
        elif user["password"] != password:
            msg = "<div class='alert alert-danger'>Incorrect password. Please try again.</div>"
        else:
            session["user"] = username
            session["role"] = user["role"]
            return redirect("/dashboard")

    content = f"""
    <div class="login-wrap">
      <div class="login-box">
        <h2>Employee Sign In</h2>
        {msg}
        <form method="POST">
          <div class="form-group">
            <label for="username">Username</label>
            <input id="username" name="username" type="text" placeholder="your.username" autocomplete="username">
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input id="password" name="password" type="password" placeholder="Password" autocomplete="current-password">
          </div>
          <button class="btn btn-primary" type="submit" style="width:100%;margin-top:.5rem">Sign In</button>
        </form>
        <div class="divider"></div>
        <p style="text-align:center;font-size:.85rem;color:#78909c">
          Forgot your password? <a href="/reset" style="color:#0055aa">Reset it here</a>
        </p>
      </div>
    </div>"""
    return render(content)

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect("/login")

    data = USERS.get(user, {})
    role = session.get("role", "employee")

    flag_section = ""
    if role == "admin":
        flag_section = f"""
        <div class="card" style="border-left:4px solid #0055aa">
          <h3>Administration Access</h3>
          <div class="alert alert-info">
            <strong>Elevated access confirmed.</strong> Authorization token: <code>{_flag('a07_force')}</code>
          </div>
          <table>
            <tr><th>Employee</th><th>Department</th><th>Role</th><th>Status</th></tr>
            <tr><td>alice</td><td>Engineering</td><td>Employee</td><td><span class="badge badge-green">Active</span></td></tr>
            <tr><td>bob</td><td>Finance</td><td>Employee</td><td><span class="badge badge-green">Active</span></td></tr>
            <tr><td>admin</td><td>IT</td><td>Administrator</td><td><span class="badge badge-blue">Active</span></td></tr>
          </table>
        </div>"""

    content = f"""
    <div class="page-title">My Dashboard</div>
    <div class="card">
      <h3>Profile Overview</h3>
      <table>
        <tr><td style="width:40%"><strong>Username</strong></td><td>{user}</td></tr>
        <tr><td><strong>Email</strong></td><td>{data.get('email', 'N/A')}</td></tr>
        <tr><td><strong>Department</strong></td><td>{data.get('dept', 'N/A')}</td></tr>
        <tr><td><strong>Role</strong></td><td><span class="badge {'badge-red' if role == 'admin' else 'badge-blue'}">{role.capitalize()}</span></td></tr>
      </table>
    </div>
    {flag_section}
    <div class="card">
      <h3>Upcoming Events</h3>
      <table>
        <tr><th>Date</th><th>Event</th></tr>
        <tr><td>2024-12-15</td><td>Year-end performance review deadline</td></tr>
        <tr><td>2024-12-20</td><td>Holiday party — Main conference room</td></tr>
        <tr><td>2025-01-06</td><td>Q1 planning kickoff</td></tr>
      </table>
    </div>
    <div style="margin-top:.5rem">
      <a href="/logout" class="btn btn-danger">Sign Out</a>
    </div>"""
    return render(content)

@app.route("/reset", methods=["GET", "POST"])
def reset_request():
    msg = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        ts = int(time.time() / 300) * 300
        token = hashlib.md5(f"{email}{ts}".encode()).hexdigest()
        found = False
        for uname, data in USERS.items():
            if data["email"] == email:
                RESET_TOKENS[token] = uname
                found = True
                break
        if found:
            msg = f"<div class='alert alert-success'>A password reset link has been sent to <strong>{email}</strong>. Please check your inbox.</div>"
        else:
            msg = "<div class='alert alert-danger'>No account associated with that email address.</div>"

    content = f"""
    <div class="page-title">Password Reset</div>
    <div class="card">
      <h3>Request a Password Reset</h3>
      <p style="color:#546e7a;margin-bottom:1rem">Enter your corporate email address and we will send you a secure link to reset your password.</p>
      {msg}
      <form method="POST">
        <div class="form-group">
          <label>Corporate Email Address</label>
          <input name="email" type="email" placeholder="you@corp.internal">
        </div>
        <button class="btn btn-primary" type="submit">Send Reset Link</button>
      </form>
    </div>"""
    return render(content)

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    username = RESET_TOKENS.get(token)
    if not username:
        content = """
        <div class="page-title">Password Reset</div>
        <div class="card">
          <div class="alert alert-danger">This reset link is invalid or has already been used.</div>
          <a href="/reset" class="btn btn-outline" style="margin-top:.5rem">Request a new link</a>
        </div>"""
        return render(content)

    msg = ""
    flag_section = ""
    if request.method == "POST":
        new_pass = request.form.get("password", "")
        USERS[username]["password"] = new_pass
        del RESET_TOKENS[token]
        if username == "admin":
            flag_section = f"""
            <div class="alert alert-info" style="margin-top:.8rem">
              <strong>Administrator account reset.</strong> Recovery token: <code>{_flag('a07_token')}</code>
            </div>"""
        msg = f"<div class='alert alert-success'>Password for account <strong>{username}</strong> has been updated successfully.</div>"

    content = f"""
    <div class="page-title">Set New Password</div>
    <div class="card">
      <h3>Reset Password for: <em>{username}</em></h3>
      {msg}
      {flag_section}
      <form method="POST">
        <div class="form-group">
          <label>New Password</label>
          <input name="password" type="password" placeholder="Enter your new password">
        </div>
        <button class="btn btn-primary" type="submit">Update Password</button>
      </form>
    </div>"""
    return render(content)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    global login_attempts, RESET_TOKENS
    login_attempts = {}
    RESET_TOKENS = {}
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
