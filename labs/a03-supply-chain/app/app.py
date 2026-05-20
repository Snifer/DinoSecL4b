import hashlib
from flask import Flask, request, render_template_string
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "pkgmgr-2024-internal"

DEPENDENCIES = [
    {"name": "requests",     "installed": "2.25.0",  "latest": "2.31.0",  "license": "Apache-2.0", "cve": "CVE-2023-32681", "severity": "MEDIUM"},
    {"name": "pillow",       "installed": "8.0.0",   "latest": "10.0.1",  "license": "HPND",        "cve": "CVE-2023-44271", "severity": "HIGH"},
    {"name": "cryptography", "installed": "2.8",     "latest": "41.0.6",  "license": "Apache-2.0",  "cve": "CVE-2023-49083", "severity": "HIGH"},
    {"name": "flask",        "installed": "0.12.2",  "latest": "3.0.3",   "license": "BSD-3-Clause","cve": "CVE-2018-1000656","severity": "HIGH"},
    {"name": "pyyaml",       "installed": "3.13",    "latest": "6.0.1",   "license": "MIT",          "cve": "CVE-2020-1747",  "severity": "CRITICAL"},
    {"name": "sqlalchemy",   "installed": "1.3.0",   "latest": "2.0.23",  "license": "MIT",          "cve": "CVE-2019-7164",  "severity": "HIGH"},
    {"name": "paramiko",     "installed": "1.17.0",  "latest": "3.4.0",   "license": "LGPL-2.1",    "cve": "CVE-2018-7750",  "severity": "CRITICAL"},
    {"name": "urllib3",      "installed": "1.24.1",  "latest": "2.1.0",   "license": "MIT",          "cve": "CVE-2023-45803", "severity": "MEDIUM"},
    {"name": "jinja2",       "installed": "2.10.0",  "latest": "3.1.3",   "license": "BSD-3-Clause","cve": "CVE-2019-10906", "severity": "MEDIUM"},
    {"name": "werkzeug",     "installed": "0.14.1",  "latest": "3.0.1",   "license": "BSD-3-Clause","cve": "CVE-2023-46136", "severity": "HIGH"},
    {"name": "numpy",        "installed": "1.19.0",  "latest": "1.26.3",  "license": "BSD-3-Clause","cve": "CVE-2021-33430", "severity": "LOW"},
    {"name": "django",       "installed": "2.2.0",   "latest": "4.2.9",   "license": "BSD-3-Clause","cve": "CVE-2021-35042", "severity": "CRITICAL"},
]

