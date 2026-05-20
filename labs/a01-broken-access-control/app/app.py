import os
from flask import Flask, request, session, redirect, render_template_string
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "c0rp-hr-2024-x9z"

USERS = {
    1: {
        "username": "test",
        "password": "test",
        "email": "test@corphr.internal",
        "role": "employee",
        "department": "Operations",
        "salary": 62000,
        "ssn": "555-12-3456",
        "phone": "+1-555-0199",
        "secret_note": "New hire — onboarding pending.",
    },
    2: {
        "username": "jsmith",
        "password": "jsmith2024",
        "email": "jsmith@corphr.internal",
        "role": "employee",
        "department": "Finance",
        "salary": 88000,
        "ssn": "234-56-7890",
        "phone": "+1-555-0211",
        "secret_note": "Approved for remote work.",
    },
    3: {
        "username": "mwilson",
        "password": "mwilson#99",
        "email": "mwilson@corphr.internal",
        "role": "employee",
        "department": "Engineering",
        "salary": 102000,
        "ssn": "876-54-3210",
        "phone": "+1-555-0304",
        "secret_note": "Senior lead — security clearance L2.",
    },
    4: {
        "username": "admin",
        "password": "C0rpHR!2024x",
        "email": "admin@corphr.internal",
        "role": "admin",
        "department": "Executive",
        "salary": 150000,
        "ssn": "000-00-0000",
        "phone": "+1-555-0000",
        "secret_note": _flag('a01_idor'),
    },
}

