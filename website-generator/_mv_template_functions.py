# ─────────────────────────────────────────────────────────────────────────────
# 3b. MULTI-VENDOR MARKETPLACE TEMPLATE HELPERS
# All _mv_* functions return complete Jinja2 template strings.
# ─────────────────────────────────────────────────────────────────────────────

def _readme_marketplace(site_name: str) -> str:
    return f"""{site_name} — Multi-Vendor Marketplace
{'=' * 50}

QUICK START
-----------
1. pip install -r requirements.txt
2. python app.py
3. Open http://localhost:5000

DEFAULT ADMIN
-------------
Email   : admin@marketplace.com
Password: admin123

ROLES
-----
admin    → /admin          (pre-seeded)
seller   → /seller/dashboard  (register at /signup)
customer → /             (register at /signup)

PAYMENT FLOW
------------
On checkout a PAY-XXXXXXXX reference is generated.
90% credited to seller earnings.
10% kept as platform commission.

UPLOADS
-------
Product images saved to static/uploads/
"""


def _mv_css() -> str:
    return """
/* ── Multi-vendor marketplace styles ─────────────────────────────────── */
:root{--mv-pink:#e91e63;--mv-orange:#ff5722;--mv-dark:#1a1a2e;--mv-card:#fff;--mv-border:#eee}
body{background:#f5f5f5}

/* Topbar */
.mv-topbar{background:var(--mv-dark);color:#ccc;font-size:.78rem;padding:.3rem 1.5rem;display:flex;justify-content:space-between}
.mv-topbar a{color:#ccc;margin-left:1rem}
.mv-topbar a:hover{color:#fff}

/* Navbar */
.mv-nav{background:var(--mv-pink);padding:.6rem 1.5rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.2)}
.mv-nav .brand{font-size:1.5rem;font-weight:800;color:#fff;letter-spacing:-1px}
.mv-search{flex:1;min-width:200px;max-width:500px;display:flex}
.mv-search input{flex:1;padding:.5rem 1rem;border:none;border-radius:24px 0 0 24px;font-size:.9rem;outline:none}
.mv-search button{padding:.5rem 1rem;background:#ff5722;color:#fff;border:none;border-radius:0 24px 24px 0;cursor:pointer}
.mv-nav-links{display:flex;align-items:center;gap:.5rem;margin-left:auto}
.mv-nav-links a{color:rgba(255,255,255,.9);font-size:.88rem;padding:.3rem .7rem;border-radius:20px;transition:background .2s}
.mv-nav-links a:hover,.mv-nav-links a.active{background:rgba(255,255,255,.2);color:#fff}
.mv-nav-links .btn-signup{background:#fff;color:var(--mv-pink);font-weight:700;padding:.35rem .9rem;border-radius:20px}
.cart-badge{background:#ff5722;color:#fff;border-radius:50%;font-size:.65rem;padding:.1rem .35rem;margin-left:.2rem;font-weight:700}

/* Hero banner */
.mv-hero{background:linear-gradient(135deg,var(--mv-pink),var(--mv-orange));color:#fff;padding:3rem 1.5rem;text-align:center}
.mv-hero h1{font-size:2.2rem;font-weight:800;margin-bottom:.5rem}
.mv-hero p{opacity:.9;margin-bottom:1.5rem}
.mv-hero .btn-hero{background:#fff;color:var(--mv-pink);padding:.7rem 2rem;border-radius:30px;font-weight:700;font-size:1rem;display:inline-block}

/* Category pills */
.mv-cats{display:flex;gap:.5rem;flex-wrap:wrap;padding:1rem 1.5rem;background:#fff;border-bottom:1px solid var(--mv-border)}
.mv-cats a{padding:.3rem .9rem;border-radius:20px;font-size:.82rem;border:1px solid var(--mv-border);color:#555;transition:all .2s}
.mv-cats a:hover,.mv-cats a.active{background:var(--mv-pink);color:#fff;border-color:var(--mv-pink)}

/* Product grid */
.mv-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:1rem;padding:1.5rem}
.mv-card{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06);transition:transform .2s,box-shadow .2s;cursor:pointer}
.mv-card:hover{transform:translateY(-4px);box-shadow:0 8px 20px rgba(0,0,0,.12)}
.mv-card img{width:100%;height:180px;object-fit:cover}
.mv-card-body{padding:.75rem}
.mv-card-name{font-size:.88rem;font-weight:600;margin-bottom:.3rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.mv-card-price{color:var(--mv-pink);font-weight:800;font-size:1rem}
.mv-card-seller{font-size:.72rem;color:#888;margin-top:.2rem}
.mv-card-btn{width:100%;margin-top:.5rem;padding:.4rem;background:var(--mv-pink);color:#fff;border:none;border-radius:8px;font-size:.82rem;cursor:pointer;font-weight:600}
.mv-card-btn:hover{background:#c2185b}

/* Sidebar filter */
.mv-layout{display:grid;grid-template-columns:220px 1fr;gap:1.5rem;padding:1.5rem;max-width:1400px;margin:0 auto}
.mv-sidebar{background:#fff;border-radius:12px;padding:1.25rem;height:fit-content;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.mv-sidebar h4{font-size:.85rem;text-transform:uppercase;letter-spacing:.06em;color:#888;margin-bottom:.75rem;margin-top:1rem}
.mv-sidebar h4:first-child{margin-top:0}
.mv-sidebar label{display:flex;align-items:center;gap:.5rem;font-size:.88rem;margin-bottom:.4rem;cursor:pointer}
.mv-sidebar input[type=range]{width:100%}
.mv-price-inputs{display:flex;gap:.5rem}
.mv-price-inputs input{width:100%;padding:.35rem .5rem;border:1px solid var(--mv-border);border-radius:6px;font-size:.82rem}
.mv-filter-btn{width:100%;margin-top:.75rem;padding:.5rem;background:var(--mv-pink);color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600}

/* Dashboard */
.mv-dash{max-width:1200px;margin:0 auto;padding:1.5rem}
.mv-dash-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;flex-wrap:wrap;gap:.75rem}
.mv-dash-header h2{font-size:1.5rem;font-weight:800}
.mv-stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin-bottom:1.5rem}
.mv-stat{background:#fff;border-radius:12px;padding:1.25rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.mv-stat-val{font-size:1.8rem;font-weight:800;color:var(--mv-pink)}
.mv-stat-label{font-size:.78rem;color:#888;margin-top:.25rem}

/* Tables */
.mv-table-wrap{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.mv-table-head{display:flex;justify-content:space-between;align-items:center;padding:1rem 1.25rem;border-bottom:1px solid var(--mv-border)}
.mv-table-head h3{font-size:1rem;font-weight:700}
table.mv-table{width:100%;border-collapse:collapse}
table.mv-table th{background:#fafafa;padding:.75rem 1rem;text-align:left;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:#888;border-bottom:1px solid var(--mv-border)}
table.mv-table td{padding:.75rem 1rem;border-bottom:1px solid var(--mv-border);font-size:.88rem;vertical-align:middle}
table.mv-table tr:last-child td{border-bottom:none}
table.mv-table tr:hover td{background:#fafafa}

/* Badges */
.badge{padding:.25rem .65rem;border-radius:20px;font-size:.72rem;font-weight:700;display:inline-block}
.badge-paid{background:#e8f5e9;color:#2e7d32}
.badge-pending{background:#fff3e0;color:#e65100}
.badge-confirmed{background:#e3f2fd;color:#1565c0}
.badge-shipped{background:#f3e5f5;color:#6a1b9a}
.badge-delivered{background:#e8f5e9;color:#1b5e20}
.badge-cancelled{background:#ffebee;color:#b71c1c}

/* Forms */
.mv-form-card{background:#fff;border-radius:16px;padding:2rem;max-width:600px;margin:2rem auto;box-shadow:0 4px 20px rgba(0,0,0,.08)}
.mv-form-card h2{margin-bottom:1.5rem;font-size:1.4rem;font-weight:800}
.mv-form-group{margin-bottom:1.1rem}
.mv-form-group label{display:block;font-size:.85rem;font-weight:600;margin-bottom:.4rem;color:#444}
.mv-form-group input,.mv-form-group textarea,.mv-form-group select{width:100%;padding:.7rem 1rem;border:1.5px solid var(--mv-border);border-radius:8px;font-size:.95rem;font-family:inherit;transition:border-color .2s;outline:none}
.mv-form-group input:focus,.mv-form-group textarea:focus,.mv-form-group select:focus{border-color:var(--mv-pink)}
.mv-form-group textarea{resize:vertical;min-height:100px}
.mv-btn{padding:.7rem 1.75rem;border-radius:8px;border:none;font-size:.95rem;font-weight:700;cursor:pointer;transition:opacity .2s}
.mv-btn-primary{background:var(--mv-pink);color:#fff}
.mv-btn-primary:hover{opacity:.88}
.mv-btn-outline{background:transparent;border:2px solid var(--mv-pink);color:var(--mv-pink)}
.mv-btn-danger{background:#e53935;color:#fff}
.mv-btn-sm{padding:.35rem .9rem;font-size:.8rem}

/* Cart */
.mv-cart{max-width:1000px;margin:2rem auto;padding:0 1.5rem}
.mv-cart-item{background:#fff;border-radius:12px;padding:1rem;display:flex;align-items:center;gap:1rem;margin-bottom:.75rem;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.mv-cart-item img{width:72px;height:72px;object-fit:cover;border-radius:8px;flex-shrink:0}
.mv-cart-item-info{flex:1}
.mv-cart-item-name{font-weight:700;margin-bottom:.2rem}
.mv-cart-item-price{color:var(--mv-pink);font-weight:800}
.mv-cart-summary{background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06);margin-top:1rem}
.mv-cart-total{display:flex;justify-content:space-between;font-size:1.2rem;font-weight:800;margin-bottom:1rem}

/* Order tracker */
.mv-tracker{display:flex;align-items:center;justify-content:center;gap:0;margin:1.5rem 0;flex-wrap:wrap}
.mv-tracker-step{display:flex;flex-direction:column;align-items:center;gap:.3rem}
.mv-tracker-dot{width:36px;height:36px;border-radius:50%;background:#eee;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700;color:#aaa}
.mv-tracker-dot.done{background:var(--mv-pink);color:#fff}
.mv-tracker-label{font-size:.7rem;color:#888}
.mv-tracker-line{flex:1;height:3px;background:#eee;min-width:30px}
.mv-tracker-line.done{background:var(--mv-pink)}

/* Auth */
.mv-auth{min-height:80vh;display:flex;align-items:center;justify-content:center;padding:2rem}
.mv-auth-card{background:#fff;padding:2.5rem;border-radius:20px;box-shadow:0 8px 32px rgba(0,0,0,.1);width:100%;max-width:440px}
.mv-auth-card h2{text-align:center;margin-bottom:.5rem;font-size:1.6rem;font-weight:800}
.mv-auth-card .subtitle{text-align:center;color:#888;margin-bottom:1.75rem;font-size:.9rem}
.mv-auth-switch{text-align:center;margin-top:1.25rem;font-size:.88rem;color:#666}
.mv-auth-switch a{color:var(--mv-pink);font-weight:700}

/* Flash */
.mv-flash{padding:.75rem 1.5rem;text-align:center;font-weight:500;font-size:.9rem;border-radius:8px;margin:.5rem 1.5rem}
.mv-flash-success{background:#e8f5e9;color:#2e7d32}
.mv-flash-error{background:#ffebee;color:#c62828}
.mv-flash-warning{background:#fff3e0;color:#e65100}
.mv-flash-info{background:#e3f2fd;color:#1565c0}

/* Earnings */
.mv-earn-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:1.5rem}
.mv-earn-card{background:#fff;border-radius:12px;padding:1.5rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06);border-top:4px solid var(--mv-pink)}
.mv-earn-val{font-size:2rem;font-weight:800;color:var(--mv-pink)}
.mv-earn-label{font-size:.82rem;color:#888;margin-top:.3rem}

/* Responsive */
@media(max-width:768px){
  .mv-layout{grid-template-columns:1fr}
  .mv-sidebar{display:none}
  .mv-grid{grid-template-columns:repeat(2,1fr);padding:1rem}
  .mv-nav{gap:.5rem}
  .mv-search{min-width:0;flex:1}
}
"""


