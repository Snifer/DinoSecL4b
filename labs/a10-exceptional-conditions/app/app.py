import json
import traceback
from flask import Flask, request, render_template_string, jsonify
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "dataapi-prod-2024"
app.config["FLAG_KEY"] = _flag('a10_trace')
app.config["DB_HOST"] = "db-internal.corp.local"
app.config["DB_USER"] = "svc_dataapi"
app.config["API_VERSION"] = "v2.4.1"

ACCOUNTS = {
    "ACC001": {"owner": "alice.morgan",   "balance": 58200.00,  "active": True,  "tier": "Premium"},
    "ACC002": {"owner": "bob.chen",       "balance": 12800.50,  "active": True,  "tier": "Standard"},
    "ACC003": {"owner": "admin.service",  "balance": 990000.00, "active": False, "tier": "Enterprise"},
}

DATASETS = {
    "sales_q4":   {"rows": 18420, "cols": 12, "updated": "2024-11-30"},
    "hr_headcount":{"rows": 342,  "cols": 8,  "updated": "2024-12-01"},
    "finance_ytd":{"rows": 5200,  "cols": 25, "updated": "2024-11-28"},
}

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DataAPI &mdash; Enterprise Data &amp; Analytics Portal</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',Arial,sans-serif;background:#f0f4f8;color:#1a2035;min-height:100vh}
    header{background:#1a2035;color:#fff;padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:62px;box-shadow:0 2px 8px rgba(0,0,0,.4)}
    header .logo{font-size:1.4rem;font-weight:700}
    header .logo span{color:#43e97b}
    header .tagline{font-size:.8rem;color:#90caf9}
    nav{background:#222d45;border-bottom:3px solid #43e97b}
    nav a{color:#a8c5da;text-decoration:none;padding:.75rem 1.2rem;display:inline-block;font-size:.87rem;transition:background .2s}
    nav a:hover{background:#1a2035;color:#fff}
    .container{max-width:1050px;margin:0 auto;padding:2rem 1.5rem}
    .page-title{font-size:1.4rem;font-weight:600;color:#1a2035;margin-bottom:1.4rem;border-bottom:2px solid #dde3ef;padding-bottom:.5rem}
    .card{background:#fff;border-radius:8px;box-shadow:0 1px 5px rgba(0,0,0,.09);padding:1.6rem;margin-bottom:1.4rem}
    .card h3{color:#1a2035;font-size:1.05rem;margin-bottom:1rem}
    .btn{display:inline-block;padding:.55rem 1.5rem;border-radius:5px;border:none;cursor:pointer;font-size:.9rem;font-weight:600;transition:background .2s;text-decoration:none}
    .btn-primary{background:#1a6fcf;color:#fff}.btn-primary:hover{background:#145ab5}
    .btn-outline{background:#fff;color:#1a2035;border:1px solid #b0bec5}.btn-outline:hover{background:#f0f4f8}
    input,textarea{border:1px solid #b0bec5;border-radius:5px;padding:.55rem .85rem;font-size:.9rem;width:100%;background:#fafbfc;color:#1a2035;font-family:'Courier New',monospace}
    input:focus,textarea:focus{outline:none;border-color:#1a6fcf;box-shadow:0 0 0 2px rgba(26,111,207,.15)}
    .form-group{margin-bottom:1rem}
    .form-group label{display:block;margin-bottom:.3rem;font-weight:500;color:#455a64;font-size:.88rem;font-family:'Segoe UI',Arial,sans-serif}
    .alert{padding:.75rem 1.1rem;border-radius:5px;margin:.8rem 0;font-size:.9rem}
    .alert-success{background:#e8f5e9;color:#1b5e20;border-left:4px solid #27ae60}
    .alert-danger{background:#fce4ec;color:#b71c1c;border-left:4px solid #e53935}
    .alert-warning{background:#fff8e1;color:#f57f17;border-left:4px solid #f9a825}
    .alert-info{background:#e3f2fd;color:#0d47a1;border-left:4px solid #1565c0}
    table{width:100%;border-collapse:collapse;font-size:.88rem}
    th{background:#1a2035;color:#fff;padding:.65rem .9rem;text-align:left}
    td{padding:.6rem .9rem;border-bottom:1px solid #e8edf2}
    tr:hover td{background:#f5f8fc}
    .badge{display:inline-block;padding:.2rem .65rem;border-radius:12px;font-size:.75rem;font-weight:600}
    .badge-green{background:#e8f5e9;color:#2e7d32}
    .badge-blue{background:#e3f2fd;color:#1565c0}
    .badge-orange{background:#fff3e0;color:#e65100}
    .badge-red{background:#fce4ec;color:#b71c1c}
    pre{background:#1a1f2e;color:#f8f8f2;padding:1.2rem;border-radius:6px;overflow:auto;max-height:450px;font-size:.78rem;line-height:1.6;font-family:'Courier New',monospace}
    code{background:#f0f4f8;border:1px solid #dde3ef;border-radius:3px;padding:.15rem .4rem;font-size:.85em}
    .stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin-bottom:1.5rem}
    .stat-card{background:#fff;border-radius:8px;padding:1.2rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.1);border-left:4px solid #1a6fcf}
    .stat-card .num{font-size:1.9rem;font-weight:700;color:#1a2035}
    .stat-card .lbl{color:#78909c;font-size:.82rem;margin-top:.2rem}
    footer{background:#1a2035;color:#78909c;text-align:center;padding:1rem;font-size:.8rem;margin-top:3rem}
  </style>
</head>
<body>
<header>
  <div class="logo">Data<span>API</span></div>
  <div class="tagline">Enterprise Data &amp; Analytics Portal &mdash; v2.4.1</div>
</header>
<nav>
  <a href="/">Dashboard</a>
  <a href="/query">Data Query</a>
  <a href="/account/ACC001">Accounts</a>
  <a href="/calculate">Calculator</a>
  <a href="/datasets">Datasets</a>
</nav>
<div class="container">
CONTENT_PLACEHOLDER
</div>
<footer>DataAPI &copy; 2024 &mdash; Enterprise Data &amp; Analytics Platform &mdash; Authorized access only</footer>
</body>
</html>"""

def render(content):
    return BASE.replace("CONTENT_PLACEHOLDER", content)

@app.route("/")
def index():
    content = """
    <div class="page-title">Analytics Dashboard</div>
    <div class="stat-grid">
      <div class="stat-card"><div class="num">23,962</div><div class="lbl">Total Records</div></div>
      <div class="stat-card" style="border-color:#43e97b"><div class="num">3</div><div class="lbl">Active Datasets</div></div>
      <div class="stat-card" style="border-color:#f9a825"><div class="num">142ms</div><div class="lbl">Avg Query Time</div></div>
      <div class="stat-card" style="border-color:#1565c0"><div class="num">99.9%</div><div class="lbl">API Uptime</div></div>
    </div>
    <div class="card">
      <h3>Welcome to DataAPI</h3>
      <p style="color:#546e7a;line-height:1.8">Enterprise data access and analytics platform. Query structured datasets, retrieve account information, and perform financial calculations through a unified API interface.</p>
      <div style="margin-top:1rem;display:flex;gap:.8rem;flex-wrap:wrap">
        <a href="/query" class="btn btn-primary">Run Query</a>
        <a href="/account/ACC001" class="btn btn-outline">Browse Accounts</a>
        <a href="/calculate" class="btn btn-outline">Calculator</a>
      </div>
    </div>
    <div class="card">
      <h3>Available Datasets</h3>
      <table>
        <tr><th>Dataset</th><th>Rows</th><th>Columns</th><th>Last Updated</th><th>Status</th></tr>
        <tr><td>sales_q4</td><td>18,420</td><td>12</td><td>2024-11-30</td><td><span class="badge badge-green">Active</span></td></tr>
        <tr><td>hr_headcount</td><td>342</td><td>8</td><td>2024-12-01</td><td><span class="badge badge-green">Active</span></td></tr>
        <tr><td>finance_ytd</td><td>5,200</td><td>25</td><td>2024-11-28</td><td><span class="badge badge-green">Active</span></td></tr>
      </table>
    </div>"""
    return render(content)

@app.route("/query", methods=["GET", "POST"])
def query():
    result = ""
    if request.method == "POST":
        raw = request.form.get("payload", "")
        data = json.loads(raw)
        dataset = data["dataset"]
        field = data["field"]
        ds = DATASETS[dataset]
        value = ds[field]
        result = f"""
        <div class="alert alert-success">
          <strong>Query result:</strong> <code>{dataset}.{field}</code> = <strong>{value}</strong>
        </div>"""

    content = f"""
    <div class="page-title">Data Query Interface</div>
    <div class="card">
      <h3>JSON Query</h3>
      <p style="color:#546e7a;margin-bottom:1rem">Submit a JSON payload specifying the dataset and field to retrieve. The API processes the request and returns the matching record.</p>
      <form method="POST">
        <div class="form-group">
          <label>Query Payload (JSON)</label>
          <textarea name="payload" rows="6" placeholder='{"dataset": "sales_q4", "field": "rows"}'></textarea>
        </div>
        <button class="btn btn-primary" type="submit">Execute Query</button>
      </form>
      {result}
    </div>
    <div class="card">
      <h3>Query Schema</h3>
      <p style="color:#546e7a;margin-bottom:.5rem">Valid datasets: <code>sales_q4</code>, <code>hr_headcount</code>, <code>finance_ytd</code></p>
      <p style="color:#546e7a">Valid fields: <code>rows</code>, <code>cols</code>, <code>updated</code></p>
    </div>"""
    return render(content)

@app.route("/account/<account_id>")
def get_account(account_id):
    try:
        account = ACCOUNTS.get(account_id)
        is_active = account["active"]
        owner = account["owner"]
        balance = account["balance"]
        tier = account["tier"]
        status_badge = "<span class='badge badge-green'>Active</span>" if is_active else "<span class='badge badge-red'>Inactive</span>"
        content = f"""
        <div class="page-title">Account Details</div>
        <div class="card">
          <h3>Account <code>{account_id}</code></h3>
          <table>
            <tr><th>Field</th><th>Value</th></tr>
            <tr><td>Account ID</td><td><strong>{account_id}</strong></td></tr>
            <tr><td>Owner</td><td>{owner}</td></tr>
            <tr><td>Balance</td><td>${balance:,.2f}</td></tr>
            <tr><td>Tier</td><td><span class="badge badge-blue">{tier}</span></td></tr>
            <tr><td>Status</td><td>{status_badge}</td></tr>
          </table>
          <div style="margin-top:1rem;display:flex;gap:.8rem">
            <a href="/account/ACC001" class="btn btn-outline">ACC001</a>
            <a href="/account/ACC002" class="btn btn-outline">ACC002</a>
            <a href="/account/ACC003" class="btn btn-outline">ACC003</a>
          </div>
        </div>"""
        return render(content)
    except TypeError:
        return _flag('a10_bypass'), 200

@app.route("/calculate", methods=["GET", "POST"])
def calculate():
    result = ""
    if request.method == "POST":
        a = float(request.form.get("a", "0"))
        b = float(request.form.get("b", "1"))
        res = a / b
        result = f"""
        <div class="alert alert-success">
          Result: <strong>{a} &divide; {b} = {res:.6f}</strong>
        </div>"""

    content = f"""
    <div class="page-title">Financial Calculator</div>
    <div class="card">
      <h3>Division Calculator</h3>
      <p style="color:#546e7a;margin-bottom:1rem">Compute financial ratios, rate calculations, and division operations across datasets.</p>
      <form method="POST">
        <div class="form-group">
          <label>Numerator (A)</label>
          <input name="a" type="number" step="any" placeholder="e.g. 1000000" style="font-family:'Segoe UI',Arial,sans-serif">
        </div>
        <div class="form-group">
          <label>Denominator (B)</label>
          <input name="b" type="number" step="any" placeholder="e.g. 12" style="font-family:'Segoe UI',Arial,sans-serif">
        </div>
        <button class="btn btn-primary" type="submit">Calculate</button>
      </form>
      {result}
    </div>"""
    return render(content)

@app.route("/datasets")
def datasets():
    rows = ""
    for name, ds in DATASETS.items():
        rows += f"<tr><td><code>{name}</code></td><td>{ds['rows']:,}</td><td>{ds['cols']}</td><td>{ds['updated']}</td><td><span class='badge badge-green'>Active</span></td></tr>"
    content = f"""
    <div class="page-title">Dataset Catalog</div>
    <div class="card">
      <h3>Available Datasets</h3>
      <table>
        <tr><th>Name</th><th>Rows</th><th>Columns</th><th>Updated</th><th>Status</th></tr>
        {rows}
      </table>
    </div>
    <div class="card">
      <h3>Access via Query API</h3>
      <p style="color:#546e7a">Use the <a href="/query" style="color:#1a6fcf">Data Query</a> interface to retrieve records from any active dataset.</p>
    </div>"""
    return render(content)

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
