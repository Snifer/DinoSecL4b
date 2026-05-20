import sqlite3
import subprocess
import os
from flask import Flask, request, render_template_string, session, redirect, jsonify
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "shopcorp-2024-internal"
app.config["FLAG_KEY"] = _flag('a05_ssti')

DB_PATH = "/tmp/shopcorp.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS products")
    c.execute("DROP TABLE IF EXISTS comments")
    c.execute("DROP TABLE IF EXISTS secrets")
    c.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, role TEXT
    )""")
    c.execute("""CREATE TABLE products (
        id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT, stock INTEGER, description TEXT
    )""")
    c.execute("""CREATE TABLE comments (
        id INTEGER PRIMARY KEY, author TEXT, content TEXT, product_id INTEGER
    )""")
    c.execute("""CREATE TABLE secrets (
        id INTEGER PRIMARY KEY, key TEXT, flag TEXT
    )""")
    c.executemany("INSERT INTO users VALUES (?,?,?,?,?)", [
        (1, "alice", "password123",  "alice@shopcorp.internal", "customer"),
        (2, "bob",   "qwerty",       "bob@shopcorp.internal",   "customer"),
        (3, "admin", "S3cr3t!2024",  "admin@shopcorp.internal", "admin"),
    ])
    c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?)", [
        (1, "ProBook Laptop 15",   1299.99, "Electronics", 24, "Intel i7, 16GB RAM, 512GB SSD"),
        (2, "Wireless Headset X1", 149.99,  "Electronics", 87, "Noise-cancelling, 30h battery"),
        (3, "Ergonomic Chair",     399.99,  "Office",      12, "Lumbar support, adjustable armrests"),
        (4, "Standing Desk Pro",   799.99,  "Office",       5, "Electric height adjustment, 160cm"),
        (5, "USB-C Hub 7-in-1",    59.99,   "Electronics", 145, "HDMI 4K, SD card, 3x USB-A"),
        (6, "Mechanical Keyboard", 89.99,   "Electronics",  62, "Tactile switches, RGB backlight"),
    ])
    c.executemany("INSERT INTO comments VALUES (?,?,?,?)", [
        (1, "alice",   "Great product, fast shipping!", 1),
        (2, "bob",     "Good value for money.",         2),
        (3, "charlie", "Highly recommended.",           1),
    ])
    c.execute("INSERT INTO secrets VALUES (1, 'internal_flag', ?)", (_flag('a05_sqli'),))
    conn.commit()
    conn.close()

init_db()

# Write RCE flag to /tmp
RCE_FLAG_PATH = "/tmp/flag_rce.txt"
with open(RCE_FLAG_PATH, "w") as _f:
    _f.write(_flag('a05_rce') + "\n")

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ShopCorp — Enterprise Marketplace</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Courier New', Courier, monospace; background: #0d1117; color: #e6edf3; min-height: 100vh; }
    header { background: #161b22; border-bottom: 1px solid #30363d; padding: .75rem 2rem; display: flex; align-items: center; justify-content: space-between; }
    .brand { font-size: 1.1rem; font-weight: bold; color: #58a6ff; }
    .brand span { color: #3fb950; }
    header nav a { color: #8b949e; text-decoration: none; margin-left: 1.5rem; font-size: .85rem; }
    header nav a:hover { color: #e6edf3; }
    main { max-width: 1060px; margin: 2rem auto; padding: 0 1.5rem; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1.25rem; margin-bottom: 1.25rem; }
    .card-title { font-size: .8rem; color: #8b949e; text-transform: uppercase; letter-spacing: .1em; margin-bottom: .75rem; border-bottom: 1px solid #21262d; padding-bottom: .5rem; }
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
    .product-card { background: #21262d; border: 1px solid #30363d; border-radius: 6px; padding: 1rem; }
    .product-name { font-size: .95rem; margin-bottom: .3rem; }
    .product-cat { font-size: .7rem; color: #8b949e; margin-bottom: .5rem; }
    .product-price { color: #3fb950; font-size: 1.1rem; }
    .product-stock { font-size: .72rem; color: #8b949e; }
    .product-desc { font-size: .78rem; color: #8b949e; margin-top: .4rem; }
    table { width: 100%; border-collapse: collapse; font-size: .85rem; }
    th { text-align: left; padding: .5rem .75rem; color: #8b949e; border-bottom: 1px solid #30363d; font-weight: normal; font-size: .75rem; text-transform: uppercase; }
    td { padding: .5rem .75rem; border-bottom: 1px solid #21262d; }
    input, textarea { background: #21262d; border: 1px solid #30363d; color: #e6edf3; padding: .4rem .75rem; border-radius: 4px; font-family: inherit; font-size: .875rem; }
    input:focus, textarea:focus { outline: none; border-color: #58a6ff; }
    button { background: #238636; border: 1px solid #2ea043; color: #fff; padding: .4rem 1rem; border-radius: 4px; font-family: inherit; font-size: .875rem; cursor: pointer; }
    button:hover { background: #2ea043; }
    .form-row { display: flex; align-items: center; gap: .75rem; margin-bottom: .75rem; }
    .form-row label { color: #8b949e; font-size: .8rem; min-width: 90px; }
    pre { background: #0d1117; padding: 1rem; border-radius: 4px; overflow: auto; font-size: .78rem; line-height: 1.5; max-height: 400px; border: 1px solid #21262d; }
    .comment-item { background: #0d1117; padding: .6rem .75rem; border-radius: 4px; margin-bottom: .5rem; border: 1px solid #21262d; font-size: .85rem; }
    .comment-author { color: #58a6ff; font-size: .75rem; margin-bottom: .25rem; }
    code { background: #21262d; padding: .1rem .3rem; border-radius: 3px; font-size: .8rem; }
    a { color: #58a6ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .stats-row { display: flex; gap: 1rem; }
    .stats-row .card { flex: 1; text-align: center; }
    .stat-value { font-size: 1.4rem; color: #58a6ff; }
    .stat-label { font-size: .7rem; color: #8b949e; text-transform: uppercase; margin-top: .2rem; }
    footer { text-align: center; font-size: .7rem; color: #484f58; margin: 3rem 0 1rem; }
  </style>
</head>
<body>
<header>
  <div class="brand">Shop<span>Corp</span></div>
  <nav>
    <a href="/">Catalog</a>
    <a href="/search">Search</a>
    <a href="/ping">Connectivity</a>
    <a href="/render">Promotions</a>
    <a href="/comments">Reviews</a>
  </nav>
</header>
<main>
{{ content | safe }}
</main>
<footer>ShopCorp Enterprise Marketplace v3.4.1 &mdash; &copy; 2024 ShopCorp Inc.</footer>
</body>
</html>"""