def _mv_base_html(site_name: str, font: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{% block title %}}{site_name}{{% endblock %}}</title>
  <link href="https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@300;400;600;700;800&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}"/>
</head>
<body>
<div class="mv-topbar">
  <span>🛍️ {site_name} — Shop from thousands of sellers</span>
  <span>
    {{%- if session.user_id %}}
      Hi, {{{{ session.user_name }}}} &nbsp;|&nbsp;
      <a href="{{{{ url_for('logout') }}}}">Logout</a>
    {{%- else %}}
      <a href="{{{{ url_for('login') }}}}">Login</a> &nbsp;|&nbsp;
      <a href="{{{{ url_for('signup') }}}}">Sign Up</a>
    {{%- endif %}}
  </span>
</div>
<nav class="mv-nav">
  <a href="{{{{ url_for('index') }}}}" class="brand">🛍️ {site_name}</a>
  {{%- if session.role == 'customer' or not session.role %}}
  <form class="mv-search" action="{{{{ url_for('index') }}}}" method="get">
    <input type="search" name="q" placeholder="Search products, brands…" value="{{{{ request.args.get('q','') }}}}"/>
    <button type="submit">🔍</button>
  </form>
  {{%- endif %}}
  <div class="mv-nav-links">
    {{%- if not session.user_id %}}
      <a href="{{{{ url_for('index') }}}}">Shop</a>
      <a href="{{{{ url_for('login') }}}}">Login</a>
      <a href="{{{{ url_for('signup') }}}}" class="btn-signup">Sign Up</a>
    {{%- elif session.role == 'admin' %}}
      <a href="{{{{ url_for('admin_dashboard') }}}}" {{%- if request.endpoint=='admin_dashboard' %}}class="active"{{%- endif %}}>Dashboard</a>
      <a href="{{{{ url_for('admin_users') }}}}" {{%- if request.endpoint=='admin_users' %}}class="active"{{%- endif %}}>Users</a>
      <a href="{{{{ url_for('admin_products') }}}}" {{%- if request.endpoint=='admin_products' %}}class="active"{{%- endif %}}>Products</a>
      <a href="{{{{ url_for('admin_orders') }}}}" {{%- if request.endpoint=='admin_orders' %}}class="active"{{%- endif %}}>Orders</a>
      <a href="{{{{ url_for('admin_earnings') }}}}" {{%- if request.endpoint=='admin_earnings' %}}class="active"{{%- endif %}}>Earnings</a>
    {{%- elif session.role == 'seller' %}}
      <a href="{{{{ url_for('seller_dashboard') }}}}" {{%- if request.endpoint=='seller_dashboard' %}}class="active"{{%- endif %}}>Dashboard</a>
      <a href="{{{{ url_for('seller_add_product') }}}}" {{%- if request.endpoint=='seller_add_product' %}}class="active"{{%- endif %}}>+ Product</a>
      <a href="{{{{ url_for('seller_orders') }}}}" {{%- if request.endpoint=='seller_orders' %}}class="active"{{%- endif %}}>Orders</a>
      <a href="{{{{ url_for('seller_earnings') }}}}" {{%- if request.endpoint=='seller_earnings' %}}class="active"{{%- endif %}}>Earnings</a>
    {{%- else %}}
      <a href="{{{{ url_for('index') }}}}">Shop</a>
      <a href="{{{{ url_for('cart') }}}}">🛒 Cart<span class="cart-badge">{{{{ session.get('cart_count',0) }}}}</span></a>
      <a href="{{{{ url_for('my_orders') }}}}">Orders</a>
    {{%- endif %}}
  </div>
</nav>
{{%- with messages = get_flashed_messages(with_categories=true) %}}
  {{%- for cat, msg in messages %}}
    <div class="mv-flash mv-flash-{{{{ cat }}}}">{{{{ msg }}}}</div>
  {{%- endfor %}}
{{%- endwith %}}
{{%- block content %}}{{%- endblock %}}
<footer style="background:#1a1a2e;color:#aaa;text-align:center;padding:2rem 1rem;margin-top:3rem">
  <p style="font-size:1.1rem;font-weight:800;color:#fff;margin-bottom:.3rem">🛍️ {site_name}</p>
  <p style="font-size:.82rem">&copy; 2025 {site_name}. Multi-Vendor Marketplace.</p>
</footer>
<script src="{{{{ url_for('static', filename='js/script.js') }}}}"></script>
{{%- block scripts %}}{{%- endblock %}}
</body>
</html>"""


def _mv_login_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Login{%- endblock %}
{%- block content %}
<div class="mv-auth">
  <div class="mv-auth-card">
    <h2>Welcome Back</h2>
    <p class="subtitle">Login to your account</p>
    <form method="POST" action="{{ url_for('login') }}">
      <div class="mv-form-group">
        <label>Email Address</label>
        <input type="email" name="email" placeholder="you@example.com" required autofocus/>
      </div>
      <div class="mv-form-group">
        <label>Password</label>
        <input type="password" name="password" placeholder="••••••••" required/>
      </div>
      <button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Login</button>
    </form>
    <p class="mv-auth-switch">No account? <a href="{{ url_for('signup') }}">Sign up free</a></p>
  </div>
</div>
{%- endblock %}"""


def _mv_signup_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Create Account{%- endblock %}
{%- block content %}
<div class="mv-auth">
  <div class="mv-auth-card">
    <h2>Create Account</h2>
    <p class="subtitle">Join as a seller or customer</p>
    <form method="POST" action="{{ url_for('signup') }}" id="signupForm">
      <div class="mv-form-group">
        <label>Full Name</label>
        <input type="text" name="name" placeholder="Your name" required autofocus/>
      </div>
      <div class="mv-form-group">
        <label>Email Address</label>
        <input type="email" name="email" placeholder="you@example.com" required/>
      </div>
      <div class="mv-form-group">
        <label>Password</label>
        <input type="password" name="password" placeholder="Min 6 characters" required minlength="6"/>
      </div>
      <div class="mv-form-group">
        <label>I want to</label>
        <select name="role" id="roleSelect" onchange="toggleShop(this.value)">
          <option value="customer">Shop (Customer)</option>
          <option value="seller">Sell Products (Seller)</option>
        </select>
      </div>
      <div class="mv-form-group" id="shopNameField" style="display:none">
        <label>Your Shop Name <span style="color:red">*</span></label>
        <input type="text" name="shop_name" id="shopNameInput" placeholder="e.g. Priya's Boutique" maxlength="120"/>
        <div style="font-size:.78rem;color:#888;margin-top:.3rem">
          Store URL: <code>/store/<span id="slugPreview">your-shop</span></code>
        </div>
      </div>
      <button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Create Account</button>
    </form>
    <p class="mv-auth-switch">Already have an account? <a href="{{ url_for('login') }}">Login</a></p>
  </div>
