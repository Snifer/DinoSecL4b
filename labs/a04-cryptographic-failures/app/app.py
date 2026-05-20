import hashlib
import base64
import json
import hmac
import time
from flask import Flask, request, session, redirect, render_template_string
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "securebank-weak-2024"

USERS_DB = {
    "alice": {
        "hash_md5": hashlib.md5(b"password123").hexdigest(),   # 482c811da5d5b4bc6d497ffa98491e38
        "email": "alice@securebank.internal",
        "role": "user",
        "account": "****-****-****-9012",
        "balance": 8_432.15,
    },
    "admin": {
        "hash_md5": hashlib.md5(b"admin").hexdigest(),          # 21232f297a57a5a743894a0e4a801fc3
        "email": "admin@securebank.internal",
        "role": "admin",
        "account": "****-****-****-1111",
        "balance": 1_250_000.00,
    },
    "bob": {
        "hash_md5": hashlib.md5(b"qwerty").hexdigest(),
        "email": "bob@securebank.internal",
        "role": "user",
        "account": "****-****-****-0004",
        "balance": 3_102.90,
    },
}

JWT_SECRET = "secret"

def jwt_encode(payload):
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    body   = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    sig    = base64.urlsafe_b64encode(
        hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    return f"{header}.{body}.{sig}"

def jwt_decode(token):
    try:
        parts = token.split(".")
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
        return payload
    except Exception:
        return None

def jwt_verify(token):
    """Returns decoded payload only if signature is valid."""
    try:
        parts = token.split(".")
        header_b, body_b, sig_b = parts[0], parts[1], parts[2]
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(JWT_SECRET.encode(), f"{header_b}.{body_b}".encode(), hashlib.sha256).digest()
        ).rstrip(b"=").decode()
        if sig_b != expected_sig:
            return None
        return json.loads(base64.urlsafe_b64decode(body_b + "=="))
    except Exception:
        return None

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SecureBank — Online Banking</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Courier New', Courier, monospace; background: #0d1117; color: #e6edf3; min-height: 100vh; }
    header { background: #161b22; border-bottom: 1px solid #30363d; padding: .75rem 2rem; display: flex; align-items: center; justify-content: space-between; }
    .brand { font-size: 1.1rem; font-weight: bold; color: #58a6ff; }
    .brand span { color: #3fb950; }
    header nav a { color: #8b949e; text-decoration: none; margin-left: 1.5rem; font-size: .85rem; }
    header nav a:hover { color: #e6edf3; }
    main { max-width: 960px; margin: 2rem auto; padding: 0 1.5rem; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1.25rem; margin-bottom: 1.25rem; }
    .card-title { font-size: .8rem; color: #8b949e; text-transform: uppercase; letter-spacing: .1em; margin-bottom: .75rem; border-bottom: 1px solid #21262d; padding-bottom: .5rem; }
    .stats-row { display: flex; gap: 1rem; }
    .stats-row .card { flex: 1; text-align: center; }
    .stat-value { font-size: 1.4rem; color: #3fb950; }
    .stat-label { font-size: .7rem; color: #8b949e; text-transform: uppercase; margin-top: .2rem; }
    table { width: 100%; border-collapse: collapse; font-size: .85rem; }
    th { text-align: left; padding: .5rem .75rem; color: #8b949e; border-bottom: 1px solid #30363d; font-weight: normal; font-size: .75rem; text-transform: uppercase; }
    td { padding: .5rem .75rem; border-bottom: 1px solid #21262d; }
    input, select { background: #21262d; border: 1px solid #30363d; color: #e6edf3; padding: .4rem .75rem; border-radius: 4px; font-family: inherit; font-size: .875rem; }
    input:focus { outline: none; border-color: #58a6ff; }
    button { background: #238636; border: 1px solid #2ea043; color: #fff; padding: .4rem 1rem; border-radius: 4px; font-family: inherit; font-size: .875rem; cursor: pointer; }
    button:hover { background: #2ea043; }
    .alert-error { background: rgba(248,81,73,.1); border: 1px solid rgba(248,81,73,.3); color: #f85149; padding: .6rem 1rem; border-radius: 4px; margin-bottom: 1rem; font-size: .85rem; }
    .alert-success { background: rgba(63,185,80,.1); border: 1px solid rgba(63,185,80,.3); color: #3fb950; padding: .6rem 1rem; border-radius: 4px; margin-bottom: 1rem; font-size: .85rem; }
    .form-row { display: flex; align-items: center; gap: .75rem; margin-bottom: .75rem; }
    .form-row label { color: #8b949e; font-size: .8rem; min-width: 100px; }
    code { background: #21262d; padding: .1rem .3rem; border-radius: 3px; font-size: .8rem; word-break: break-all; }
    .mono { font-family: 'Courier New', monospace; font-size: .8rem; word-break: break-all; }
    .result-box { background: #0d1117; border: 1px solid #30363d; border-radius: 4px; padding: 1rem; margin-top: .75rem; font-size: .82rem; line-height: 1.7; }
    .result-flag { border-color: rgba(63,185,80,.4); color: #3fb950; background: rgba(63,185,80,.05); }
    a { color: #58a6ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    footer { text-align: center; font-size: .7rem; color: #484f58; margin: 3rem 0 1rem; }
  </style>
</head>
<body>
<header>
  <div class="brand">Secure<span>Bank</span></div>
  <nav>
    {% if session.get('user') %}
    <a href="/dashboard">Dashboard</a>
    <a href="/hashes">Account Security</a>
    <a href="/jwt-data">API Access</a>
    <a href="/verify-crack">Identity Verify</a>
    <a href="/logout">Sign out</a>
    {% else %}
    <a href="/login">Sign in</a>
    {% endif %}
  </nav>
</header>
<main>
{{ content | safe }}
</main>
<footer>SecureBank &mdash; Member FDIC &mdash; &copy; 2024 SecureBank Corporation</footer>
</body>
</html>"""

def render(content, **ctx):
    return render_template_string(BASE, content=content, **ctx)

@app.route("/")
def index():
    if session.get("user"):
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        pwd_hash = hashlib.md5(password.encode()).hexdigest()
        user = USERS_DB.get(username)
        if user and user["hash_md5"] == pwd_hash:
            session["user"] = username
            session["role"] = user["role"]
            token = jwt_encode({"sub": username, "role": user["role"], "iat": int(time.time())})
            session["jwt"] = token
            return redirect("/dashboard")
        msg = "<div class='alert-error'>Authentication failed. Please check your credentials.</div>"
    content = f"""
    <div class="card" style="max-width:400px;margin:3rem auto">
      <div class="card-title">Online Banking — Sign In</div>
      {msg}
      <form method="POST">
        <div class="form-row"><label>Username</label><input name="username" autocomplete="username" style="flex:1"></div>
        <div class="form-row"><label>Password</label><input name="password" type="password" autocomplete="current-password" style="flex:1"></div>
        <div style="text-align:right;margin-top:.5rem"><button type="submit">Sign In</button></div>
      </form>
    </div>"""
    return render(content)

@app.route("/dashboard")
def dashboard():
    username = session.get("user")
    if not username:
        return redirect("/login")
    u = USERS_DB.get(username, {})
    txns = [
        ("2024-03-01", "Wire Transfer OUT", "-$1,200.00"),
        ("2024-02-28", "Payroll Deposit",   "+$4,500.00"),
        ("2024-02-26", "ATM Withdrawal",    "-$200.00"),
        ("2024-02-25", "Online Purchase",   "-$87.43"),
        ("2024-02-24", "Transfer IN",       "+$500.00"),
    ]
    txn_rows = "".join(
        f"<tr><td>{d}</td><td>{desc}</td><td style='color:{'#3fb950' if '+' in amt else '#f85149'}'>{amt}</td></tr>"
        for d, desc, amt in txns
    )
    content = f"""
    <div class="stats-row">
      <div class="card"><div class="stat-value">${u.get('balance', 0):,.2f}</div><div class="stat-label">Available Balance</div></div>
      <div class="card"><div class="stat-value" style="color:#58a6ff">{u.get('account','N/A')}</div><div class="stat-label">Account Number</div></div>
      <div class="card"><div class="stat-value" style="color:#8b949e">{u.get('role','user')}</div><div class="stat-label">Account Type</div></div>
    </div>
    <div class="card">
      <div class="card-title">Recent Transactions</div>
      <table>
        <thead><tr><th>Date</th><th>Description</th><th>Amount</th></tr></thead>
        <tbody>{txn_rows}</tbody>
      </table>
    </div>"""
    return render(content)

@app.route("/hashes")
def hashes():
    rows = "".join(
        f"<tr><td>{u}</td><td class='mono'>{data['hash_md5']}</td><td>MD5</td><td style='color:#8b949e'>{data['email']}</td></tr>"
        for u, data in USERS_DB.items()
    )
    content = f"""
    <div class="card">
      <div class="card-title">Credential Store</div>
      <table>
        <thead><tr><th>Username</th><th>Password Hash</th><th>Algorithm</th><th>Email</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""
    return render(content)

@app.route("/jwt-data", methods=["GET", "POST"])
def jwt_data():
    result = ""
    token_in = ""
    if request.method == "POST":
        token_in = request.form.get("token", "").strip()
        payload = jwt_verify(token_in)
        if payload:
            data = {
                "sub": payload.get("sub", "unknown"),
                "role": payload.get("role", "user"),
                "account_status": "active",
                "credit_limit": 5000,
            }
            if payload.get("role") == "admin":
                data["vault_key"] = _flag('a04_jwt')
                data["admin_console"] = "https://admin.securebank.internal"
            result = f"""
            <div class="result-box">
              <strong>Token validated successfully.</strong><br><br>
              {''.join(f'{k}: <strong>{v}</strong><br>' for k, v in data.items())}
            </div>"""
        else:
            result = "<div class='result-box'><span style='color:#f85149'>Invalid or tampered token.</span></div>"
    current_jwt = session.get("jwt", "")
    content = f"""
    <div class="card">
      <div class="card-title">API Token Inspection</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:1rem">
        Submit a signed JWT to retrieve your account data from the API.
      </p>
      <div style="margin-bottom:.75rem;font-size:.8rem;color:#8b949e">
        Your current session token:<br>
        <span class="mono">{current_jwt or '(not logged in)'}</span>
      </div>
      <form method="POST">
        <div class="form-row">
          <label>JWT Token</label>
          <input name="token" value="{token_in}" style="flex:1;font-size:.75rem">
        </div>
        <button type="submit">Submit</button>
      </form>
      {result}
    </div>"""
    return render(content)

@app.route("/verify-crack", methods=["GET", "POST"])
def verify_crack():
    result = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = USERS_DB.get(username)
        if user:
            pwd_hash = hashlib.md5(password.encode()).hexdigest()
            if pwd_hash == user["hash_md5"]:
                if username == "admin" and password == "admin":
                    result = f"""
                    <div class="result-box result-flag">
                      Security audit confirmed: administrator password is weak.<br><br>
                      MD5 hash: <code>{user['hash_md5']}</code><br>
                      Plaintext: <code>admin</code><br><br>
                      Audit token: <strong>{_flag('a04_hash')}</strong>
                    </div>"""
                else:
                    result = f"<div class='result-box'>Credentials verified for <strong>{username}</strong>.</div>"
            else:
                result = "<div class='result-box'><span style='color:#f85149'>Password mismatch.</span></div>"
        else:
            result = "<div class='result-box'><span style='color:#f85149'>User not found.</span></div>"
    content = f"""
    <div class="card">
      <div class="card-title">Security Credential Verification</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:1rem">
        Enter credentials to verify against the stored hash database.
      </p>
      <form method="POST">
        <div class="form-row"><label>Username</label><input name="username" style="width:200px"></div>
        <div class="form-row"><label>Password</label><input name="password" type="text" style="width:200px"></div>
        <button type="submit">Verify</button>
      </form>
      {result}
    </div>"""
    return render(content)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    from flask import jsonify
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