INTERNAL_PACKAGES = [
    {"name": "corp-utils",      "version": "1.0.0", "registry": "pypi.corp.internal:8080", "hash": None},
    {"name": "internal-auth",   "version": "2.1.0", "registry": "pypi.corp.internal:8080", "hash": None},
    {"name": "data-pipeline",   "version": "0.8.3", "registry": "pypi.corp.internal:8080", "hash": "sha256:a1b2c3"},
    {"name": "report-engine",   "version": "3.0.1", "registry": "pypi.corp.internal:8080", "hash": None},
]

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PkgManager — Dependency Management</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Courier New', Courier, monospace; background: #0d1117; color: #e6edf3; min-height: 100vh; }
    header { background: #161b22; border-bottom: 1px solid #30363d; padding: .75rem 2rem; display: flex; align-items: center; justify-content: space-between; }
    .brand { font-size: 1.1rem; font-weight: bold; color: #58a6ff; }
    .brand span { color: #e6edf3; }
    header nav a { color: #8b949e; text-decoration: none; margin-left: 1.5rem; font-size: .85rem; }
    header nav a:hover { color: #e6edf3; }
    main { max-width: 1080px; margin: 2rem auto; padding: 0 1.5rem; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1.25rem; margin-bottom: 1.25rem; }
    .card-title { font-size: .8rem; color: #8b949e; text-transform: uppercase; letter-spacing: .1em; margin-bottom: .75rem; border-bottom: 1px solid #21262d; padding-bottom: .5rem; }
    .stats-row { display: flex; gap: 1rem; }
    .stats-row .card { flex: 1; text-align: center; }
    .stat-value { font-size: 1.5rem; color: #58a6ff; }
    .stat-label { font-size: .7rem; color: #8b949e; text-transform: uppercase; margin-top: .2rem; }
    table { width: 100%; border-collapse: collapse; font-size: .82rem; }
    th { text-align: left; padding: .5rem .75rem; color: #8b949e; border-bottom: 1px solid #30363d; font-weight: normal; font-size: .72rem; text-transform: uppercase; }
    td { padding: .45rem .75rem; border-bottom: 1px solid #21262d; }
    .sev-CRITICAL { color: #ff6b6b; font-weight: bold; }
    .sev-HIGH { color: #f85149; }
    .sev-MEDIUM { color: #d29922; }
    .sev-LOW { color: #3fb950; }
    .badge-outdated { background: rgba(248,81,73,.15); color: #f85149; border: 1px solid rgba(248,81,73,.3); padding: .1rem .4rem; border-radius: 3px; font-size: .68rem; }
    .badge-ok { background: rgba(63,185,80,.15); color: #3fb950; border: 1px solid rgba(63,185,80,.3); padding: .1rem .4rem; border-radius: 3px; font-size: .68rem; }
    input { background: #21262d; border: 1px solid #30363d; color: #e6edf3; padding: .4rem .75rem; border-radius: 4px; font-family: inherit; font-size: .875rem; }
    button { background: #238636; border: 1px solid #2ea043; color: #fff; padding: .4rem 1rem; border-radius: 4px; font-family: inherit; font-size: .875rem; cursor: pointer; }
    button:hover { background: #2ea043; }
    .form-row { display: flex; align-items: center; gap: .75rem; margin-bottom: .75rem; }
    .form-row label { color: #8b949e; font-size: .8rem; min-width: 100px; }
    .result-box { background: #0d1117; border: 1px solid #30363d; border-radius: 4px; padding: 1rem; margin-top: .75rem; font-size: .82rem; line-height: 1.6; }
    .result-flag { background: rgba(63,185,80,.08); border-color: rgba(63,185,80,.3); color: #3fb950; }
    pre { background: #0d1117; padding: 1rem; border-radius: 4px; overflow: auto; font-size: .78rem; line-height: 1.6; border: 1px solid #21262d; }
    a { color: #58a6ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    footer { text-align: center; font-size: .7rem; color: #484f58; margin: 3rem 0 1rem; }
  </style>
</head>
<body>
<header>
  <div class="brand">Pkg<span>Manager</span></div>
  <nav>
    <a href="/">Overview</a>
    <a href="/dependencies">Dependencies</a>
    <a href="/cve-check">CVE Lookup</a>
    <a href="/registry">Registry</a>
    <a href="/install">Install</a>
  </nav>
</header>
<main>
{{ content | safe }}
</main>
<footer>PkgManager v1.8.3 &mdash; Internal Package Governance Platform &mdash; &copy; 2024</footer>
</body>
</html>"""

def render(content, **ctx):
    return render_template_string(BASE, content=content, **ctx)

@app.route("/")
def index():
    critical = sum(1 for p in DEPENDENCIES if p["severity"] == "CRITICAL")
    high = sum(1 for p in DEPENDENCIES if p["severity"] == "HIGH")
    medium = sum(1 for p in DEPENDENCIES if p["severity"] == "MEDIUM")
    content = f"""
    <div class="stats-row">
      <div class="card"><div class="stat-value" style="color:#ff6b6b">{critical}</div><div class="stat-label">Critical</div></div>
      <div class="card"><div class="stat-value" style="color:#f85149">{high}</div><div class="stat-label">High</div></div>
      <div class="card"><div class="stat-value" style="color:#d29922">{medium}</div><div class="stat-label">Medium</div></div>
      <div class="card"><div class="stat-value">{len(DEPENDENCIES)}</div><div class="stat-label">Total Packages</div></div>
    </div>
    <div class="card">
      <div class="card-title">Dependency Status Summary</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:.75rem">
        Last scan: 2024-03-01 06:00 UTC &mdash; {len([p for p in DEPENDENCIES if p['installed'] != p['latest']])} packages require updates.
      </p>
      <table>
        <thead><tr><th>Package</th><th>Installed</th><th>Latest</th><th>License</th><th>Known CVE</th><th>Severity</th></tr></thead>
        <tbody>
          {''.join(f"<tr><td>{p['name']}</td><td><span class='badge-outdated'>{p['installed']}</span></td><td>{p['latest']}</td><td style='color:#8b949e'>{p['license']}</td><td style='font-size:.75rem'>{p['cve']}</td><td class='sev-{p['severity']}'>{p['severity']}</td></tr>" for p in DEPENDENCIES)}
        </tbody>
      </table>
    </div>"""
    return render(content)

@app.route("/dependencies")
def dependencies():
    rows = ""
    for p in DEPENDENCIES:
        status = "badge-outdated" if p["installed"] != p["latest"] else "badge-ok"
        rows += (
            f"<tr><td>{p['name']}</td>"
            f"<td><span class='{status}'>{p['installed']}</span></td>"
            f"<td>{p['latest']}</td>"
            f"<td>{p['license']}</td>"
            "<td><a href='https://nvd.nist.gov/vuln/detail/" + p['cve'] + "' target='_blank' style='font-size:.75rem'>" + p['cve'] + "</a></td>"
            "<td class='sev-" + p['severity'] + "'>" + p['severity'] + "</td></tr>"
        )
    content = f"""
    <div class="card">
      <div class="card-title">Full Dependency Manifest</div>
      <table>
        <thead><tr><th>Package</th><th>Installed</th><th>Latest</th><th>License</th><th>CVE</th><th>Severity</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""
    return render(content)

@app.route("/cve-check", methods=["GET", "POST"])
def cve_check():
    result = ""
    cve_input = ""
    if request.method == "POST":
        cve_input = request.form.get("cve_id", "").strip()
        if cve_input == "CVE-2020-1747":
            result = f"""
            <div class="result-box result-flag">
              <strong>CVE-2020-1747 — PyYAML Arbitrary Code Execution</strong><br><br>
              Package: pyyaml 3.13<br>
              CVSS Score: 9.8 (Critical)<br>
              Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H<br>
              Description: The yaml.load() function in PyYAML before 5.3.1 allows arbitrary code
              execution when processing untrusted YAML input due to unsafe default Loader.<br><br>
              Verification token: <strong>{_flag('a03_cve')}</strong>
            </div>"""
        elif cve_input:
            match = next((p for p in DEPENDENCIES if p["cve"] == cve_input), None)
            if match:
                result = f"""
                <div class="result-box">
                  <strong>{cve_input}</strong><br>
                  Package: {match['name']} {match['installed']}<br>
                  Severity: <span class="sev-{match['severity']}">{match['severity']}</span><br>
                  Remediation: upgrade to {match['latest']}
                </div>"""
            else:
                result = f"""
                <div class="result-box">
                  <span style="color:#8b949e">No matching CVE found in current manifest for: {cve_input}</span>
                </div>"""
    content = f"""
    <div class="card">
      <div class="card-title">CVE Lookup</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:1rem">
        Enter a CVE identifier to check if any installed dependency is affected.
      </p>
      <form method="POST">
        <div class="form-row">
          <label>CVE ID</label>
          <input name="cve_id" value="{cve_input}" placeholder="CVE-YYYY-NNNNN" style="width:220px">
          <button type="submit">Check</button>
        </div>
      </form>
      {result}
    </div>"""
    return render(content)

@app.route("/registry")
def registry():
    rows = ""
    for p in INTERNAL_PACKAGES:
        hash_display = p["hash"] if p["hash"] else "<span style='color:#f85149'>not verified</span>"
        rows += f"<tr><td>{p['name']}</td><td>{p['version']}</td><td style='font-size:.75rem;color:#8b949e'>{p['registry']}</td><td>{hash_display}</td></tr>"
    content = f"""
    <div class="card">
      <div class="card-title">Internal Package Registry</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:.75rem">
        Packages sourced from the corporate PyPI mirror at pypi.corp.internal.
      </p>
      <table>
        <thead><tr><th>Package</th><th>Version</th><th>Registry</th><th>SHA256</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""
    return render(content)

@app.route("/install", methods=["GET", "POST"])
def install_pkg():
    result = ""
    pkg_input = ""
    if request.method == "POST":
        pkg_input = request.form.get("package", "").strip()
        if pkg_input == "corp-utils":
            result = f"""
            <div class="result-box result-flag">
              WARNING: Dependency confusion detected.<br><br>
              Package <strong>corp-utils</strong> was resolved from public PyPI (version 9.9.9)
              instead of the internal registry (version 1.0.0).<br><br>
              The public package executed code during installation via setup.py.<br><br>
              Incident token: <strong>{_flag('a03_deps')}</strong>
            </div>"""
        elif pkg_input:
            fake_hash = hashlib.sha256(pkg_input.encode()).hexdigest()
            result = f"""
            <div class="result-box">
              Collecting {pkg_input}<br>
              Downloading {pkg_input}-1.0.0.tar.gz<br>
              Building wheel for {pkg_input}...<br>
              Hash (computed): {fake_hash[:32]}...<br>
              Hash (expected): <span style="color:#f85149">not verified</span><br>
              Successfully installed {pkg_input}-1.0.0
            </div>"""
    content = f"""
    <div class="card">
      <div class="card-title">Package Installation</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:1rem">
        Simulates package retrieval and installation from configured registries.
      </p>
      <form method="POST">
        <div class="form-row">
          <label>Package name</label>
          <input name="package" value="{pkg_input}" placeholder="package-name" style="width:220px">
          <button type="submit">Install</button>
        </div>
      </form>
      {result}
    </div>"""
    return render(content)

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    from flask import jsonify
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