</div>
{%- endblock %}
{%- block scripts %}
<script>
function toggleShop(role) {
  var f = document.getElementById('shopNameField');
  var i = document.getElementById('shopNameInput');
  f.style.display = role === 'seller' ? 'block' : 'none';
  i.required = role === 'seller';
}
document.getElementById('shopNameInput').addEventListener('input', function() {
  var slug = this.value.toLowerCase().trim()
    .replace(/[^\\w\\s-]/g,'').replace(/[\\s_-]+/g,'-') || 'your-shop';
  document.getElementById('slugPreview').textContent = slug;
});
</script>
{%- endblock %}"""


def _mv_403_html(site_name: str) -> str:
    return f"""{{% extends 'base.html' %}}
{{% block title %}}403 Forbidden{{% endblock %}}
{{% block content %}}
<div style="text-align:center;padding:5rem 1rem">
  <div style="font-size:5rem">🚫</div>
  <h1 style="font-size:2rem;margin:.5rem 0">Access Denied</h1>
  <p style="color:#888">You don't have permission to view this page.</p>
  <a href="{{{{ url_for('index') }}}}" class="mv-btn mv-btn-primary" style="display:inline-block;margin-top:1.5rem">Go Home</a>
</div>
{{% endblock %}}"""


def _mv_404_html(site_name: str) -> str:
    return f"""{{% extends 'base.html' %}}
{{% block title %}}404 Not Found{{% endblock %}}
{{% block content %}}
<div style="text-align:center;padding:5rem 1rem">
  <div style="font-size:5rem">🔍</div>
  <h1 style="font-size:2rem;margin:.5rem 0">Page Not Found</h1>
  <p style="color:#888">The page you're looking for doesn't exist.</p>
  <a href="{{{{ url_for('index') }}}}" class="mv-btn mv-btn-primary" style="display:inline-block;margin-top:1.5rem">Go Home</a>