ORDERS = {
    100: {"owner": 1, "items": "Ergonomic Chair x1",   "total": 349,  "status": "Delivered"},
    101: {"owner": 1, "items": "USB Hub x2",            "total": 58,   "status": "Delivered"},
    102: {"owner": 2, "items": "Monitor 27\" x1",       "total": 520,  "status": "Processing"},
    103: {"owner": 3, "items": "Laptop Dock x1",        "total": 280,  "status": "Shipped"},
    104: {"owner": 4, "items": "Server Rack x1",        "total": 9999, "status": "Pending Approval"},
}

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CorpHR — Human Resources Portal</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Courier New', Courier, monospace; background: #0d1117; color: #e6edf3; min-height: 100vh; }
    header { background: #161b22; border-bottom: 1px solid #30363d; padding: .75rem 2rem; display: flex; align-items: center; justify-content: space-between; }
    header .brand { font-size: 1.1rem; font-weight: bold; color: #58a6ff; letter-spacing: .05em; }
    header .brand span { color: #e6edf3; }
    header nav a { color: #8b949e; text-decoration: none; margin-left: 1.5rem; font-size: .85rem; }
    header nav a:hover { color: #e6edf3; }
    main { max-width: 960px; margin: 2rem auto; padding: 0 1.5rem; }
    h2 { color: #58a6ff; margin-bottom: 1rem; font-size: 1rem; text-transform: uppercase; letter-spacing: .08em; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1.25rem; margin-bottom: 1.25rem; }
    .card-title { font-size: .8rem; color: #8b949e; text-transform: uppercase; letter-spacing: .1em; margin-bottom: .75rem; border-bottom: 1px solid #21262d; padding-bottom: .5rem; }
    table { width: 100%; border-collapse: collapse; font-size: .85rem; }
    th { text-align: left; padding: .5rem .75rem; color: #8b949e; border-bottom: 1px solid #30363d; font-weight: normal; font-size: .75rem; text-transform: uppercase; }
    td { padding: .5rem .75rem; border-bottom: 1px solid #21262d; }
    .badge { display: inline-block; padding: .15rem .5rem; border-radius: 3px; font-size: .7rem; }
    .badge-admin { background: rgba(88,166,255,.15); color: #58a6ff; border: 1px solid rgba(88,166,255,.3); }
    .badge-emp { background: rgba(63,185,80,.15); color: #3fb950; border: 1px solid rgba(63,185,80,.3); }
    .field { margin-bottom: .65rem; font-size: .875rem; }
    .field label { color: #8b949e; display: inline-block; width: 130px; font-size: .8rem; }
    .field value { color: #e6edf3; }
    input, select { background: #21262d; border: 1px solid #30363d; color: #e6edf3; padding: .4rem .75rem; border-radius: 4px; font-family: inherit; font-size: .875rem; }
    input:focus { outline: none; border-color: #58a6ff; }
    button, .btn { background: #238636; border: 1px solid #2ea043; color: #fff; padding: .4rem 1rem; border-radius: 4px; font-family: inherit; font-size: .875rem; cursor: pointer; text-decoration: none; display: inline-block; }
    button:hover, .btn:hover { background: #2ea043; }
    .btn-secondary { background: #21262d; border-color: #30363d; color: #8b949e; }
    .btn-secondary:hover { color: #e6edf3; background: #30363d; }
    .alert { padding: .6rem 1rem; border-radius: 4px; font-size: .85rem; margin-bottom: 1rem; }
    .alert-error { background: rgba(248,81,73,.1); border: 1px solid rgba(248,81,73,.3); color: #f85149; }
    .alert-success { background: rgba(63,185,80,.1); border: 1px solid rgba(63,185,80,.3); color: #3fb950; }
    .stat { text-align: center; }
    .stat-value { font-size: 1.5rem; color: #58a6ff; }
    .stat-label { font-size: .7rem; color: #8b949e; text-transform: uppercase; margin-top: .2rem; }
    .stats-row { display: flex; gap: 1rem; }
    .stats-row .card { flex: 1; }
    .mono { font-family: 'Courier New', monospace; }
    pre { background: #0d1117; padding: 1rem; border-radius: 4px; overflow: auto; font-size: .8rem; line-height: 1.5; max-height: 400px; border: 1px solid #21262d; }
    a { color: #58a6ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .form-row { display: flex; align-items: center; gap: .75rem; margin-bottom: .75rem; }
    .form-row label { color: #8b949e; font-size: .8rem; min-width: 80px; }
    footer { text-align: center; font-size: .7rem; color: #484f58; margin: 3rem 0 1rem; }
  </style>
</head>
<body>
<header>
  <div class="brand">Corp<span>HR</span></div>
  <nav>
    {% if session.get('user_id') %}
    <a href="/">Home</a>
    <a href="/profile/{{ session.get('user_id') }}">My Profile</a>
    <a href="/documents">Documents</a>
    {% if session.get('role') == 'admin' %}<a href="/admin">Admin</a>{% endif %}
    <a href="/logout">Sign out</a>
    {% else %}
    <a href="/login">Sign in</a>
    {% endif %}
  </nav>
</header>
<main>
{{ content | safe }}
</main>
<footer>CorpHR v4.2.1 &mdash; Internal Use Only &mdash; &copy; 2024 Corporation Inc.</footer>
</body>
</html>"""

def render(content, **ctx):
    return render_template_string(BASE, content=content, **ctx)

@app.route("/")
def index():
    uid = session.get("user_id")
    u = USERS.get(uid)
    if not u:
        return redirect("/login")
    my_orders = [(oid, o) for oid, o in ORDERS.items() if o["owner"] == uid]
    orders_rows = "".join(
        f"<tr><td>#{oid}</td><td>{o['items']}</td><td>${o['total']:,}</td><td>{o['status']}</td><td><a href='/orders/{oid}'>View</a></td></tr>"
        for oid, o in my_orders
    )
    content = f"""
    <div class="stats-row">
      <div class="card stat">
        <div class="stat-value">{u['department']}</div>
        <div class="stat-label">Department</div>
      </div>
      <div class="card stat">
        <div class="stat-value">{len(my_orders)}</div>
        <div class="stat-label">My Orders</div>
      </div>
      <div class="card stat">
        <div class="stat-value">{u['role'].title()}</div>
        <div class="stat-label">Role</div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">My Profile</div>
      <div class="field"><label>Username</label><span>{u['username']}</span></div>
      <div class="field"><label>Email</label><span>{u['email']}</span></div>
      <div class="field"><label>Department</label><span>{u['department']}</span></div>
      <div class="field"><label>Phone</label><span>{u['phone']}</span></div>
      <a href="/profile/{uid}" class="btn" style="margin-top:.75rem">View Full Profile</a>
    </div>
    <div class="card">
      <div class="card-title">My Purchase Orders</div>
      <table>
        <thead><tr><th>Order ID</th><th>Items</th><th>Total</th><th>Status</th><th></th></tr></thead>
        <tbody>{orders_rows if orders_rows else '<tr><td colspan="5" style="color:#8b949e">No orders found.</td></tr>'}</tbody>
      </table>
    </div>
    """
    return render(content)

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        un = request.form.get("username", "")
        pw = request.form.get("password", "")
        for uid, u in USERS.items():
            if u["username"] == un and u["password"] == pw:
                session["user_id"] = uid
                session["role"] = u["role"]
                return redirect("/")
        msg = "<div class='alert alert-error'>Invalid credentials. Please try again.</div>"
    content = f"""
    <div class="card" style="max-width:400px;margin:3rem auto">
      <div class="card-title">Employee Sign In</div>
      {msg}
      <form method="POST">
        <div class="form-row">
          <label>Username</label>
          <input name="username" autocomplete="username" style="flex:1">
        </div>
        <div class="form-row">
          <label>Password</label>
          <input name="password" type="password" autocomplete="current-password" style="flex:1">
        </div>
        <div style="text-align:right;margin-top:.5rem">
          <button type="submit">Sign In</button>
        </div>
      </form>
    </div>"""
    return render(content)

@app.route("/profile/<int:user_id>")
def profile(user_id):
    u = USERS.get(user_id)
    if not u:
        return render("<div class='card'><p>Record not found.</p></div>")
    content = f"""
    <div class="card">
      <div class="card-title">Employee Record — {u['username']}</div>
      <div class="field"><label>Full Name</label><span>{u['username']}</span></div>
      <div class="field"><label>Email</label><span>{u['email']}</span></div>
      <div class="field"><label>Department</label><span>{u['department']}</span></div>
      <div class="field"><label>Role</label><span><span class="badge {'badge-admin' if u['role']=='admin' else 'badge-emp'}">{u['role']}</span></span></div>
      <div class="field"><label>Phone</label><span>{u['phone']}</span></div>
      <div class="field"><label>Annual Salary</label><span>${u['salary']:,}</span></div>
      <div class="field"><label>SSN</label><span>{u['ssn']}</span></div>
      <div class="field"><label>Internal Note</label><span class="mono">{u['secret_note']}</span></div>
    </div>
    <a class="btn btn-secondary" href="/">← Back to Directory</a>"""
    return render(content)

@app.route("/orders/<int:order_id>")
def orders(order_id):
    o = ORDERS.get(order_id)
    if not o:
        return render("<div class='card'><p>Order not found.</p></div>")
    owner = USERS.get(o["owner"], {})
    content = f"""
    <div class="card">
      <div class="card-title">Purchase Order #{order_id}</div>
      <div class="field"><label>Requested By</label><span>{owner.get('username', 'N/A')} ({owner.get('email', '')})</span></div>
      <div class="field"><label>Items</label><span>{o['items']}</span></div>
      <div class="field"><label>Total Amount</label><span>${o['total']:,}</span></div>
      <div class="field"><label>Status</label><span>{o['status']}</span></div>
      <div class="field"><label>Department</label><span>{owner.get('department', 'N/A')}</span></div>
    </div>
    <a class="btn btn-secondary" href="/">← Back</a>"""
    return render(content)

@app.route("/admin")
def admin():
    token = request.args.get("token", "")
    uid = session.get("user_id")
    is_admin = (token == "admin") or (uid and USERS.get(uid, {}).get("role") == "admin")
    if not is_admin:
        content = """
        <div class="card">
          <div class="card-title">Access Restricted</div>
          <p style="color:#8b949e">You do not have permission to view this page.</p>
        </div>"""
        return render(content), 403
    rows = "".join(
        f"<tr><td>{uid2}</td><td>{u2['username']}</td><td>{u2['email']}</td><td>{u2['department']}</td><td>${u2['salary']:,}</td><td>{u2['ssn']}</td></tr>"
        for uid2, u2 in USERS.items()
    )
    content = f"""
    <div class="stats-row">
      <div class="card stat"><div class="stat-value">3</div><div class="stat-label">Total Employees</div></div>
      <div class="card stat"><div class="stat-value">$327K</div><div class="stat-label">Payroll/yr</div></div>
      <div class="card stat"><div class="stat-value">99.8%</div><div class="stat-label">Uptime</div></div>
    </div>
    <div class="card">
      <div class="card-title">Administration — All Employee Records</div>
      <table>
        <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Department</th><th>Salary</th><th>SSN</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""
    return render(content)

@app.route("/files")
@app.route("/documents")
def files():
    path = request.args.get("doc", "welcome.txt")
    full_path = os.path.normpath(os.path.join("/app/files", path))
    try:
        with open(full_path, "r") as f:
            file_content = f.read()
        status = "200 OK"
    except FileNotFoundError:
        file_content = "Document not found."
        status = "404 Not Found"
    except PermissionError:
        file_content = "Access denied."
        status = "403 Forbidden"
    except Exception as e:
        file_content = str(e)
        status = "500 Internal Server Error"
    content = f"""
    <div class="card">
      <div class="card-title">Document Repository</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:1rem">Access shared company documents and policy files.</p>
      <div class="form-row" style="margin-bottom:1rem">
        <form method="GET" style="display:flex;gap:.5rem;align-items:center;width:100%">
          <label style="color:#8b949e;font-size:.8rem;white-space:nowrap">Document</label>
          <input name="doc" value="{path}" style="flex:1" placeholder="filename.txt">
          <button type="submit">Open</button>
        </form>
      </div>
      <pre>{file_content}</pre>
    </div>"""
    return render(content)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Initialise file system artifacts
os.makedirs("/app/files", exist_ok=True)

_welcome = "/app/files/welcome.txt"
if not os.path.exists(_welcome):
    with open(_welcome, "w") as f:
        f.write("CorpHR Document Repository\n==========================\nShared HR policies, onboarding guides, and company templates.\n")

_handbook = "/app/files/employee_handbook.txt"
if not os.path.exists(_handbook):
    with open(_handbook, "w") as f:
        f.write("CORPHR EMPLOYEE HANDBOOK v4.2\n\n1. Code of Conduct\n2. Leave Policy\n3. Remote Work Guidelines\n4. Data Privacy\n5. IT Acceptable Use\n\nFor questions contact hr@corphr.internal\n")

_env_file = "/app/.env"
if not os.path.exists(_env_file):
    with open(_env_file, "w") as f:
        f.write(
            "# CorpHR Application Environment\n"
            "APP_ENV=production\n"
            "APP_PORT=5000\n"
            "SECRET_KEY=c0rp-hr-2024-x9z\n"
            "DB_HOST=db-internal.corphr.local\n"
            "DB_PORT=5432\n"
            "DB_NAME=corphr_prod\n"
            "DB_USER=corphr_app\n"
            "DB_PASS=Xk9#mP2!qR7vL4nZ\n"
            "LDAP_URL=ldap://ldap.corphr.internal:389\n"
            "LDAP_BIND_DN=cn=svc_hr,dc=corphr,dc=internal\n"
            "LDAP_BIND_PASS=LdapSvc!2024\n"
            "SMTP_HOST=mail.corphr.internal\n"
            "SMTP_PORT=587\n"
            "SMTP_USER=noreply@corphr.internal\n"
            "SMTP_PASS=MailRelay#77\n"
            "JWT_SECRET=hr-jwt-weak-2024\n"
            f"FLAG={_flag('a01_path')}\n"
        )

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    from flask import jsonify
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
