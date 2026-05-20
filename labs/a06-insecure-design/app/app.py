import time
from flask import Flask, request, session, redirect, render_template_string, jsonify
import hmac as _hmac, hashlib as _hashlib, os as _os
_SECRET = _os.environ.get('FLAG_SECRET', 'dinoseclabs-default')
def _flag(vuln_id): return "FLAG{" + _hmac.new(_SECRET.encode(), vuln_id.encode(), _hashlib.sha256).hexdigest()[:20] + "}"

app = Flask(__name__)
app.secret_key = "biz-store-k8s-prod-2024"

PRODUCTS = {
    1: {"name": "Enterprise Server License",  "price": 1299.00, "stock": 5,  "sku": "ESL-001"},
    2: {"name": "Network Security Suite",      "price": 449.00,  "stock": 20, "sku": "NSS-002"},
    3: {"name": "Cloud Storage Pack (1TB)",    "price": 89.00,   "stock": 15, "sku": "CSP-003"},
    4: {"name": "Managed Firewall Service",    "price": 599.00,  "stock": 8,  "sku": "MFS-004"},
}

VALID_COUPONS = {
    "SAVE10":  10,
    "PROMO50": 50,
    "VIP100":  100,
}

orders = {
    1000: {"product": "Enterprise Server License", "qty": 1, "total": 1299.00, "user": "mgarcia",   "status": "delivered"},
    1001: {"product": "Network Security Suite",     "qty": 2, "total": 898.00,  "user": "jlopez",    "status": "processing"},
    1002: {"product": "Cloud Storage Pack (1TB)",   "qty": 5, "total": 445.00,  "user": "asmith",    "status": "shipped"},
    1003: {"product": "Managed Firewall Service",   "qty": 1, "total": 599.00,  "user": "rperez",    "status": "pending"},
}
order_counter = 1004