</div>
{{% endblock %}}"""


def _mv_storefront_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Shop — {{ request.host }}{%- endblock %}
{%- block content %}
<div class="mv-hero">
  <h1>Shop the Best Deals</h1>
  <p>Millions of products from verified sellers. Free delivery on orders above ₹499.</p>
  <a href="#products" class="btn-hero">Browse Now</a>
</div>

<div class="mv-cats">
  <a href="{{ url_for('index') }}" class="{{ 'active' if not selected_cat else '' }}">All</a>
  {%- for cat in categories %}
  <a href="{{ url_for('index', category=cat, q=q) }}"
     class="{{ 'active' if selected_cat==cat else '' }}">{{ cat }}</a>
  {%- endfor %}
</div>

<div class="mv-layout" id="products">
  <!-- Sidebar filters -->
  <aside class="mv-sidebar">
    <form method="get" action="{{ url_for('index') }}">
      {%- if q %}<input type="hidden" name="q" value="{{ q }}"/>{%- endif %}
      {%- if selected_cat %}<input type="hidden" name="category" value="{{ selected_cat }}"/>{%- endif %}
      <h4>Sort By</h4>
      <label><input type="radio" name="sort" value="newest" {{ 'checked' if sort=='newest' else '' }} onchange="this.form.submit()"/> Newest</label>
      <label><input type="radio" name="sort" value="price_asc" {{ 'checked' if sort=='price_asc' else '' }} onchange="this.form.submit()"/> Price: Low → High</label>
      <label><input type="radio" name="sort" value="price_desc" {{ 'checked' if sort=='price_desc' else '' }} onchange="this.form.submit()"/> Price: High → Low</label>
      <h4>Price Range</h4>
      <div class="mv-price-inputs">
        <input type="number" name="min_price" placeholder="Min" value="{{ min_price }}"/>
        <input type="number" name="max_price" placeholder="Max" value="{{ max_price }}"/>
      </div>
      <button type="submit" class="mv-filter-btn">Apply Filters</button>
    </form>
  </aside>

  <!-- Product grid -->
  <div>
    <p style="color:#888;font-size:.85rem;margin-bottom:.75rem">
      <strong>{{ products|length }}</strong> products
      {%- if q %} for "<strong>{{ q }}</strong>"{%- endif %}
      {%- if selected_cat %} in <strong>{{ selected_cat }}</strong>{%- endif %}
    </p>
    {%- if products %}
    <div class="mv-grid">
      {%- for p in products %}
      <div class="mv-card" onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
        <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
             alt="{{ p.name }}"
             onerror="this.src='https://placehold.co/300x300/fce4ec/e91e63?text=No+Image'"/>
        <div class="mv-card-body">
          <div class="mv-card-name">{{ p.name }}</div>
          <div class="mv-card-price">₹{{ '%.0f'|format(p.price) }}</div>
          <div class="mv-card-seller">by {{ p.seller_name }}</div>
          {%- if session.role == 'customer' or not session.role %}
          <form method="POST" action="{{ url_for('add_to_cart', pid=p.id) }}" onclick="event.stopPropagation()">
            <input type="hidden" name="quantity" value="1"/>
            <button type="submit" class="mv-card-btn">Add to Cart</button>
          </form>
          {%- endif %}
        </div>
      </div>
      {%- endfor %}
    </div>
    {%- else %}
    <div style="text-align:center;padding:4rem 1rem">
      <div style="font-size:4rem">🔍</div>
      <h3 style="margin:.75rem 0;color:#555">No products found</h3>
      <a href="{{ url_for('index') }}" class="mv-btn mv-btn-primary">Browse All</a>
    </div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""


def _mv_product_detail_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}{{ product.name }}{%- endblock %}
{%- block content %}
<div style="max-width:1100px;margin:2rem auto;padding:0 1.5rem">
  <p style="color:#888;font-size:.85rem;margin-bottom:1rem">
    <a href="{{ url_for('index') }}">Home</a> /
    <a href="{{ url_for('index', category=product.category) }}">{{ product.category }}</a> /
    {{ product.name }}
  </p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:2.5rem;background:#fff;border-radius:16px;padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,.08)">
    <div>
      <img src="{{ url_for('static', filename='uploads/' + (product.image or 'default.png')) }}"
           alt="{{ product.name }}"
           style="width:100%;border-radius:12px;max-height:420px;object-fit:cover"
           onerror="this.src='https://placehold.co/500x500/fce4ec/e91e63?text=No+Image'"/>
    </div>
    <div>
      <span style="background:#fce4ec;color:#e91e63;padding:.2rem .7rem;border-radius:20px;font-size:.78rem;font-weight:700">{{ product.category }}</span>
      <h1 style="font-size:1.6rem;font-weight:800;margin:.75rem 0 .5rem">{{ product.name }}</h1>
      <div style="font-size:2rem;font-weight:800;color:#e91e63;margin-bottom:.75rem">₹{{ '%.0f'|format(product.price) }}</div>
      {%- if product.stock > 5 %}
        <span style="background:#e8f5e9;color:#2e7d32;padding:.25rem .7rem;border-radius:20px;font-size:.8rem;font-weight:700">✓ In Stock ({{ product.stock }})</span>
      {%- elif product.stock > 0 %}
        <span style="background:#fff3e0;color:#e65100;padding:.25rem .7rem;border-radius:20px;font-size:.8rem;font-weight:700">⚠ Only {{ product.stock }} left</span>
      {%- else %}
        <span style="background:#ffebee;color:#c62828;padding:.25rem .7rem;border-radius:20px;font-size:.8rem;font-weight:700">✗ Out of Stock</span>
      {%- endif %}
      <p style="color:#666;margin:1rem 0;line-height:1.7">{{ product.description or 'No description provided.' }}</p>
      <p style="font-size:.85rem;color:#888;margin-bottom:1.25rem">Sold by: <strong>{{ product.seller_name }}</strong></p>
      {%- if product.stock > 0 and (session.role == 'customer' or not session.role) %}
      <form method="POST" action="{{ url_for('add_to_cart', pid=product.id) }}" style="display:flex;gap:.75rem;align-items:center">
        <input type="number" name="quantity" value="1" min="1" max="{{ product.stock }}"
               style="width:80px;padding:.6rem;border:1.5px solid #eee;border-radius:8px;font-size:1rem"/>
        <button type="submit" class="mv-btn mv-btn-primary">🛒 Add to Cart</button>
      </form>
      {%- elif not session.user_id %}
      <a href="{{ url_for('login') }}" class="mv-btn mv-btn-primary">Login to Buy</a>
      {%- endif %}
    </div>
  </div>
  {%- if related %}
  <h3 style="margin:2rem 0 1rem;font-size:1.2rem;font-weight:800">You may also like</h3>
  <div class="mv-grid" style="grid-template-columns:repeat(auto-fill,minmax(160px,1fr))">
    {%- for p in related %}
    <div class="mv-card" onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
      <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
           alt="{{ p.name }}"
           onerror="this.src='https://placehold.co/300x300/fce4ec/e91e63?text=?'"/>
      <div class="mv-card-body">
        <div class="mv-card-name">{{ p.name }}</div>
        <div class="mv-card-price">₹{{ '%.0f'|format(p.price) }}</div>
      </div>
    </div>
    {%- endfor %}
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_cart_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}My Cart{%- endblock %}
{%- block content %}
<div class="mv-cart">
  <h2 style="font-size:1.5rem;font-weight:800;margin-bottom:1.25rem">🛒 My Cart</h2>
  {%- if items %}
  <div style="display:grid;grid-template-columns:1fr 320px;gap:1.5rem;align-items:start">
    <div>
      {%- for item in items %}
      <div class="mv-cart-item">
        <img src="{{ url_for('static', filename='uploads/' + (item.image or 'default.png')) }}"
             alt="{{ item.name }}"
             onerror="this.src='https://placehold.co/72x72/fce4ec/e91e63?text=?'"/>
        <div class="mv-cart-item-info">
          <div class="mv-cart-item-name">{{ item.name }}</div>
          <div class="mv-cart-item-price">₹{{ '%.0f'|format(item.price) }} each</div>
        </div>
        <form method="POST" action="{{ url_for('update_cart', iid=item.id) }}" style="display:flex;align-items:center;gap:.5rem">
          <button type="submit" name="quantity" value="{{ item.quantity - 1 }}"
                  style="width:28px;height:28px;border:1px solid #ddd;border-radius:6px;background:#fff;cursor:pointer;font-size:1rem">−</button>
          <span style="font-weight:700;min-width:24px;text-align:center">{{ item.quantity }}</span>
          <button type="submit" name="quantity" value="{{ item.quantity + 1 }}"
                  style="width:28px;height:28px;border:1px solid #ddd;border-radius:6px;background:#fff;cursor:pointer;font-size:1rem"
                  {{ 'disabled' if item.quantity >= item.stock else '' }}>+</button>
        </form>
        <div style="font-weight:800;color:#e91e63;min-width:70px;text-align:right">₹{{ '%.0f'|format(item.price * item.quantity) }}</div>
        <form method="POST" action="{{ url_for('remove_from_cart', iid=item.id) }}">
          <button type="submit" style="background:none;border:none;color:#e53935;cursor:pointer;font-size:1.1rem" title="Remove">🗑</button>
        </form>
      </div>
      {%- endfor %}
    </div>
    <div class="mv-cart-summary">
      <h3 style="font-size:1.1rem;font-weight:800;margin-bottom:1rem">Order Summary</h3>
      {%- for item in items %}
      <div style="display:flex;justify-content:space-between;font-size:.85rem;color:#666;margin-bottom:.4rem">
        <span>{{ item.name }} × {{ item.quantity }}</span>
        <span>₹{{ '%.0f'|format(item.price * item.quantity) }}</span>
      </div>
      {%- endfor %}
      <hr style="margin:.75rem 0;border:none;border-top:1px solid #eee"/>
      <div class="mv-cart-total">
        <span>Total</span>
        <span style="color:#e91e63">₹{{ '%.0f'|format(total) }}</span>
      </div>
      <a href="{{ url_for('checkout') }}" class="mv-btn mv-btn-primary" style="display:block;text-align:center;width:100%">Proceed to Checkout →</a>
      <a href="{{ url_for('index') }}" style="display:block;text-align:center;margin-top:.75rem;font-size:.85rem;color:#888">Continue Shopping</a>
    </div>
  </div>
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">🛒</div>
    <h3 style="margin:.75rem 0;color:#555">Your cart is empty</h3>
    <a href="{{ url_for('index') }}" class="mv-btn mv-btn-primary">Start Shopping</a>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_checkout_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Checkout{%- endblock %}
{%- block content %}
<div style="max-width:900px;margin:2rem auto;padding:0 1.5rem">
  <h2 style="font-size:1.5rem;font-weight:800;margin-bottom:1.5rem">💳 Checkout</h2>
  <div style="display:grid;grid-template-columns:1fr 320px;gap:1.5rem;align-items:start">
    <div>
      <div style="background:#fff;border-radius:16px;padding:1.75rem;box-shadow:0 4px 20px rgba(0,0,0,.08);margin-bottom:1rem">
        <h3 style="font-size:1rem;font-weight:800;margin-bottom:1rem">📍 Delivery Address</h3>
        <form method="POST" action="{{ url_for('checkout') }}" id="checkoutForm">
          <div class="mv-form-group">
            <label>Full Delivery Address *</label>
            <textarea name="address" rows="3" placeholder="House no, Street, City, State, PIN" required></textarea>
          </div>
          <h3 style="font-size:1rem;font-weight:800;margin:1.25rem 0 1rem">💳 Payment</h3>
          <div style="background:#f5f5f5;border-radius:10px;padding:1rem;margin-bottom:1rem">
            <p style="font-size:.85rem;color:#666;margin:0">
              🔒 <strong>Secure Demo Payment</strong> — A PAY-XXXXXXXX reference will be generated.
              No real charges. 90% goes to seller, 10% platform commission.
            </p>
          </div>
          <div class="mv-form-group">
            <label>Card Number (demo)</label>
            <input type="text" placeholder="4242 4242 4242 4242" disabled style="background:#f9f9f9"/>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem">
            <div class="mv-form-group"><label>Expiry</label><input type="text" placeholder="MM/YY" disabled style="background:#f9f9f9"/></div>
            <div class="mv-form-group"><label>CVV</label><input type="text" placeholder="•••" disabled style="background:#f9f9f9"/></div>
          </div>
          <button type="submit" class="mv-btn mv-btn-primary" style="width:100%;padding:.85rem;font-size:1rem">
            🔒 Place Order — ₹{{ '%.0f'|format(total) }}
          </button>
        </form>
      </div>
    </div>
    <div style="background:#fff;border-radius:16px;padding:1.5rem;box-shadow:0 4px 20px rgba(0,0,0,.08);position:sticky;top:80px">
      <h3 style="font-size:1rem;font-weight:800;margin-bottom:1rem">Order Items</h3>
      {%- for item in items %}
      <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.75rem">
        <img src="{{ url_for('static', filename='uploads/' + (item.image or 'default.png')) }}"
             style="width:44px;height:44px;object-fit:cover;border-radius:8px"
             onerror="this.src='https://placehold.co/44x44/fce4ec/e91e63?text=?'"/>
        <div style="flex:1;font-size:.85rem">{{ item.name }} × {{ item.quantity }}</div>
        <div style="font-weight:700;color:#e91e63;font-size:.9rem">₹{{ '%.0f'|format(item.price * item.quantity) }}</div>
      </div>
      {%- endfor %}
      <hr style="margin:.75rem 0;border:none;border-top:1px solid #eee"/>
      <div style="display:flex;justify-content:space-between;font-size:1.1rem;font-weight:800">
        <span>Total</span><span style="color:#e91e63">₹{{ '%.0f'|format(total) }}</span>
      </div>
    </div>
  </div>
</div>
{%- endblock %}"""