def render(content, **ctx):
    return render_template_string(BASE, content=content, **ctx)

@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, category, stock, description FROM products")
    products = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM products")
    total_products = cur.fetchone()[0]
    conn.close()

    cards = ""
    for p in products:
        cards += f"""
        <div class="product-card">
          <div class="product-name">{p[1]}</div>
          <div class="product-cat">{p[3]}</div>
          <div class="product-price">${p[2]:,.2f}</div>
          <div class="product-stock">{p[4]} in stock</div>
          <div class="product-desc">{p[5]}</div>
        </div>"""

    content = f"""
    <div class="stats-row">
      <div class="card"><div class="stat-value">{total_products}</div><div class="stat-label">Products</div></div>
      <div class="card"><div class="stat-value">3</div><div class="stat-label">Categories</div></div>
      <div class="card"><div class="stat-value">2-day</div><div class="stat-label">Delivery</div></div>
    </div>
    <div class="card">
      <div class="card-title">Product Catalog</div>
      <div class="product-grid">{cards}</div>
    </div>"""
    return render(content)

@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    query_str = ""
    error = ""
    if request.method == "POST":
        query_str = request.form.get("q", "")
        sql = f"SELECT id, name, price, category, stock FROM products WHERE name LIKE '%{query_str}%'"
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(sql)
            results = cur.fetchall()
            conn.close()
        except Exception as e:
            error = str(e)

    rows = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>${r[2]:,.2f}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
        for r in results
    )
    error_html = f"<div style='color:#f85149;font-size:.82rem;margin-top:.5rem'>Error: {error}</div>" if error else ""
    results_html = f"""
    <div class="card">
      <div class="card-title">Results ({len(results)} rows)</div>
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Price</th><th>Category</th><th>Stock</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>""" if results else ""

    content = f"""
    <div class="card">
      <div class="card-title">Product Search</div>
      <form method="POST">
        <div class="form-row">
          <label>Keyword</label>
          <input name="q" value="{query_str}" placeholder="Search products..." style="flex:1">
          <button type="submit">Search</button>
        </div>
      </form>
      {error_html}
    </div>
    {results_html}"""
    return render(content)