BASE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BizStore — B2B Technology Marketplace</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',Arial,sans-serif;background:#f4f6f9;color:#2c3e50;min-height:100vh}
    header{background:#1a2744;color:#fff;padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:60px;box-shadow:0 2px 8px rgba(0,0,0,.3)}
    header .logo{font-size:1.4rem;font-weight:700;letter-spacing:1px}
    header .logo span{color:#4fc3f7}
    nav{display:flex;gap:0;background:#243054;border-bottom:3px solid #4fc3f7}
    nav a{color:#cfd8dc;text-decoration:none;padding:.7rem 1.2rem;font-size:.88rem;transition:background .2s}
    nav a:hover,nav a.active{background:#1a2744;color:#fff}
    .container{max-width:1100px;margin:0 auto;padding:2rem 1.5rem}
    .page-title{font-size:1.5rem;font-weight:600;color:#1a2744;margin-bottom:1.5rem;border-bottom:2px solid #e0e7ef;padding-bottom:.5rem}
    .card{background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.1);padding:1.5rem;margin-bottom:1.5rem}
    .card h3{color:#1a2744;margin-bottom:1rem;font-size:1.1rem}
    .btn{display:inline-block;padding:.55rem 1.4rem;border-radius:5px;border:none;cursor:pointer;font-size:.9rem;font-weight:600;transition:background .2s}
    .btn-primary{background:#1a6fcf;color:#fff}.btn-primary:hover{background:#145ab5}
    .btn-success{background:#27ae60;color:#fff}.btn-success:hover{background:#219a52}
    .btn-outline{background:#fff;color:#1a2744;border:1px solid #b0bec5}.btn-outline:hover{background:#f0f4f8}
    input,select,textarea{border:1px solid #b0bec5;border-radius:5px;padding:.5rem .8rem;font-size:.9rem;width:100%;background:#fafbfc;color:#2c3e50}
    input:focus,select:focus{outline:none;border-color:#1a6fcf;box-shadow:0 0 0 2px rgba(26,111,207,.15)}
    .form-row{display:flex;gap:1rem;align-items:center;margin-bottom:.8rem;flex-wrap:wrap}
    .form-row label{min-width:130px;font-weight:500;color:#455a64;font-size:.88rem}
    .form-row input,.form-row select{flex:1;min-width:180px}
    .alert{padding:.75rem 1rem;border-radius:5px;margin:.8rem 0;font-size:.9rem}
    .alert-success{background:#e8f5e9;color:#1b5e20;border-left:4px solid #27ae60}
    .alert-info{background:#e3f2fd;color:#0d47a1;border-left:4px solid #1a6fcf}
    .alert-warning{background:#fff8e1;color:#f57f17;border-left:4px solid #f9a825}
    .alert-danger{background:#fce4ec;color:#b71c1c;border-left:4px solid #e53935}
    table{width:100%;border-collapse:collapse;font-size:.88rem}
    th{background:#1a2744;color:#fff;padding:.6rem .8rem;text-align:left}
    td{padding:.55rem .8rem;border-bottom:1px solid #e8edf2}
    tr:hover td{background:#f5f7fa}
    .badge{display:inline-block;padding:.2rem .6rem;border-radius:12px;font-size:.75rem;font-weight:600}
    .badge-green{background:#e8f5e9;color:#2e7d32}
    .badge-blue{background:#e3f2fd;color:#1565c0}
    .badge-orange{background:#fff3e0;color:#e65100}
    footer{background:#1a2744;color:#90a4ae;text-align:center;padding:1.2rem;font-size:.8rem;margin-top:3rem}
    .stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-bottom:1.5rem}
    .stat-card{background:#fff;border-radius:8px;padding:1.2rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.1);border-left:4px solid #1a6fcf}
    .stat-card .num{font-size:2rem;font-weight:700;color:#1a2744}
    .stat-card .lbl{color:#78909c;font-size:.82rem;margin-top:.2rem}
  </style>
</head>
<body>
<header>
  <div class="logo">Biz<span>Store</span></div>
  <div style="font-size:.85rem;color:#90caf9">B2B Technology Marketplace &mdash; Enterprise Portal</div>
</header>
<nav>
  <a href="/">Home</a>
  <a href="/shop">Products</a>
  <a href="/coupon">Promotions</a>
  <a href="/order/1000">My Orders</a>
  <a href="/cart">Cart</a>
  <a href="/support">Support</a>
</nav>
<div class="container">
CONTENT_PLACEHOLDER
</div>
<footer>BizStore &copy; 2024 &mdash; Enterprise B2B Technology Solutions &mdash; All rights reserved</footer>
</body>
</html>"""

def render(content):
    return BASE.replace("CONTENT_PLACEHOLDER", content)

@app.route("/")
def index():
    content = """
    <div class="page-title">Dashboard</div>
    <div class="stat-grid">
      <div class="stat-card"><div class="num">4</div><div class="lbl">Product Categories</div></div>
      <div class="stat-card" style="border-color:#27ae60"><div class="num">1,240</div><div class="lbl">Active Clients</div></div>
      <div class="stat-card" style="border-color:#f9a825"><div class="num">$98K</div><div class="lbl">Monthly Revenue</div></div>
      <div class="stat-card" style="border-color:#8e24aa"><div class="num">99.8%</div><div class="lbl">Uptime SLA</div></div>
    </div>
    <div class="card">
      <h3>Welcome to BizStore Enterprise</h3>
      <p style="color:#546e7a;line-height:1.7">Your one-stop B2B marketplace for enterprise technology solutions. Browse our catalog, apply promotional codes, and manage your orders from a single portal.</p>
      <div style="margin-top:1rem;display:flex;gap:.8rem;flex-wrap:wrap">
        <a href="/shop" class="btn btn-primary">Browse Products</a>
        <a href="/coupon" class="btn btn-outline">Apply Coupon</a>
        <a href="/order/1000" class="btn btn-outline">View Orders</a>
      </div>
    </div>
    <div class="card">
      <h3>Recent Announcements</h3>
      <ul style="color:#546e7a;line-height:2;padding-left:1.2rem">
        <li>New Enterprise Server License bundles available — up to 40% off for volume orders</li>
        <li>Managed Firewall Service now includes 24/7 SOC monitoring at no extra cost</li>
        <li>Q4 promotion codes active — check the Promotions section for details</li>
      </ul>
    </div>"""
    return render(content)

@app.route("/shop", methods=["GET", "POST"])
def shop():
    global order_counter
    msg = ""
    flag_section = ""
    if request.method == "POST":
        product_id = int(request.form.get("product_id", 1))
        try:
            quantity = int(request.form.get("quantity", "1"))
        except ValueError:
            quantity = 1
        product = PRODUCTS.get(product_id, PRODUCTS[1])
        total = product["price"] * quantity
        order_id = order_counter
        order_counter += 1
        orders[order_id] = {
            "product": product["name"],
            "qty": quantity,
            "total": total,
            "user": session.get("user", "guest"),
            "status": "processing"
        }
        if total < 0:
            flag_section = f"""
            <div class="alert alert-success" style="background:#e8f5e9;border-left:4px solid #27ae60;margin-top:1rem">
              <strong>Order #{order_id} confirmed.</strong> Total: <strong>${total:.2f}</strong><br>
              <small style="color:#388e3c">Account credit applied. Authorization code: <code>{_flag('a06_logic')}</code></small>
            </div>"""
        else:
            msg = f"""
            <div class="alert alert-success">
              Order <strong>#{order_id}</strong> placed successfully. Total: <strong>${total:.2f}</strong>
            </div>"""

    products_rows = ""
    product_options = ""
    for pid, p in PRODUCTS.items():
        products_rows += f"""<tr>
          <td><code>{p['sku']}</code></td>
          <td>{p['name']}</td>
          <td>${p['price']:,.2f}</td>
          <td>{p['stock']}</td>
          <td><span class="badge badge-green">Available</span></td>
        </tr>"""
        product_options += f"<option value='{pid}'>{p['name']} &mdash; ${p['price']:,.2f}</option>"

    content = f"""
    <div class="page-title">Product Catalog</div>
    <div class="card">
      <h3>Available Products</h3>
      <table>
        <tr><th>SKU</th><th>Product</th><th>Unit Price</th><th>Stock</th><th>Status</th></tr>
        {products_rows}
      </table>
    </div>
    <div class="card">
      <h3>Place an Order</h3>
      <form method="POST">
        <div class="form-row">
          <label>Product</label>
          <select name="product_id">{product_options}</select>
        </div>
        <div class="form-row">
          <label>Quantity</label>
          <input name="quantity" type="number" value="1" style="max-width:120px">
        </div>
        <button class="btn btn-primary" type="submit">Submit Order</button>
      </form>
      {msg}
      {flag_section}
    </div>"""
    return render(content)

@app.route("/coupon", methods=["GET", "POST"])
def coupon():
    result = ""
    if request.method == "POST":
        code = request.form.get("code", "").upper().strip()
        if code in VALID_COUPONS:
            discount = VALID_COUPONS[code]
            result = f"""<div class="alert alert-success">Coupon <strong>{code}</strong> applied successfully. Discount: <strong>${discount}</strong> off your next order.</div>"""
        else:
            result = f"""<div class="alert alert-danger">Coupon code <strong>{code}</strong> is not valid or has expired.</div>"""

    content = """
    <div class="page-title">Promotions & Discount Codes</div>
    <div class="card">
      <h3>Apply a Promotional Code</h3>
      <p style="color:#546e7a;margin-bottom:1rem">Enter your promotional or discount code below. Codes are case-insensitive and can be applied once per order.</p>
      <form method="POST">
        <div class="form-row">
          <label>Coupon Code</label>
          <input name="code" placeholder="Enter coupon code" style="max-width:280px">
        </div>
        <button class="btn btn-primary" type="submit">Apply Code</button>
      </form>
      RESULT_PLACEHOLDER
    </div>
    <div class="card">
      <h3>Active Promotions</h3>
      <p style="color:#546e7a">Contact your account manager or check your registered email for exclusive promotional codes.</p>
    </div>""".replace("RESULT_PLACEHOLDER", result)
    return render(content)

@app.route("/order/<int:order_id>")
def view_order(order_id):
    order = orders.get(order_id)
    if not order:
        content = """
        <div class="page-title">Order Details</div>
        <div class="card">
          <div class="alert alert-warning">Order not found. Please verify the order number.</div>
          <a href="/shop" class="btn btn-outline" style="margin-top:.5rem">Back to Shop</a>
        </div>"""
        return render(content)

    status_badge = {
        "delivered":  "<span class='badge badge-green'>Delivered</span>",
        "processing": "<span class='badge badge-blue'>Processing</span>",
        "shipped":    "<span class='badge badge-orange'>Shipped</span>",
        "pending":    "<span class='badge badge-orange'>Pending</span>",
    }.get(order.get("status", "pending"), "<span class='badge badge-blue'>Unknown</span>")

    content = f"""
    <div class="page-title">Order #{order_id}</div>
    <div class="card">
      <h3>Order Summary</h3>
      <table>
        <tr><th>Field</th><th>Value</th></tr>
        <tr><td>Order ID</td><td><strong>#{order_id}</strong></td></tr>
        <tr><td>Product</td><td>{order['product']}</td></tr>
        <tr><td>Quantity</td><td>{order['qty']}</td></tr>
        <tr><td>Total</td><td>${order['total']:,.2f}</td></tr>
        <tr><td>Account</td><td>{order['user']}</td></tr>
        <tr><td>Status</td><td>{status_badge}</td></tr>
      </table>
      <div style="margin-top:1rem;display:flex;gap:.8rem">
        <a href="/order/{order_id - 1}" class="btn btn-outline">Previous Order</a>
        <a href="/order/{order_id + 1}" class="btn btn-outline">Next Order</a>
      </div>
    </div>"""
    return render(content)

@app.route("/cart")
def cart():
    content = """
    <div class="page-title">Shopping Cart</div>
    <div class="card">
      <h3>Your Cart</h3>
      <div class="alert alert-info">Your cart is currently empty. <a href="/shop">Browse products</a> to add items.</div>
    </div>"""
    return render(content)

@app.route("/support")
def support():
    content = """
    <div class="page-title">Support Center</div>
    <div class="card">
      <h3>Contact Support</h3>
      <p style="color:#546e7a">For enterprise support, please contact your dedicated account manager or open a ticket at support@bizstore.example.com</p>
    </div>"""
    return render(content)

@app.route("/admin-x7k9q")
def hidden_admin():
    content = """
    <div class="page-title">Administration Panel</div>
    <div class="alert alert-info" style="margin-bottom:1.5rem">
      <strong>Authorization code:</strong> <code>""" + _flag('a06_obscur') + """</code>
    </div>
    <div class="stat-grid">
      <div class="stat-card"><div class="num">1,240</div><div class="lbl">Registered Clients</div></div>
      <div class="stat-card" style="border-color:#27ae60"><div class="num">$23,450</div><div class="lbl">Revenue Today</div></div>
      <div class="stat-card" style="border-color:#f9a825"><div class="num">87</div><div class="lbl">Orders Today</div></div>
      <div class="stat-card" style="border-color:#e53935"><div class="num">3</div><div class="lbl">Support Tickets</div></div>
    </div>
    <div class="card">
      <h3>System Status</h3>
      <table>
        <tr><th>Service</th><th>Status</th><th>Uptime</th></tr>
        <tr><td>Order Processing</td><td><span class="badge badge-green">Online</span></td><td>99.9%</td></tr>
        <tr><td>Payment Gateway</td><td><span class="badge badge-green">Online</span></td><td>99.7%</td></tr>
        <tr><td>Inventory Sync</td><td><span class="badge badge-orange">Degraded</span></td><td>97.2%</td></tr>
        <tr><td>Email Notifications</td><td><span class="badge badge-green">Online</span></td><td>100%</td></tr>
      </table>
    </div>
    <div class="card">
      <h3>User Management</h3>
      <table>
        <tr><th>Username</th><th>Role</th><th>Last Login</th><th>Status</th></tr>
        <tr><td>mgarcia</td><td>Client</td><td>2024-12-01 09:15</td><td><span class="badge badge-green">Active</span></td></tr>
        <tr><td>jlopez</td><td>Client</td><td>2024-12-01 08:42</td><td><span class="badge badge-green">Active</span></td></tr>
        <tr><td>asmith</td><td>Manager</td><td>2024-11-30 17:03</td><td><span class="badge badge-green">Active</span></td></tr>
        <tr><td>rperez</td><td>Client</td><td>2024-11-28 11:20</td><td><span class="badge badge-orange">Inactive</span></td></tr>
      </table>
    </div>"""
    return render(content)

@app.route("/reset-lab", methods=["POST"])
def reset_lab():
    """Reinicia el estado interno del lab (DB, archivos, sesiones) sin reconstruir la imagen."""
    global orders, order_counter
    orders = {
        1000: {"product": "Enterprise Server License", "qty": 1, "total": 1299.00, "user": "mgarcia",   "status": "delivered"},
        1001: {"product": "Network Security Suite",     "qty": 2, "total": 898.00,  "user": "jlopez",    "status": "processing"},
        1002: {"product": "Cloud Storage Pack (1TB)",   "qty": 5, "total": 445.00,  "user": "asmith",    "status": "shipped"},
        1003: {"product": "Managed Firewall Service",   "qty": 1, "total": 599.00,  "user": "rperez",    "status": "pending"},
    }
    order_counter = 1004
    return jsonify({"ok": True, "message": "Lab state reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