def _mv_customer_orders_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}My Orders{%- endblock %}
{%- block content %}
<div style="max-width:900px;margin:2rem auto;padding:0 1.5rem">
  <h2 style="font-size:1.5rem;font-weight:800;margin-bottom:1.25rem">📦 My Orders</h2>
  {%- if orders %}
  {%- for o in orders %}
  <a href="{{ url_for('order_detail', oid=o.id) }}" style="text-decoration:none;color:inherit">
    <div style="background:#fff;border-radius:12px;padding:1.25rem;margin-bottom:.75rem;box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.75rem;transition:box-shadow .2s" onmouseover="this.style.boxShadow='0 6px 20px rgba(0,0,0,.12)'" onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,.06)'">
      <div>
        <div style="font-weight:800">Order #{{ o.id }}</div>
        <div style="font-size:.82rem;color:#888;margin-top:.2rem">{{ o.created_at[:10] }} · Ref: {{ o.payment_ref }}</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:1.1rem;font-weight:800;color:#e91e63">₹{{ '%.0f'|format(o.total_price) }}</div>
        <span class="badge badge-{{ o.status }}">{{ o.status|capitalize }}</span>
      </div>
    </div>
  </a>
  {%- endfor %}
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">📦</div>
    <h3 style="margin:.75rem 0;color:#555">No orders yet</h3>
    <a href="{{ url_for('index') }}" class="mv-btn mv-btn-primary">Start Shopping</a>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_order_detail_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Order #{{ order.id }}{%- endblock %}
{%- block content %}
<div style="max-width:700px;margin:2rem auto;padding:0 1.5rem">
  <div style="background:#fff;border-radius:16px;padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,.08);text-align:center;margin-bottom:1.5rem">
    <div style="font-size:3.5rem">✅</div>
    <h2 style="font-size:1.5rem;font-weight:800;margin:.5rem 0">Order #{{ order.id }}</h2>
    <p style="color:#888;font-size:.88rem">{{ order.created_at[:16] }}</p>
    <span class="badge badge-{{ order.status }}" style="font-size:.9rem;padding:.35rem 1rem">{{ order.status|capitalize }}</span>
  </div>

  <!-- Progress tracker -->
  <div style="background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:1rem">
    <h3 style="font-size:.95rem;font-weight:800;margin-bottom:1rem">Order Progress</h3>
    {%- set steps = [('paid','💳','Paid'),('confirmed','✓','Confirmed'),('shipped','🚚','Shipped'),('delivered','🏠','Delivered')] %}
    {%- set step_order = ['paid','confirmed','shipped','delivered'] %}
    {%- set cur = step_order.index(order.status) if order.status in step_order else -1 %}
    <div class="mv-tracker">
      {%- for val, icon, label in steps %}
      {%- set si = loop.index0 %}
      <div class="mv-tracker-step">
        <div class="mv-tracker-dot {{ 'done' if si <= cur and order.status != 'cancelled' else '' }}">{{ icon }}</div>
        <span class="mv-tracker-label">{{ label }}</span>
      </div>
      {%- if not loop.last %}
      <div class="mv-tracker-line {{ 'done' if si < cur and order.status != 'cancelled' else '' }}"></div>
      {%- endif %}
      {%- endfor %}
    </div>
    {%- if order.status == 'cancelled' %}
    <p style="text-align:center;color:#e53935;font-size:.85rem;margin-top:.5rem">This order was cancelled.</p>
    {%- endif %}
  </div>

  <div style="background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:1rem">
    <h3 style="font-size:.95rem;font-weight:800;margin-bottom:1rem">Items Ordered</h3>
    {%- for item in items %}
    <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.75rem">
      <img src="{{ url_for('static', filename='uploads/' + (item.image or 'default.png')) }}"
           style="width:52px;height:52px;object-fit:cover;border-radius:8px"
           onerror="this.src='https://placehold.co/52x52/fce4ec/e91e63?text=?'"/>
      <div style="flex:1">
        <div style="font-weight:700;font-size:.9rem">{{ item.name }}</div>
        <div style="font-size:.8rem;color:#888">Qty: {{ item.quantity }} × ₹{{ '%.0f'|format(item.price) }}</div>
      </div>
      <div style="font-weight:800;color:#e91e63">₹{{ '%.0f'|format(item.price * item.quantity) }}</div>
    </div>
    {%- endfor %}
    <hr style="margin:.75rem 0;border:none;border-top:1px solid #eee"/>
    <div style="display:flex;justify-content:space-between;font-size:1.1rem;font-weight:800">
      <span>Total Paid</span><span style="color:#e91e63">₹{{ '%.0f'|format(order.total_price) }}</span>
    </div>
  </div>

  <div style="background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06)">
    <h3 style="font-size:.95rem;font-weight:800;margin-bottom:.75rem">Order Details</h3>
    <div style="font-size:.88rem;color:#555;display:grid;grid-template-columns:auto 1fr;gap:.4rem 1rem">
      <span style="color:#888">Payment Ref</span><span style="font-family:monospace;font-weight:700">{{ order.payment_ref }}</span>
      <span style="color:#888">Delivery To</span><span>{{ order.address }}</span>
    </div>
  </div>

  <div style="text-align:center;margin-top:1.5rem">
    <a href="{{ url_for('my_orders') }}" class="mv-btn mv-btn-outline" style="margin-right:.75rem">← My Orders</a>
    <a href="{{ url_for('index') }}" class="mv-btn mv-btn-primary">Continue Shopping</a>
  </div>
</div>
{%- endblock %}"""


def _mv_seller_dashboard_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Seller Dashboard{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🏪 Seller Dashboard</h2>
    <a href="{{ url_for('seller_add_product') }}" class="mv-btn mv-btn-primary">+ Add Product</a>
  </div>
  <div class="mv-stat-grid">
    <div class="mv-stat"><div class="mv-stat-val">{{ products|length }}</div><div class="mv-stat-label">Products</div></div>
    <div class="mv-stat"><div class="mv-stat-val">{{ total_orders }}</div><div class="mv-stat-label">Orders</div></div>
    <div class="mv-stat"><div class="mv-stat-val">₹{{ '%.0f'|format(total_earned) }}</div><div class="mv-stat-label">Net Earnings (90%)</div></div>
  </div>
  <div style="display:flex;gap:.75rem;margin-bottom:1.5rem;flex-wrap:wrap">
    <a href="{{ url_for('seller_orders') }}" class="mv-btn mv-btn-outline mv-btn-sm">📦 All Orders</a>
    <a href="{{ url_for('seller_earnings') }}" class="mv-btn mv-btn-outline mv-btn-sm">💰 Earnings Report</a>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>My Products</h3></div>
    {%- if products %}
    <table class="mv-table">
      <thead><tr><th>Image</th><th>Name</th><th>Category</th><th>Price</th><th>Stock</th><th>Actions</th></tr></thead>
      <tbody>
        {%- for p in products %}
        <tr>
          <td><img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
                   style="width:44px;height:44px;object-fit:cover;border-radius:8px"
                   onerror="this.src='https://placehold.co/44x44/fce4ec/e91e63?text=?'"/></td>
          <td style="font-weight:700">{{ p.name }}</td>
          <td><span class="badge" style="background:#fce4ec;color:#e91e63">{{ p.category }}</span></td>
          <td style="color:#e91e63;font-weight:800">₹{{ '%.0f'|format(p.price) }}</td>
          <td>
            {%- if p.stock > 10 %}<span class="badge badge-paid">{{ p.stock }}</span>
            {%- elif p.stock > 0 %}<span class="badge badge-pending">{{ p.stock }}</span>
            {%- else %}<span class="badge badge-cancelled">Out</span>{%- endif %}
          </td>
          <td>
            <a href="{{ url_for('seller_edit_product', pid=p.id) }}" class="mv-btn mv-btn-outline mv-btn-sm">Edit</a>
            <form method="POST" action="{{ url_for('seller_delete_product', pid=p.id) }}" style="display:inline" onsubmit="return confirm('Delete this product?')">
              <button type="submit" class="mv-btn mv-btn-danger mv-btn-sm">Del</button>
            </form>
          </td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
    {%- else %}
    <div style="text-align:center;padding:3rem"><p style="color:#888">No products yet. <a href="{{ url_for('seller_add_product') }}">Add your first product</a>.</p></div>
    {%- endif %}
  </div>
  {%- if recent %}
  <div class="mv-table-wrap" style="margin-top:1.5rem">
    <div class="mv-table-head"><h3>Recent Orders</h3><a href="{{ url_for('seller_orders') }}" style="font-size:.85rem;color:#e91e63">View All</a></div>
    <table class="mv-table">
      <thead><tr><th>Order #</th><th>Customer</th><th>Total</th><th>Status</th><th>Date</th></tr></thead>
      <tbody>
        {%- for o in recent %}
        <tr>
          <td style="font-weight:700">#{{ o.id }}</td>
          <td>{{ o.customer_name }}</td>
          <td style="color:#e91e63;font-weight:800">₹{{ '%.0f'|format(o.total_price) }}</td>
          <td><span class="badge badge-{{ o.status }}">{{ o.status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ o.created_at[:10] }}</td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_seller_product_form_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}{{ 'Edit' if product else 'Add' }} Product{%- endblock %}
{%- block content %}
<div class="mv-form-card">
  <h2>{{ '✏️ Edit' if product else '➕ Add New' }} Product</h2>
  <form method="POST" enctype="multipart/form-data">
    <div class="mv-form-group">
      <label>Product Name *</label>
      <input type="text" name="name" value="{{ product.name if product else '' }}" required placeholder="e.g. Cotton Kurti"/>
    </div>
    <div class="mv-form-group">
      <label>Description</label>
      <textarea name="description" placeholder="Describe your product…">{{ product.description if product else '' }}</textarea>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem">
      <div class="mv-form-group">
        <label>Price (₹) *</label>
        <input type="number" name="price" step="0.01" min="0" value="{{ product.price if product else '' }}" required placeholder="299"/>
      </div>
      <div class="mv-form-group">
        <label>Stock *</label>
        <input type="number" name="stock" min="0" value="{{ product.stock if product else '' }}" required placeholder="50"/>
      </div>
    </div>
    <div class="mv-form-group">
      <label>Category</label>
      <select name="category">
        {%- for cat in categories %}
        <option value="{{ cat }}" {{ 'selected' if product and product.category==cat else '' }}>{{ cat }}</option>
        {%- endfor %}
      </select>
    </div>
    <div class="mv-form-group">
      <label>Product Image</label>
      {%- if product and product.image and product.image != 'default.png' %}
      <div style="margin-bottom:.5rem">
        <img src="{{ url_for('static', filename='uploads/' + product.image) }}"
             style="height:72px;border-radius:8px" alt="current"/>
        <span style="font-size:.78rem;color:#888;margin-left:.5rem">Current image</span>
      </div>
      {%- endif %}
      <input type="file" name="image" accept="image/*"/>
    </div>
    <div style="display:flex;gap:.75rem">
      <button type="submit" class="mv-btn mv-btn-primary">{{ 'Save Changes' if product else 'Add Product' }}</button>
      <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline">Cancel</a>
    </div>
  </form>
</div>
{%- endblock %}"""