@app.route("/ping", methods=["GET", "POST"])
def ping():
    output = ""
    host_val = ""
    if request.method == "POST":
        host_val = request.form.get("host", "localhost")
        cmd = f"ping -c 2 {host_val}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = "Request timed out."
        except Exception as e:
            output = str(e)

    content = f"""
    <div class="card">
      <div class="card-title">Connectivity Check</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:1rem">
        Verify reachability to a supplier or warehouse endpoint.
      </p>
      <form method="POST">
        <div class="form-row">
          <label>Destination</label>
          <input name="host" value="{host_val}" placeholder="hostname or IP" style="flex:1">
          <button type="submit">Check</button>
        </div>
      </form>
    </div>
    {'<div class="card"><div class="card-title">Output</div><pre>' + output + '</pre></div>' if output else ''}"""
    return render(content)

@app.route("/render", methods=["GET", "POST"])
def render_tpl():
    output = ""
    tpl_input = ""
    if request.method == "POST":
        tpl_input = request.form.get("template", "")
        try:
            output = render_template_string(tpl_input)
        except Exception as e:
            output = f"Template error: {e}"

    content = f"""
    <div class="card">
      <div class="card-title">Promotional Banner Builder</div>
      <p style="font-size:.85rem;color:#8b949e;margin-bottom:1rem">
        Compose a custom promotional message to preview before publishing to the storefront.
      </p>
      <form method="POST">
        <div class="form-row" style="align-items:flex-start">
          <label style="margin-top:.3rem">Message</label>
          <textarea name="template" rows="4" style="flex:1">{tpl_input}</textarea>
        </div>
        <button type="submit">Preview</button>
      </form>
    </div>
    {'<div class="card"><div class="card-title">Preview</div><div style="font-size:.9rem;line-height:1.6">' + output + '</div></div>' if output else ''}"""
    return render_template_string(BASE, content=content)

# In-memory review store
_comments = [
    {"author": "alice",   "content": "Great product, fast shipping!"},
    {"author": "bob",     "content": "Good value for money."},
]

@app.route("/comments", methods=["GET", "POST"])
def comments():
    if request.method == "POST":
        author = request.form.get("author", "anonymous")
        content_text = request.form.get("content", "")
        _comments.append({"author": author, "content": content_text})

    comments_html = "".join(
        f"<div class='comment-item'><div class='comment-author'>{c['author']}</div>{c['content']}</div>"
        for c in _comments
    )

    content = f"""
    <div class="card">
      <div class="card-title">Product Reviews</div>
      <form method="POST">
        <div class="form-row"><label>Name</label><input name="author" style="width:200px"></div>
        <div class="form-row" style="align-items:flex-start">
          <label style="margin-top:.3rem">Review</label>
          <textarea name="content" rows="3" style="flex:1" placeholder="Write your review..."></textarea>
        </div>
        <button type="submit">Post Review</button>
      </form>
    </div>
    <div class="card">
      <div class="card-title">All Reviews ({len(_comments)})</div>
      {comments_html if comments_html else '<p style="color:#8b949e">No reviews yet.</p>'}
    </div>"""
    return render_template_string(BASE, content=content)

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    init_db()
    with open(RCE_FLAG_PATH, "w") as _f:
        _f.write(_flag('a05_rce') + "\n")
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