def _mv_seller_orders_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Orders Received{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>📦 Orders Received</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  {%- if orders %}
  {%- for order in orders %}
  <div class="mv-table-wrap" style="margin-bottom:1rem">
    <div class="mv-table-head">
      <div>
        <strong>Order #{{ order.id }}</strong>
        <span style="color:#888;font-size:.82rem;margin-left:.75rem">{{ order.created_at[:10] }}</span>
        <span style="margin-left:.75rem">Customer: <strong>{{ order.customer_name }}</strong></span>
      </div>
      <span class="badge badge-{{ order.status }}">{{ order.status|capitalize }}</span>
    </div>
    <div style="padding:1rem">
      {%- for item in order.items if item.product_id in pids %}
      <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.5rem;padding:.5rem;background:#fafafa;border-radius:8px">
        <img src="{{ url_for('static', filename='uploads/' + (item.image or 'default.png')) }}"
             style="width:40px;height:40px;object-fit:cover;border-radius:6px"
             onerror="this.src='https://placehold.co/40x40/fce4ec/e91e63?text=?'"/>
        <span style="flex:1;font-size:.88rem;font-weight:600">{{ item.name }}</span>
        <span style="font-size:.82rem;color:#888">× {{ item.quantity }}</span>
        <span style="font-weight:800;color:#e91e63">₹{{ '%.0f'|format(item.price * item.quantity) }}</span>
      </div>
      {%- endfor %}
      <div style="margin-top:.75rem">
        <form method="POST" action="{{ url_for('seller_update_status', oid=order.id) }}" style="display:flex;gap:.5rem;align-items:center">
          <select name="status" style="padding:.4rem .75rem;border:1.5px solid #eee;border-radius:8px;font-size:.85rem">
            {%- for s in ['pending','paid','confirmed','shipped','delivered','cancelled'] %}
            <option value="{{ s }}" {{ 'selected' if s==order.status else '' }}>{{ s|capitalize }}</option>
            {%- endfor %}
          </select>
          <button type="submit" class="mv-btn mv-btn-primary mv-btn-sm">Update</button>
        </form>
      </div>
    </div>
  </div>
  {%- endfor %}
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">📭</div>
    <h3 style="margin:.75rem 0;color:#555">No orders yet</h3>
    <p style="color:#888">Orders for your products will appear here.</p>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_seller_earnings_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Earnings Report{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>💰 Earnings Report</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-earn-grid">
    <div class="mv-earn-card">
      <div class="mv-earn-val">₹{{ '%.2f'|format(total) }}</div>
      <div class="mv-earn-label">Total Net Earnings (90%)</div>
    </div>
    <div class="mv-earn-card" style="border-top-color:#ff5722">
      <div class="mv-earn-val" style="color:#ff5722">{{ rows|length }}</div>
      <div class="mv-earn-label">Paid Orders</div>
    </div>
    <div class="mv-earn-card" style="border-top-color:#4caf50">
      <div class="mv-earn-val" style="color:#4caf50">₹{{ '%.2f'|format(total / rows|length if rows else 0) }}</div>
      <div class="mv-earn-label">Avg. per Order</div>
    </div>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>Transaction Log</h3></div>
    {%- if rows %}
    <table class="mv-table">
      <thead><tr><th>#</th><th>Order</th><th>Customer</th><th>Order Total</th><th>Your Share (90%)</th><th>Date</th></tr></thead>
      <tbody>
        {%- for r in rows %}
        <tr>
          <td style="color:#888">{{ loop.index }}</td>
          <td style="font-weight:700">#{{ r.order_id }}</td>
          <td>{{ r.customer_name }}</td>
          <td>₹{{ '%.2f'|format(r.total_price) }}</td>
          <td style="font-weight:800;color:#e91e63">₹{{ '%.2f'|format(r.amount) }}</td>
          <td style="color:#888;font-size:.82rem">{{ r.created_at[:16] }}</td>
        </tr>
        {%- endfor %}
      </tbody>
      <tfoot>
        <tr style="background:#fafafa">
          <td colspan="4" style="text-align:right;font-weight:800;padding:.75rem 1rem">Total Earned</td>
          <td style="font-weight:800;color:#e91e63;padding:.75rem 1rem">₹{{ '%.2f'|format(total) }}</td>
          <td></td>
        </tr>
      </tfoot>
    </table>
    {%- else %}
    <div style="text-align:center;padding:3rem"><p style="color:#888">No earnings yet. Start selling!</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""


def _mv_admin_dashboard_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Admin Dashboard{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <h2 style="font-size:1.5rem;font-weight:800;margin-bottom:1.5rem">⚙️ Admin Dashboard</h2>
  <div class="mv-stat-grid">
    <div class="mv-stat"><div class="mv-stat-val">{{ stats.users }}</div><div class="mv-stat-label">Total Users</div></div>
    <div class="mv-stat"><div class="mv-stat-val">{{ stats.sellers }}</div><div class="mv-stat-label">Sellers</div></div>
    <div class="mv-stat"><div class="mv-stat-val">{{ stats.products }}</div><div class="mv-stat-label">Products</div></div>
    <div class="mv-stat"><div class="mv-stat-val">{{ stats.orders }}</div><div class="mv-stat-label">Orders</div></div>
    <div class="mv-stat"><div class="mv-stat-val">₹{{ '%.0f'|format(stats.revenue) }}</div><div class="mv-stat-label">Gross Revenue</div></div>
    <div class="mv-stat" style="border-top:4px solid #4caf50"><div class="mv-stat-val" style="color:#4caf50">₹{{ '%.0f'|format(stats.seller_payouts) }}</div><div class="mv-stat-label">Seller Payouts (90%)</div></div>
    <div class="mv-stat" style="border-top:4px solid #2196f3"><div class="mv-stat-val" style="color:#2196f3">₹{{ '%.0f'|format(stats.platform_income) }}</div><div class="mv-stat-label">Platform Income (10%)</div></div>
  </div>
  <div style="display:flex;gap:.75rem;margin-bottom:1.5rem;flex-wrap:wrap">
    <a href="{{ url_for('admin_users') }}" class="mv-btn mv-btn-outline mv-btn-sm">👥 Users</a>
    <a href="{{ url_for('admin_products') }}" class="mv-btn mv-btn-outline mv-btn-sm">📦 Products</a>
    <a href="{{ url_for('admin_orders') }}" class="mv-btn mv-btn-outline mv-btn-sm">🧾 Orders</a>
    <a href="{{ url_for('admin_earnings') }}" class="mv-btn mv-btn-outline mv-btn-sm">💰 Earnings</a>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>Recent Orders</h3><a href="{{ url_for('admin_orders') }}" style="font-size:.85rem;color:#e91e63">View All</a></div>
    {%- if recent %}
    <table class="mv-table">
      <thead><tr><th>Order #</th><th>Customer</th><th>Total</th><th>Status</th><th>Ref</th><th>Date</th></tr></thead>
      <tbody>
        {%- for o in recent %}
        <tr>
          <td style="font-weight:700">#{{ o.id }}</td>
          <td>{{ o.customer_name }}</td>
          <td style="color:#e91e63;font-weight:800">₹{{ '%.2f'|format(o.total_price) }}</td>
          <td><span class="badge badge-{{ o.status }}">{{ o.status|capitalize }}</span></td>
          <td style="font-family:monospace;font-size:.78rem;color:#888">{{ o.payment_ref }}</td>
          <td style="color:#888;font-size:.82rem">{{ o.created_at[:10] }}</td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
    {%- else %}
    <div style="text-align:center;padding:2rem"><p style="color:#888">No orders yet.</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""


def _mv_admin_users_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Manage Users{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>👥 All Users</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>#</th><th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th>Action</th></tr></thead>
      <tbody>
        {%- for u in users %}
        <tr>
          <td style="color:#888">{{ u.id }}</td>
          <td style="font-weight:700">{{ u.name }}</td>
          <td style="color:#888;font-size:.85rem">{{ u.email }}</td>
          <td>
            {%- if u.role == 'admin' %}<span class="badge badge-cancelled">Admin</span>
            {%- elif u.role == 'seller' %}<span class="badge badge-confirmed">Seller</span>
            {%- else %}<span class="badge badge-paid">Customer</span>{%- endif %}
          </td>
          <td style="color:#888;font-size:.82rem">{{ u.created_at[:10] }}</td>
          <td>
            {%- if u.role != 'admin' %}
            <form method="POST" action="{{ url_for('admin_delete_user', uid=u.id) }}" onsubmit="return confirm('Delete {{ u.name }}?')">
              <button type="submit" class="mv-btn mv-btn-danger mv-btn-sm">Delete</button>
            </form>
            {%- endif %}
          </td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_products_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Manage Products{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>📦 All Products</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>Image</th><th>Name</th><th>Seller</th><th>Category</th><th>Price</th><th>Stock</th><th>Action</th></tr></thead>
      <tbody>
        {%- for p in products %}
        <tr>
          <td><img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
                   style="width:40px;height:40px;object-fit:cover;border-radius:6px"
                   onerror="this.src='https://placehold.co/40x40/fce4ec/e91e63?text=?'"/></td>
          <td style="font-weight:700">{{ p.name }}</td>
          <td style="color:#888;font-size:.85rem">{{ p.seller_name }}</td>
          <td><span class="badge" style="background:#fce4ec;color:#e91e63">{{ p.category }}</span></td>
          <td style="color:#e91e63;font-weight:800">₹{{ '%.0f'|format(p.price) }}</td>
          <td>{{ p.stock }}</td>
          <td>
            <form method="POST" action="{{ url_for('admin_delete_product', pid=p.id) }}" onsubmit="return confirm('Delete this product?')">
              <button type="submit" class="mv-btn mv-btn-danger mv-btn-sm">Delete</button>
            </form>
          </td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_orders_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Manage Orders{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🧾 All Orders</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>#</th><th>Customer</th><th>Total</th><th>Payment Ref</th><th>Status</th><th>Date</th><th>Update</th></tr></thead>
      <tbody>
        {%- for o in orders %}
        <tr>
          <td style="font-weight:700">#{{ o.id }}</td>
          <td>{{ o.customer_name }}</td>
          <td style="color:#e91e63;font-weight:800">₹{{ '%.2f'|format(o.total_price) }}</td>
          <td style="font-family:monospace;font-size:.78rem;color:#888">{{ o.payment_ref }}</td>
          <td><span class="badge badge-{{ o.status }}">{{ o.status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ o.created_at[:10] }}</td>
          <td>
            <form method="POST" action="{{ url_for('admin_update_status', oid=o.id) }}" style="display:flex;gap:.4rem">
              <select name="status" style="padding:.35rem .6rem;border:1.5px solid #eee;border-radius:6px;font-size:.82rem">
                {%- for s in ['pending','paid','confirmed','shipped','delivered','cancelled'] %}
                <option value="{{ s }}" {{ 'selected' if s==o.status else '' }}>{{ s|capitalize }}</option>
                {%- endfor %}
              </select>
              <button type="submit" class="mv-btn mv-btn-primary mv-btn-sm">Save</button>
            </form>
          </td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_earnings_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Platform Earnings{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>💰 Platform Earnings</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-earn-grid">
    <div class="mv-earn-card" style="border-top-color:#2196f3">
      <div class="mv-earn-val" style="color:#2196f3">₹{{ '%.2f'|format(total) }}</div>
      <div class="mv-earn-label">Total Commission (10%)</div>
    </div>
    <div class="mv-earn-card">
      <div class="mv-earn-val">{{ rows|length }}</div>
      <div class="mv-earn-label">Paid Orders</div>
    </div>
  </div>
  {%- if seller_summary %}
  <div class="mv-table-wrap" style="margin-bottom:1.5rem">
    <div class="mv-table-head"><h3>Seller Payout Summary</h3></div>
    <table class="mv-table">
      <thead><tr><th>Seller</th><th>Email</th><th>Total Paid Out (90%)</th></tr></thead>
      <tbody>
        {%- for name, email, total_s in seller_summary %}
        <tr>
          <td style="font-weight:700">{{ name }}</td>
          <td style="color:#888;font-size:.85rem">{{ email }}</td>
          <td style="font-weight:800;color:#4caf50">₹{{ '%.2f'|format(total_s) }}</td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
  {%- endif %}
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>Commission Log</h3></div>
    {%- if rows %}
    <table class="mv-table">
      <thead><tr><th>#</th><th>Order</th><th>Customer</th><th>Order Total</th><th>Ref</th><th>Commission (10%)</th><th>Date</th></tr></thead>
      <tbody>
        {%- for r in rows %}
        <tr>
          <td style="color:#888">{{ loop.index }}</td>
          <td style="font-weight:700">#{{ r.order_id }}</td>
          <td>{{ r.customer_name }}</td>
          <td>₹{{ '%.2f'|format(r.total_price) }}</td>
          <td style="font-family:monospace;font-size:.78rem;color:#888">{{ r.payment_ref }}</td>
          <td style="font-weight:800;color:#2196f3">₹{{ '%.2f'|format(r.amount) }}</td>
          <td style="color:#888;font-size:.82rem">{{ r.created_at[:16] }}</td>
        </tr>
        {%- endfor %}
      </tbody>
      <tfoot>
        <tr style="background:#fafafa">
          <td colspan="5" style="text-align:right;font-weight:800;padding:.75rem 1rem">Total Commission</td>
          <td style="font-weight:800;color:#2196f3;padding:.75rem 1rem">₹{{ '%.2f'|format(total) }}</td>
          <td></td>
        </tr>
      </tfoot>
    </table>
    {%- else %}
    <div style="text-align:center;padding:3rem"><p style="color:#888">No commissions yet.</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""


def _mv_seller_store_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}{{ profile.shop_name }} — Store{%- endblock %}
{%- block content %}
<div style="background:linear-gradient(135deg,#e91e63,#ff5722);height:90px;border-radius:0 0 16px 16px;margin:-1rem -1rem 0"></div>
<div style="max-width:1200px;margin:0 auto;padding:0 1rem">
  <div style="display:flex;align-items:flex-end;gap:1rem;margin-top:-40px;margin-bottom:1.5rem">
    <img src="{{ url_for('static', filename='uploads/' + (profile.logo or 'default.png')) }}"
         style="width:80px;height:80px;border-radius:50%;border:4px solid #fff;object-fit:cover;background:#fff"
         onerror="this.src='https://placehold.co/80x80/e91e63/fff?text={{ profile.shop_name[0]|upper }}'"/>
    <div style="padding-bottom:.5rem">
      <h3 style="font-weight:800;margin:0">{{ profile.shop_name }}</h3>
      <p style="color:#888;font-size:.85rem;margin:0">{{ products|length }} product{{ 's' if products|length != 1 }}</p>
      {%- if profile.description %}<p style="color:#666;font-size:.88rem;margin:.25rem 0 0">{{ profile.description }}</p>{%- endif %}
    </div>
  </div>
  <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.25rem">
    <form style="display:flex;gap:.5rem;flex:1;min-width:200px" action="{{ url_for('seller_store', shop_slug=profile.shop_slug) }}" method="get">
      <input class="mv-search-input" type="search" name="q" placeholder="Search in {{ profile.shop_name }}…" value="{{ q }}" style="flex:1;padding:.5rem 1rem;border:1.5px solid #eee;border-radius:24px;outline:none"/>
      <button type="submit" class="mv-btn mv-btn-primary mv-btn-sm">Search</button>
    </form>
    <a href="{{ url_for('seller_store', shop_slug=profile.shop_slug) }}"
       style="padding:.3rem .9rem;border-radius:20px;font-size:.82rem;border:1.5px solid {% if not selected_cat %}#e91e63{% else %}#eee{% endif %};background:{% if not selected_cat %}#e91e63{% else %}#fff{% endif %};color:{% if not selected_cat %}#fff{% else %}#555{% endif %};text-decoration:none">All</a>
    {%- for cat in categories %}
    <a href="{{ url_for('seller_store', shop_slug=profile.shop_slug, category=cat) }}"
       style="padding:.3rem .9rem;border-radius:20px;font-size:.82rem;border:1.5px solid {% if selected_cat==cat %}#e91e63{% else %}#eee{% endif %};background:{% if selected_cat==cat %}#e91e63{% else %}#fff{% endif %};color:{% if selected_cat==cat %}#fff{% else %}#555{% endif %};text-decoration:none">{{ cat }}</a>
    {%- endfor %}
  </div>
  {%- if products %}
  <div class="mv-grid">
    {%- for p in products %}
    <div class="mv-card" onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
      <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
           alt="{{ p.name }}" onerror="this.src='https://placehold.co/300x300/fce4ec/e91e63?text=No+Image'"/>
      <div class="mv-card-body">
        <div class="mv-card-name">{{ p.name }}</div>
        <div class="mv-card-price">₹{{ '%.0f'|format(p.price) }}</div>
      </div>
    </div>
    {%- endfor %}
  </div>
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">📦</div>
    <p style="color:#888;margin-top:.75rem">No products found in this store.</p>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_notifications_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Notifications{%- endblock %}
{%- block content %}
<div style="max-width:700px;margin:2rem auto;padding:0 1rem">
  <h4 style="font-weight:800;margin-bottom:1.25rem">🔔 Notifications</h4>
  {%- if notifications %}
  {%- for n in notifications %}
  <div style="background:#fff;border-radius:12px;padding:1rem 1.25rem;margin-bottom:.6rem;box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;justify-content:space-between;align-items:center;{% if not n.is_read %}border-left:4px solid #e91e63{% endif %}">
    <div>
      <p style="margin:0;font-weight:{% if not n.is_read %}700{% else %}400{% endif %}">{{ n.message }}</p>
      <small style="color:#888">{{ n.created_at[:16] }}</small>
    </div>
    {%- if n.link %}
    <a href="{{ n.link }}" class="mv-btn mv-btn-outline mv-btn-sm" style="flex-shrink:0;margin-left:1rem">View</a>
    {%- endif %}
  </div>
  {%- endfor %}
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">🔕</div>
    <p style="color:#888;margin-top:.75rem">No notifications yet.</p>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_seller_shop_profile_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Shop Profile{%- endblock %}
{%- block content %}
<div style="max-width:800px;margin:2rem auto;padding:0 1rem">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem">
    <h4 style="font-weight:800;margin:0">🏪 Shop Profile</h4>
    <div style="display:flex;gap:.5rem">
      {%- if profile %}
      <a href="{{ url_for('seller_store', shop_slug=profile.shop_slug) }}"
         class="mv-btn mv-btn-outline mv-btn-sm" target="_blank">View Store ↗</a>
      {%- endif %}
      <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:200px 1fr;gap:1.5rem">
    <div style="background:#fff;border-radius:12px;padding:1.5rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06)">
      <img src="{{ url_for('static', filename='uploads/' + (profile.logo or 'default.png')) }}"
           style="width:80px;height:80px;border-radius:50%;object-fit:cover;margin-bottom:.75rem"
           onerror="this.src='https://placehold.co/80x80/e91e63/fff?text={{ profile.shop_name[0]|upper }}'"/>
      <p style="font-weight:800;margin:0">{{ profile.shop_name }}</p>
      <p style="font-size:.75rem;color:#888;font-family:monospace">/store/{{ profile.shop_slug }}</p>
    </div>
    <div style="background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06)">
      <h5 style="font-weight:800;margin-bottom:1rem">Edit Shop Details</h5>
      <form method="POST" enctype="multipart/form-data">
        <div class="mv-form-group">
          <label>Shop Name</label>
          <input type="text" name="shop_name" class="mv-form-input" value="{{ profile.shop_name }}" required maxlength="120"/>
        </div>
        <div class="mv-form-group">
          <label>Description</label>
          <textarea name="description" class="mv-form-input" rows="3" placeholder="Tell customers about your shop…">{{ profile.description or '' }}</textarea>
        </div>
        <div class="mv-form-group">
          <label>Shop Logo</label>
          {%- if profile.logo and profile.logo != 'default.png' %}
          <div style="margin-bottom:.5rem">
            <img src="{{ url_for('static', filename='uploads/' + profile.logo) }}"
                 style="height:56px;border-radius:8px"/>
          </div>
          {%- endif %}
          <input type="file" name="logo" accept="image/*" style="width:100%"/>
        </div>
        <button type="submit" class="mv-btn mv-btn-primary">Save Changes</button>
      </form>
    </div>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_sellers_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Manage Sellers{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🏪 Manage Sellers</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>Logo</th><th>Shop Name</th><th>Store URL</th><th>Seller</th><th>Email</th><th>Products</th><th>Joined</th></tr></thead>
      <tbody>
        {%- for s in sellers %}
        <tr>
          <td><img src="{{ url_for('static', filename='uploads/' + (s.logo or 'default.png')) }}"
                   style="width:36px;height:36px;border-radius:50%;object-fit:cover"
                   onerror="this.src='https://placehold.co/36x36/e91e63/fff?text={{ s.name[0]|upper }}'"/></td>
          <td style="font-weight:700">{{ s.shop_name or '—' }}</td>
          <td>{%- if s.shop_slug %}<a href="{{ url_for('seller_store', shop_slug=s.shop_slug) }}" style="font-family:monospace;font-size:.78rem;color:#e91e63" target="_blank">/store/{{ s.shop_slug }}</a>{%- else %}—{%- endif %}</td>
          <td>{{ s.name }}</td>
          <td style="color:#888;font-size:.85rem">{{ s.email }}</td>
          <td>—</td>
          <td style="color:#888;font-size:.82rem">{{ s.created_at[:10] }}</td>
        </tr>
        {%- else %}
        <tr><td colspan="7" style="text-align:center;color:#888;padding:2rem">No sellers yet.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_coupons_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Coupons — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🏷️ Coupon Management</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap" style="margin-bottom:1.5rem">
    <div style="padding:1.25rem;border-bottom:1px solid #eee;font-weight:700">Create New Coupon</div>
    <div style="padding:1.25rem">
      <form method="POST" action="{{ url_for('admin_add_coupon') }}" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.75rem;align-items:end">
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Code *</label>
          <input type="text" name="code" class="mv-form-input" placeholder="SAVE20" required style="text-transform:uppercase"/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Type</label>
          <select name="discount_type" class="mv-form-input"><option value="percent">Percent (%)</option><option value="fixed">Fixed ($)</option></select></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Value *</label>
          <input type="number" name="discount_value" class="mv-form-input" step="0.01" min="0.01" placeholder="20" required/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Min Order</label>
          <input type="number" name="min_order" class="mv-form-input" step="0.01" min="0" placeholder="0"/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Max Uses (0=∞)</label>
          <input type="number" name="max_uses" class="mv-form-input" min="0" placeholder="0"/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Expires</label>
          <input type="date" name="expires_at" class="mv-form-input"/></div>
        <div><button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Create</button></div>
      </form>
    </div>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>Code</th><th>Type</th><th>Value</th><th>Min</th><th>Uses</th><th>Expires</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>
        {%- for c in coupons %}
        <tr>
          <td style="font-weight:700;font-family:monospace">{{ c.code }}</td>
          <td>{{ c.discount_type|capitalize }}</td>
          <td>{{ c.discount_value }}{{ '%' if c.discount_type=='percent' else '$' }}</td>
          <td>${{ '%.0f'|format(c.min_order) }}</td>
          <td>{{ c.used_count }}{% if c.max_uses > 0 %}/{{ c.max_uses }}{% endif %}</td>
          <td style="font-size:.82rem;color:#888">{{ c.expires_at[:10] if c.expires_at else '—' }}</td>
          <td><span class="badge {% if c.is_active %}badge-paid{% else %}badge-cancelled{% endif %}">{{ 'Active' if c.is_active else 'Inactive' }}</span></td>
          <td>
            <form method="POST" action="{{ url_for('admin_toggle_coupon', cid=c.id) }}" style="display:inline">
              <button class="mv-btn mv-btn-outline mv-btn-sm">{{ 'Deactivate' if c.is_active else 'Activate' }}</button>
            </form>
            <form method="POST" action="{{ url_for('admin_delete_coupon', cid=c.id) }}" style="display:inline" onsubmit="return confirm('Delete?')">
              <button class="mv-btn mv-btn-danger mv-btn-sm">Del</button>
            </form>
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="8" style="text-align:center;color:#888;padding:2rem">No coupons yet.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_withdrawals_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Withdrawals — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>💸 Withdrawal Requests</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>#</th><th>Seller</th><th>Amount</th><th>UPI ID</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
      <tbody>
        {%- for r in reqs %}
        <tr>
          <td>{{ r.id }}</td>
          <td style="font-weight:700">{{ r.seller_name }}</td>
          <td style="font-weight:800;color:#4caf50">${{ '%.2f'|format(r.amount) }}</td>
          <td style="font-size:.85rem">{{ r.upi_id }}</td>
          <td><span class="badge {% if r.status=='approved' %}badge-paid{% elif r.status=='rejected' %}badge-cancelled{% else %}badge-pending{% endif %}">{{ r.status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ r.created_at[:10] }}</td>
          <td>
            {%- if r.status == 'pending' %}
            <form method="POST" action="{{ url_for('admin_withdrawal_action', rid=r.id) }}" style="display:flex;gap:.4rem">
              <input type="text" name="note" placeholder="Note" style="padding:.3rem .6rem;border:1.5px solid #eee;border-radius:6px;font-size:.82rem;width:110px"/>
              <button name="action" value="approved" class="mv-btn mv-btn-primary mv-btn-sm">Approve</button>
              <button name="action" value="rejected" class="mv-btn mv-btn-danger mv-btn-sm">Reject</button>
            </form>
            {%- else %}
            <span style="color:#888;font-size:.82rem">{{ r.note or '—' }}</span>
            {%- endif %}
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="7" style="text-align:center;color:#888;padding:2rem">No withdrawal requests.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_reviews_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Reviews — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>⭐ Product Reviews</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>#</th><th>Product</th><th>Customer</th><th>Rating</th><th>Comment</th><th>Date</th><th>Action</th></tr></thead>
      <tbody>
        {%- for r in reviews %}
        <tr>
          <td>{{ r.id }}</td>
          <td style="font-weight:700">{{ r.product_name }}</td>
          <td>{{ r.reviewer_name }}</td>
          <td>
            <span style="color:#ffc107">
              {%- for i in range(1,6) %}{{ '★' if i <= r.rating else '☆' }}{%- endfor %}
            </span>
            <span style="font-weight:700;margin-left:.25rem">{{ r.rating }}/5</span>
          </td>
          <td style="color:#888;font-size:.85rem;max-width:180px">{{ r.comment or '—' }}</td>
          <td style="color:#888;font-size:.82rem">{{ r.created_at[:10] }}</td>
          <td>
            <form method="POST" action="{{ url_for('admin_delete_review', rid=r.id) }}" onsubmit="return confirm('Delete?')">
              <button class="mv-btn mv-btn-danger mv-btn-sm">Delete</button>
            </form>
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="7" style="text-align:center;color:#888;padding:2rem">No reviews yet.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""
