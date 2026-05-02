"""
generator.py — Code Generation Engine
Produces complete, working website code from a config dict.
Supports: static HTML/CSS/JS, Flask + SQLite, E-commerce dashboard.
"""
import os
import shutil
import zipfile
from pathlib import Path

GENERATED_DIR = Path(os.path.dirname(__file__)) / "generated"
GENERATED_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def build_project(project_id: str, config: dict) -> dict:
    """
    Entry point. Reads config, generates all files, writes to disk.
    Returns {"files": [...], "type": "static|flask|ecommerce|startup|blog|portfolio_adv"}
    """
    ptype = config.get("project_type", "static")

    if ptype == "ecommerce":
        files = _gen_ecommerce(config)
    elif ptype == "startup":
        files = _gen_startup(config)
    elif ptype == "blog":
        files = _gen_blog(config)
    elif ptype == "portfolio_adv":
        files = _gen_portfolio_advanced(config)
    elif ptype == "flask":
        files = _gen_flask(config)
    else:
        files = _gen_static(config)

    _write_files(project_id, files)
    return {"files": sorted(files.keys()), "type": ptype}


def make_zip(project_id: str) -> Path:
    """Zip the generated project folder and return the zip path."""
    project_path = GENERATED_DIR / project_id
    zip_path = GENERATED_DIR / f"{project_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in project_path.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(GENERATED_DIR))
    return zip_path


def read_file(project_id: str, filepath: str) -> str | None:
    """Read a generated file and return its text content."""
    path = GENERATED_DIR / project_id / filepath
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def project_exists(project_id: str) -> bool:
    return (GENERATED_DIR / project_id).exists()


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _write_files(project_id: str, files: dict) -> None:
    """Write all files to disk, creating directories as needed."""
    project_path = GENERATED_DIR / project_id
    if project_path.exists():
        shutil.rmtree(project_path)
    project_path.mkdir(parents=True)
    for filepath, content in files.items():
        full = project_path / filepath
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")


def _c(config: dict, key: str, default=""):
    """Safe config getter."""
    return config.get(key) or default


# ─────────────────────────────────────────────────────────────────────────────
# 1. STATIC GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def _gen_static(config: dict) -> dict:
    """Generate a pure HTML/CSS/JS website."""
    site_name   = _c(config, "site_name", "My Website")
    tagline     = _c(config, "tagline", "Welcome to our website")
    primary     = _c(config, "primary_color", "#6c63ff")
    secondary   = _c(config, "secondary_color", "#f50057")
    font        = _c(config, "font", "Poppins")
    sections    = config.get("sections", ["header", "hero", "about", "contact", "footer"])
    website_type = _c(config, "website_type", "business")

    return {
        "index.html":    _static_html(site_name, tagline, font, sections, website_type),
        "style.css":     _base_css(primary, secondary, font),
        "script.js":     _base_js(),
        "README.txt":    _readme_static(site_name),
    }


def _static_html(name, tagline, font, sections, wtype) -> str:
    body = _build_sections(sections, name, tagline, wtype)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{name}</title>
  <link href="https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@300;400;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="style.css"/>
</head>
<body>
{body}
<script src="script.js"></script>
</body>
</html>"""


def _build_sections(sections: list, name: str, tagline: str, wtype: str) -> str:
    """Assemble HTML sections based on user selection."""
    parts = []

    if "header" in sections:
        nav_links = _nav_links_for_type(wtype, sections)
        parts.append(f"""<header class="site-header">
  <nav class="navbar">
    <div class="logo">{name}</div>
    <ul class="nav-links" id="navLinks">
      {nav_links}
    </ul>
    <button class="hamburger" onclick="toggleNav()" aria-label="Toggle menu">&#9776;</button>
  </nav>
</header>""")

    if "hero" in sections:
        parts.append(f"""<section class="hero" id="home">
  <div class="hero-content">
    <h1>{name}</h1>
    <p>{tagline}</p>
    <a href="#contact" class="btn-primary">Get Started</a>
  </div>
</section>""")

    if "about" in sections:
        parts.append("""<section class="about section" id="about">
  <div class="container">
    <h2 class="section-title">About Us</h2>
    <div class="about-grid">
      <div class="about-text">
        <p>We are passionate about delivering the best experience. Our team works hard to create innovative solutions that make a real difference.</p>
        <p>Founded with a vision to simplify complexity, we bring expertise and dedication to every project.</p>
      </div>
      <div class="about-stats">
        <div class="stat"><span class="stat-num">500+</span><span>Clients</span></div>
        <div class="stat"><span class="stat-num">10+</span><span>Years</span></div>
        <div class="stat"><span class="stat-num">99%</span><span>Satisfaction</span></div>
      </div>
    </div>
  </div>
</section>""")

    if "services" in sections:
        parts.append("""<section class="services section" id="services">
  <div class="container">
    <h2 class="section-title">Our Services</h2>
    <div class="cards-grid">
      <div class="card"><div class="card-icon">🚀</div><h3>Strategy</h3><p>We craft data-driven strategies tailored to your goals.</p></div>
      <div class="card"><div class="card-icon">🎨</div><h3>Design</h3><p>Beautiful, user-centric designs that convert visitors.</p></div>
      <div class="card"><div class="card-icon">⚙️</div><h3>Development</h3><p>Robust, scalable solutions built with modern tech.</p></div>
      <div class="card"><div class="card-icon">📈</div><h3>Growth</h3><p>Continuous optimisation to keep you ahead.</p></div>
    </div>
  </div>
</section>""")

    if "portfolio" in sections:
        parts.append("""<section class="portfolio section" id="portfolio">
  <div class="container">
    <h2 class="section-title">Portfolio</h2>
    <div class="portfolio-grid">
      <div class="portfolio-item"><img src="https://picsum.photos/seed/p1/400/250" alt="Project 1"/><div class="portfolio-overlay"><h3>Project One</h3><p>Web Design</p></div></div>
      <div class="portfolio-item"><img src="https://picsum.photos/seed/p2/400/250" alt="Project 2"/><div class="portfolio-overlay"><h3>Project Two</h3><p>Branding</p></div></div>
      <div class="portfolio-item"><img src="https://picsum.photos/seed/p3/400/250" alt="Project 3"/><div class="portfolio-overlay"><h3>Project Three</h3><p>Development</p></div></div>
    </div>
  </div>
</section>""")

    if "blog" in sections:
        parts.append("""<section class="blog section" id="blog">
  <div class="container">
    <h2 class="section-title">Latest Posts</h2>
    <div class="cards-grid">
      <div class="card"><img src="https://picsum.photos/seed/b1/400/200" alt="Post" style="width:100%;border-radius:8px;margin-bottom:1rem"/><span class="tag">Design</span><h3>The Future of Web Design</h3><p>Exploring trends that will shape the web in 2025 and beyond.</p><a href="#" class="read-more">Read more →</a></div>
      <div class="card"><img src="https://picsum.photos/seed/b2/400/200" alt="Post" style="width:100%;border-radius:8px;margin-bottom:1rem"/><span class="tag">Tech</span><h3>Building Scalable APIs</h3><p>Best practices for designing APIs that grow with your product.</p><a href="#" class="read-more">Read more →</a></div>
      <div class="card"><img src="https://picsum.photos/seed/b3/400/200" alt="Post" style="width:100%;border-radius:8px;margin-bottom:1rem"/><span class="tag">Business</span><h3>Growth Hacking in 2025</h3><p>Proven strategies to accelerate your startup's growth.</p><a href="#" class="read-more">Read more →</a></div>
    </div>
  </div>
</section>""")

    if "products" in sections:
        parts.append("""<section class="products section" id="products">
  <div class="container">
    <h2 class="section-title">Our Products</h2>
    <div class="cards-grid">
      <div class="product-card"><img src="https://picsum.photos/seed/pr1/300/200" alt="Product 1"/><div class="product-info"><h3>Product One</h3><p class="product-desc">High quality item with premium features.</p><div class="product-footer"><span class="price">$29.99</span><button class="btn-primary btn-sm">Add to Cart</button></div></div></div>
      <div class="product-card"><img src="https://picsum.photos/seed/pr2/300/200" alt="Product 2"/><div class="product-info"><h3>Product Two</h3><p class="product-desc">Best seller with excellent reviews.</p><div class="product-footer"><span class="price">$49.99</span><button class="btn-primary btn-sm">Add to Cart</button></div></div></div>
      <div class="product-card"><img src="https://picsum.photos/seed/pr3/300/200" alt="Product 3"/><div class="product-info"><h3>Product Three</h3><p class="product-desc">Limited edition, grab yours today.</p><div class="product-footer"><span class="price">$19.99</span><button class="btn-primary btn-sm">Add to Cart</button></div></div></div>
    </div>
  </div>
</section>""")

    if "testimonials" in sections:
        parts.append("""<section class="testimonials section" id="testimonials">
  <div class="container">
    <h2 class="section-title">What Clients Say</h2>
    <div class="testimonials-grid">
      <div class="testimonial"><p>"Absolutely fantastic service. Exceeded all our expectations!"</p><div class="testimonial-author"><img src="https://i.pravatar.cc/50?img=1" alt="Client"/><div><strong>Alice Johnson</strong><span>CEO, TechCorp</span></div></div></div>
      <div class="testimonial"><p>"Professional, fast, and the results speak for themselves."</p><div class="testimonial-author"><img src="https://i.pravatar.cc/50?img=2" alt="Client"/><div><strong>Bob Smith</strong><span>Founder, StartupX</span></div></div></div>
      <div class="testimonial"><p>"I would recommend them to anyone looking for quality work."</p><div class="testimonial-author"><img src="https://i.pravatar.cc/50?img=3" alt="Client"/><div><strong>Carol White</strong><span>Designer, Studio Y</span></div></div></div>
    </div>
  </div>
</section>""")

    if "contact" in sections:
        parts.append("""<section class="contact section" id="contact">
  <div class="container">
    <h2 class="section-title">Contact Us</h2>
    <div class="contact-layout">
      <div class="contact-info">
        <div class="contact-item"><span>📧</span><p>hello@example.com</p></div>
        <div class="contact-item"><span>📞</span><p>+1 (555) 000-0000</p></div>
        <div class="contact-item"><span>📍</span><p>123 Main St, City, Country</p></div>
      </div>
      <form class="contact-form" onsubmit="handleContact(event)">
        <input type="text" name="name" placeholder="Your Name" required/>
        <input type="email" name="email" placeholder="Your Email" required/>
        <input type="text" name="subject" placeholder="Subject"/>
        <textarea name="message" rows="5" placeholder="Your Message" required></textarea>
        <button type="submit" class="btn-primary">Send Message</button>
      </form>
    </div>
  </div>
</section>""")

    if "footer" in sections:
        parts.append(f"""<footer class="site-footer">
  <div class="footer-content">
    <div class="footer-brand"><div class="logo">{name}</div><p>Building the future, one project at a time.</p></div>
    <div class="footer-links"><h4>Quick Links</h4><ul><li><a href="#home">Home</a></li><li><a href="#about">About</a></li><li><a href="#contact">Contact</a></li></ul></div>
    <div class="footer-social"><h4>Follow Us</h4><div class="social-icons"><a href="#">Twitter</a><a href="#">LinkedIn</a><a href="#">GitHub</a></div></div>
  </div>
  <div class="footer-bottom"><p>&copy; 2025 {name}. All rights reserved.</p></div>
</footer>""")

    return "\n\n".join(parts)


def _nav_links_for_type(wtype: str, sections: list) -> str:
    """Generate nav links appropriate for the website type."""
    links = [("Home", "#home")]
    if "about" in sections:    links.append(("About", "#about"))
    if "services" in sections: links.append(("Services", "#services"))
    if "portfolio" in sections:links.append(("Portfolio", "#portfolio"))
    if "products" in sections: links.append(("Products", "#products"))
    if "blog" in sections:     links.append(("Blog", "#blog"))
    if "contact" in sections:  links.append(("Contact", "#contact"))
    return "\n      ".join(f'<li><a href="{href}">{label}</a></li>' for label, href in links)


# ─────────────────────────────────────────────────────────────────────────────
# 2. FLASK GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def _gen_flask(config: dict) -> dict:
    """Generate a full Flask project with optional auth and SQLite DB."""
    site_name = _c(config, "site_name", "My App")
    primary   = _c(config, "primary_color", "#6c63ff")
    secondary = _c(config, "secondary_color", "#f50057")
    font      = _c(config, "font", "Poppins")
    has_auth  = config.get("has_auth", False)
    has_db    = config.get("has_db", False)
    sections  = config.get("sections", ["header", "hero", "contact", "footer"])
    wtype     = _c(config, "website_type", "business")

    files = {}
    files["app.py"]                      = _flask_app_py(site_name, has_auth, has_db)
    files["templates/base.html"]         = _flask_base_html(site_name, has_auth, font)
    files["templates/index.html"]        = _flask_index_html(site_name, sections, wtype)
    files["static/css/style.css"]        = _base_css(primary, secondary, font) + _flask_extra_css()
    files["static/js/script.js"]         = _base_js()
    files["requirements.txt"]            = "Flask==3.0.0\nWerkzeug==3.0.1\n"
    files["README.txt"]                  = _readme_flask(site_name, has_auth)

    if has_auth:
        files["templates/login.html"]    = _flask_login_html()
        files["templates/signup.html"]   = _flask_signup_html()

    return files


def _flask_app_py(site_name: str, has_auth: bool, has_db: bool) -> str:
    auth_block = """
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            flash('Welcome back, ' + username + '!', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (username, password) VALUES (?,?)', (username, password))
            conn.commit()
            conn.close()
            flash('Account created! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('Username already taken.', 'error')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
""" if has_auth else ""

    db_block = """
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT,
            email   TEXT,
            message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()
""" if has_db else ""

    contact_save = """
    # Save contact message to database
    conn = get_db()
    conn.execute('INSERT INTO contacts (name, email, message) VALUES (?,?,?)',
                 (name, email, message))
    conn.commit()
    conn.close()""" if has_db else ""

    return f'''"""
app.py — {site_name}
Generated by WebGen Platform
"""
import os
from flask import (Flask, render_template, request,
                   redirect, url_for, session, flash)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production')
{db_block}
{auth_block}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    name    = request.form.get('name', '')
    email   = request.form.get('email', '')
    message = request.form.get('message', '')
    {contact_save}
    flash(f'Thanks {{name}}! We will get back to you soon.', 'success')
    return redirect(url_for('index') + '#contact')

if __name__ == '__main__':
    {'init_db()' if has_db else '# No database needed for this project'}
    app.run(debug=True)
'''


def _flask_base_html(site_name: str, has_auth: bool, font: str) -> str:
    auth_links = """
      {% if session.user %}
        <li><a href="{{ url_for('logout') }}">Logout ({{ session.user }})</a></li>
      {% else %}
        <li><a href="{{ url_for('login') }}">Login</a></li>
        <li><a href="{{ url_for('signup') }}">Sign Up</a></li>
      {% endif %}""" if has_auth else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{% block title %}}{site_name}{{% endblock %}}</title>
  <link href="https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@300;400;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}"/>
</head>
<body>
<header class="site-header">
  <nav class="navbar">
    <div class="logo">{site_name}</div>
    <ul class="nav-links" id="navLinks">
      <li><a href="{{{{ url_for('index') }}}}">Home</a></li>
      <li><a href="#about">About</a></li>
      <li><a href="#contact">Contact</a></li>
      {auth_links}
    </ul>
    <button class="hamburger" onclick="toggleNav()">&#9776;</button>
  </nav>
</header>

{{%- with messages = get_flashed_messages(with_categories=true) %}}
  {{%- if messages %}}
    {{%- for cat, msg in messages %}}
      <div class="flash flash-{{{{ cat }}}}">{{{{ msg }}}}</div>
    {{%- endfor %}}
  {{%- endif %}}
{{%- endwith %}}

{{%- block content %}}{{%- endblock %}}

<footer class="site-footer">
  <div class="footer-bottom"><p>&copy; 2025 {site_name}. All rights reserved.</p></div>
</footer>
<script src="{{{{ url_for('static', filename='js/script.js') }}}}"></script>
</body>
</html>"""


def _flask_index_html(site_name: str, sections: list, wtype: str) -> str:
    body = _build_sections(sections, site_name, "Welcome to " + site_name, wtype)
    # Convert static form to Flask POST form
    body = body.replace(
        'class="contact-form" onsubmit="handleContact(event)"',
        "class=\"contact-form\" method=\"POST\" action=\"{{ url_for('contact') }}\""
    )
    return """{% extends 'base.html' %}
{% block content %}
""" + body + """
{% endblock %}"""


def _flask_login_html() -> str:
    return """{% extends 'base.html' %}
{% block title %}Login{% endblock %}
{% block content %}
<section class="auth-section">
  <div class="auth-card">
    <h2>Login</h2>
    <form method="POST">
      <div class="form-group"><label>Username</label><input name="username" type="text" required/></div>
      <div class="form-group"><label>Password</label><input name="password" type="password" required/></div>
      <button type="submit" class="btn-primary" style="width:100%">Login</button>
    </form>
    <p class="auth-switch">No account? <a href="{{ url_for('signup') }}">Sign up</a></p>
  </div>
</section>
{% endblock %}"""


def _flask_signup_html() -> str:
    return """{% extends 'base.html' %}
{% block title %}Sign Up{% endblock %}
{% block content %}
<section class="auth-section">
  <div class="auth-card">
    <h2>Create Account</h2>
    <form method="POST">
      <div class="form-group"><label>Username</label><input name="username" type="text" required/></div>
      <div class="form-group"><label>Password</label><input name="password" type="password" required/></div>
      <button type="submit" class="btn-primary" style="width:100%">Sign Up</button>
    </form>
    <p class="auth-switch">Have an account? <a href="{{ url_for('login') }}">Login</a></p>
  </div>
</section>
{% endblock %}"""


def _flask_extra_css() -> str:
    return """
/* Auth pages */
.auth-section{min-height:80vh;display:flex;align-items:center;justify-content:center;padding:2rem}
.auth-card{background:#fff;padding:2.5rem;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.1);width:100%;max-width:420px}
.auth-card h2{text-align:center;margin-bottom:1.5rem;color:var(--primary)}
.auth-card .form-group{margin-bottom:1rem}
.auth-card label{display:block;margin-bottom:.4rem;font-size:.9rem;color:#555}
.auth-card input{width:100%;padding:.8rem 1rem;border:1px solid #ddd;border-radius:8px;font-size:1rem}
.auth-card input:focus{outline:none;border-color:var(--primary)}
.auth-switch{text-align:center;margin-top:1rem;color:#666}
.auth-switch a{color:var(--primary);font-weight:600}
.flash{padding:.75rem 1.5rem;text-align:center;font-weight:500}
.flash-success{background:#d4edda;color:#155724}
.flash-error{background:#f8d7da;color:#721c24}
"""


# ─────────────────────────────────────────────────────────────────────────────
# 3. E-COMMERCE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def _gen_ecommerce(config: dict) -> dict:
    """
    Generate a FULL MULTI-VENDOR MARKETPLACE (Meesho-style).
    3 roles: Admin / Seller / Customer
    Payment split: 90% seller, 10% platform commission
    """
    site_name = _c(config, "site_name", "MarketHub")
    primary   = _c(config, "primary_color", "#e91e63")
    secondary = _c(config, "secondary_color", "#ff5722")
    font      = _c(config, "font", "Poppins")

    return {
        # ── Core app ──────────────────────────────────────────────────────────
        "app.py":                                        _mv_app_py(site_name),
        "requirements.txt":                              "Flask==3.0.0\nWerkzeug==3.0.1\n",
        "README.txt":                                    _readme_marketplace(site_name),

        # ── Static assets ─────────────────────────────────────────────────────
        "static/css/style.css":                          _base_css(primary, secondary, font) + _mv_css(),
        "static/js/script.js":                           _base_js(),
        "static/uploads/.gitkeep":                       "",

        # ── Shared templates ──────────────────────────────────────────────────
        "templates/base.html":                           _mv_base_html(site_name, font),
        "templates/auth/login.html":                     _mv_login_html(),
        "templates/auth/signup.html":                    _mv_signup_html(),
        "templates/errors/403.html":                     _mv_403_html(site_name),
        "templates/errors/404.html":                     _mv_404_html(site_name),

        # ── Customer-facing templates ─────────────────────────────────────────
        "templates/customer/index.html":                 _mv_storefront_html(),
        "templates/customer/product.html":               _mv_product_detail_html(),
        "templates/customer/cart.html":                  _mv_cart_html(),
        "templates/customer/checkout.html":              _mv_checkout_html(),
        "templates/customer/orders.html":                _mv_customer_orders_html(),
        "templates/customer/order_detail.html":          _mv_order_detail_html(),
        "templates/customer/seller_store.html":          _mv_seller_store_html(),
        "templates/customer/notifications.html":         _mv_notifications_html(),

        # ── New public pages ──────────────────────────────────────────────────
        "templates/customer/about.html":                 _mv_about_html(site_name),
        "templates/customer/deals.html":                 _mv_deals_html(),
        "templates/customer/new_arrivals.html":          _mv_new_arrivals_html(),
        "templates/customer/become_supplier.html":       _mv_become_supplier_html(site_name),

        # ── New auth templates ────────────────────────────────────────────────
        "templates/auth/otp_request.html":               _mv_otp_request_html(),
        "templates/auth/otp_verify.html":                _mv_otp_verify_html(),

        # ── Seller templates ──────────────────────────────────────────────────
        "templates/seller/dashboard.html":               _mv_seller_dashboard_html(),
        "templates/seller/product_form.html":            _mv_seller_product_form_html(),
        "templates/seller/orders.html":                  _mv_seller_orders_html(),
        "templates/seller/earnings.html":                _mv_seller_earnings_html(),
        "templates/seller/shop_profile.html":            _mv_seller_shop_profile_html(),
        "templates/seller/notifications.html":           _mv_notifications_html(),

        # ── New seller templates ──────────────────────────────────────────────
        "templates/seller/inventory.html":               _mv_seller_inventory_html(),
        "templates/seller/shipments.html":               _mv_seller_shipments_html(),
        "templates/seller/returns.html":                 _mv_seller_returns_html(),
        "templates/seller/support.html":                 _mv_seller_support_html(),

        # ── Admin templates ───────────────────────────────────────────────────
        "templates/admin/dashboard.html":                _mv_admin_dashboard_html(),
        "templates/admin/users.html":                    _mv_admin_users_html(),
        "templates/admin/sellers.html":                  _mv_admin_sellers_html(),
        "templates/admin/products.html":                 _mv_admin_products_html(),
        "templates/admin/orders.html":                   _mv_admin_orders_html(),
        "templates/admin/earnings.html":                 _mv_admin_earnings_html(),
        "templates/admin/coupons.html":                  _mv_admin_coupons_html(),
        "templates/admin/withdrawals.html":              _mv_admin_withdrawals_html(),
        "templates/admin/reviews.html":                  _mv_admin_reviews_html(),

        # ── New admin templates ───────────────────────────────────────────────
        "templates/admin/kyc.html":                      _mv_admin_kyc_html(),
        "templates/admin/disputes.html":                 _mv_admin_disputes_html(),
        "templates/admin/banners.html":                  _mv_admin_banners_html(),
        "templates/admin/newsletter.html":               _mv_admin_newsletter_html(),
    }


def _mv_app_py(site_name: str) -> str:
    """Return the complete single-file multi-vendor marketplace app.py."""
    return _MV_APP_PY_BODY.replace("__SITE_NAME__", site_name)


# ── Complete multi-vendor app.py body ─────────────────────────────────────────
_MV_APP_PY_BODY = '''"""
app.py — __SITE_NAME__ Multi-Vendor Marketplace
Generated by WebGen Platform
Roles: Admin / Seller / Customer
Features: shop pages, reviews, coupons, notifications,
          wallet/withdrawals, order timeline, payment split 90/10
"""
import os, re, uuid, sqlite3
from datetime import datetime
from collections import defaultdict
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify, abort)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get(\'SECRET_KEY\', \'shopwave-secret-2025\')

UPLOAD_FOLDER = os.path.join(\'static\', \'uploads\')
ALLOWED_EXTENSIONS = {\'png\', \'jpg\', \'jpeg\', \'gif\', \'webp\'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config[\'UPLOAD_FOLDER\'] = UPLOAD_FOLDER

DB_PATH = os.path.join(os.path.dirname(__file__), \'database.db\')
SELLER_SHARE   = 0.90
PLATFORM_SHARE = 0.10
CATEGORIES = [\'Fashion\',\'Electronics\',\'Home & Kitchen\',\'Beauty\',\'Sports\',\'Books\',\'Toys\',\'General\']
STATUSES   = [\'pending\',\'paid\',\'confirmed\',\'shipped\',\'out_for_delivery\',\'delivered\',\'cancelled\']


# ── Database ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT \'customer\',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS seller_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            shop_name TEXT UNIQUE NOT NULL,
            shop_slug TEXT UNIQUE NOT NULL,
            logo TEXT DEFAULT \'default.png\',
            description TEXT DEFAULT \'\',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            category TEXT DEFAULT \'General\',
            image TEXT DEFAULT \'default.png\',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            payment_ref TEXT,
            status TEXT DEFAULT \'paid\',
            address TEXT,
            coupon_code TEXT,
            discount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            seller_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            price REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS order_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            note TEXT DEFAULT \'\',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS seller_earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS platform_earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL UNIQUE,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT DEFAULT \'\',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(product_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            discount_type TEXT DEFAULT \'percent\',
            discount_value REAL NOT NULL,
            min_order REAL DEFAULT 0,
            max_uses INTEGER DEFAULT 0,
            used_count INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            link TEXT DEFAULT \'\',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS withdrawal_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            upi_id TEXT DEFAULT \'\',
            status TEXT DEFAULT \'pending\',
            note TEXT DEFAULT \'\',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ALTER TABLE users ADD COLUMN mobile TEXT;
        ALTER TABLE users ADD COLUMN referral_code TEXT;
        ALTER TABLE users ADD COLUMN kyc_status TEXT DEFAULT \'none\';
        ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1;
        ALTER TABLE products ADD COLUMN slug TEXT;
        ALTER TABLE products ADD COLUMN discount_percent REAL DEFAULT 0;
        ALTER TABLE products ADD COLUMN images TEXT DEFAULT \'\';
        ALTER TABLE products ADD COLUMN mrp REAL DEFAULT 0;
        ALTER TABLE products ADD COLUMN status TEXT DEFAULT \'active\';
        ALTER TABLE cart_items ADD COLUMN variant_id INTEGER;
        CREATE TABLE IF NOT EXISTS banners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            image TEXT NOT NULL,
            link TEXT DEFAULT \'\',
            position INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS newsletter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS product_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            size TEXT DEFAULT \'\',
            color TEXT DEFAULT \'\',
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            sku TEXT DEFAULT \'\',
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT NOT NULL,
            code TEXT NOT NULL,
            is_used INTEGER DEFAULT 0,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS shipping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER UNIQUE NOT NULL,
            carrier TEXT DEFAULT \'\',
            tracking_number TEXT DEFAULT \'\',
            status TEXT DEFAULT \'pending\',
            estimated_delivery TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT \'requested\',
            refund_amount REAL DEFAULT 0,
            admin_note TEXT DEFAULT \'\',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER UNIQUE NOT NULL,
            reward_given INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT \'open\',
            priority TEXT DEFAULT \'normal\',
            admin_reply TEXT DEFAULT \'\',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    if not conn.execute("SELECT id FROM users WHERE email=\'admin@marketplace.com\'").fetchone():
        conn.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                     (\'Admin\',\'admin@marketplace.com\',generate_password_hash(\'admin123\'),\'admin\'))
    conn.commit()
    conn.close()

def _slugify(text):
    text = text.lower().strip()
    text = re.sub(r\'[^\\w\\s-]\', \'\', text)
    text = re.sub(r\'[\\s_-]+\', \'-\', text)
    return text or \'shop\'

def allowed_file(fn):
    return \'.\' in fn and fn.rsplit(\'.\',1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit(\'.\',1)[1].lower()
        fn  = uuid.uuid4().hex + \'.\' + ext
        file.save(os.path.join(app.config[\'UPLOAD_FOLDER\'], fn))
        return fn
    return \'default.png\'

def notify(conn, user_id, message, link=\'\'):
    conn.execute(\'INSERT INTO notifications (user_id,message,link) VALUES (?,?,?)\',
                 (user_id, message, link))

def record_timeline(conn, order_id, status, note=\'\'):
    conn.execute(\'INSERT INTO order_timeline (order_id,status,note) VALUES (?,?,?)\',
                 (order_id, status, note))


# ── Decorators ────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def dec(*a,**kw):
        if \'user_id\' not in session:
            flash(\'Please login first.\',\'warning\')
            return redirect(url_for(\'login\'))
        return f(*a,**kw)
    return dec

def seller_required(f):
    @wraps(f)
    def dec(*a,**kw):
        if session.get(\'role\') not in (\'seller\',\'admin\'):
            flash(\'Seller access required.\',\'error\')
            return redirect(url_for(\'index\'))
        return f(*a,**kw)
    return dec

def admin_required(f):
    @wraps(f)
    def dec(*a,**kw):
        if session.get(\'role\') != \'admin\':
            flash(\'Admin access required.\',\'error\')
            return redirect(url_for(\'index\'))
        return f(*a,**kw)
    return dec

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route(\'/signup\', methods=[\'GET\',\'POST\'])
def signup():
    if request.method == \'POST\':
        name      = request.form[\'name\'].strip()
        email     = request.form[\'email\'].strip().lower()
        pw        = generate_password_hash(request.form[\'password\'])
        role      = request.form.get(\'role\',\'customer\')
        shop_name = request.form.get(\'shop_name\',\'\').strip()
        if role not in (\'seller\',\'customer\'): role = \'customer\'
        if role == \'seller\' and not shop_name:
            flash(\'Please enter your shop name.\',\'error\')
            return redirect(url_for(\'signup\'))
        conn = get_db()
        if conn.execute(\'SELECT id FROM users WHERE email=?\', (email,)).fetchone():
            flash(\'Email already registered.\',\'error\'); conn.close()
            return redirect(url_for(\'signup\'))
        if role == \'seller\':
            slug = _slugify(shop_name)
            if conn.execute(\'SELECT id FROM seller_profiles WHERE shop_slug=?\', (slug,)).fetchone():
                flash(\'Shop name already taken.\',\'error\'); conn.close()
                return redirect(url_for(\'signup\'))
        conn.execute(\'INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)\', (name,email,pw,role))
        uid = conn.execute(\'SELECT last_insert_rowid()\').fetchone()[0]
        if role == \'seller\':
            slug = _slugify(shop_name)
            conn.execute(\'INSERT INTO seller_profiles (user_id,shop_name,shop_slug) VALUES (?,?,?)\',
                         (uid, shop_name, slug))
        conn.commit(); conn.close()
        flash(\'Account created! Please login.\',\'success\')
        return redirect(url_for(\'login\'))
    return render_template(\'auth/signup.html\')

@app.route(\'/login\', methods=[\'GET\',\'POST\'])
def login():
    if request.method == \'POST\':
        email = request.form[\'email\'].strip().lower()
        pw    = request.form[\'password\']
        conn  = get_db()
        user  = conn.execute(\'SELECT * FROM users WHERE email=?\', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user[\'password\'], pw):
            session[\'user_id\']   = user[\'id\']
            session[\'user_name\'] = user[\'name\']
            session[\'role\']      = user[\'role\']
            if user[\'role\'] == \'admin\':   return redirect(url_for(\'admin_dashboard\'))
            if user[\'role\'] == \'seller\':  return redirect(url_for(\'seller_dashboard\'))
            return redirect(url_for(\'index\'))
        flash(\'Invalid email or password.\',\'error\')
    return render_template(\'auth/login.html\')

@app.route(\'/logout\')
def logout():
    session.clear()
    return redirect(url_for(\'login\'))


# ── Customer storefront ───────────────────────────────────────────────────────

@app.route(\'/\')
def index():
    q=request.args.get(\'q\',\'\').strip(); cat=request.args.get(\'category\',\'\')
    minp=request.args.get(\'min_price\',\'\'); maxp=request.args.get(\'max_price\',\'\')
    sort=request.args.get(\'sort\',\'newest\')
    conn=get_db()
    sql=(\'SELECT p.*,u.name as seller_name,\'
         \'COALESCE(sp.shop_name,u.name) as shop_name,\'
         \'COALESCE(sp.shop_slug,"") as shop_slug,\'
         \'COALESCE(AVG(r.rating),0) as avg_rating,\'
         \'COUNT(r.id) as review_count\'
         \' FROM products p\'
         \' JOIN users u ON p.seller_id=u.id\'
         \' LEFT JOIN seller_profiles sp ON u.id=sp.user_id\'
         \' LEFT JOIN reviews r ON p.id=r.product_id\'
         \' WHERE p.stock>0\')
    args=[]
    if q:    sql+=\' AND p.name LIKE ?\'; args.append(f\'%{q}%\')
    if cat:  sql+=\' AND p.category=?\'; args.append(cat)
    if minp: sql+=\' AND p.price>=?\'; args.append(float(minp))
    if maxp: sql+=\' AND p.price<=?\'; args.append(float(maxp))
    sql+=\' GROUP BY p.id\'
    sql+=({\'price_asc\':\' ORDER BY p.price ASC\',\'price_desc\':\' ORDER BY p.price DESC\',
           \'rating\':\' ORDER BY avg_rating DESC\'}).get(sort,\' ORDER BY p.created_at DESC\')
    products=conn.execute(sql,args).fetchall()
    categories=[r[0] for r in conn.execute(\'SELECT DISTINCT category FROM products\').fetchall()]
    conn.close()
    return render_template(\'customer/index.html\',products=products,categories=categories,
                           q=q,selected_cat=cat,min_price=minp,max_price=maxp,sort=sort)

@app.route(\'/product/<int:pid>\')
def product_detail(pid):
    conn=get_db()
    p=conn.execute(
        (\'SELECT p.*,u.name as seller_name,\'
         \'COALESCE(sp.shop_name,u.name) as shop_name,\'
         \'COALESCE(sp.shop_slug,"") as shop_slug,\'
         \'COALESCE(AVG(r.rating),0) as avg_rating,\'
         \'COUNT(r.id) as review_count\'
         \' FROM products p JOIN users u ON p.seller_id=u.id\'
         \' LEFT JOIN seller_profiles sp ON u.id=sp.user_id\'
         \' LEFT JOIN reviews r ON p.id=r.product_id\'
         \' WHERE p.id=? GROUP BY p.id\'), (pid,)).fetchone()
    if not p: conn.close(); return render_template(\'errors/404.html\'),404
    related=conn.execute(
        \'SELECT * FROM products WHERE category=? AND id!=? AND stock>0 LIMIT 4\',
        (p[\'category\'],pid)).fetchall()
    reviews=conn.execute(
        (\'SELECT r.*,u.name as reviewer_name FROM reviews r\'
         \' JOIN users u ON r.user_id=u.id WHERE r.product_id=?\'
         \' ORDER BY r.created_at DESC\'), (pid,)).fetchall()
    user_review=None
    if session.get(\'user_id\'):
        user_review=conn.execute(
            \'SELECT * FROM reviews WHERE product_id=? AND user_id=?\',
            (pid,session[\'user_id\'])).fetchone()
    conn.close()
    return render_template(\'customer/product.html\',product=p,related=related,
                           reviews=reviews,user_review=user_review)

@app.route(\'/store/<shop_slug>\')
def seller_store(shop_slug):
    conn=get_db()
    sp=conn.execute(
        \'SELECT sp.*,u.name as seller_name FROM seller_profiles sp\'
        \' JOIN users u ON sp.user_id=u.id WHERE sp.shop_slug=?\',
        (shop_slug,)).fetchone()
    if not sp: conn.close(); return render_template(\'errors/404.html\'),404
    q=request.args.get(\'q\',\'\').strip(); cat=request.args.get(\'category\',\'\')
    sql=\'SELECT * FROM products WHERE seller_id=? AND stock>0\'
    args=[sp[\'user_id\']]
    if q:   sql+=\' AND name LIKE ?\'; args.append(f\'%{q}%\')
    if cat: sql+=\' AND category=?\'; args.append(cat)
    sql+=\' ORDER BY created_at DESC\'
    products=conn.execute(sql,args).fetchall()
    cats=[r[0] for r in conn.execute(
        \'SELECT DISTINCT category FROM products WHERE seller_id=?\',
        (sp[\'user_id\'],)).fetchall()]
    conn.close()
    return render_template(\'customer/seller_store.html\',profile=sp,products=products,
                           categories=cats,q=q,selected_cat=cat)

@app.route(\'/product/<int:pid>/review\', methods=[\'POST\'])
@login_required
def submit_review(pid):
    rating=int(request.form.get(\'rating\',5))
    comment=request.form.get(\'comment\',\'\').strip()
    if not 1<=rating<=5:
        flash(\'Rating must be 1-5.\',\'error\')
        return redirect(url_for(\'product_detail\',pid=pid))
    conn=get_db()
    existing=conn.execute(
        \'SELECT id FROM reviews WHERE product_id=? AND user_id=?\',
        (pid,session[\'user_id\'])).fetchone()
    if existing:
        conn.execute(\'UPDATE reviews SET rating=?,comment=? WHERE id=?\',
                     (rating,comment,existing[\'id\']))
        flash(\'Review updated!\',\'success\')
    else:
        conn.execute(
            \'INSERT INTO reviews (product_id,user_id,rating,comment) VALUES (?,?,?,?)\',
            (pid,session[\'user_id\'],rating,comment))
        flash(\'Review submitted!\',\'success\')
    conn.commit(); conn.close()
    return redirect(url_for(\'product_detail\',pid=pid))

@app.route(\'/product/<int:pid>/review/delete\', methods=[\'POST\'])
@login_required
def delete_review(pid):
    conn=get_db()
    conn.execute(\'DELETE FROM reviews WHERE product_id=? AND user_id=?\',
                 (pid,session[\'user_id\']))
    conn.commit(); conn.close()
    flash(\'Review deleted.\',\'info\')
    return redirect(url_for(\'product_detail\',pid=pid))


# ── Cart ──────────────────────────────────────────────────────────────────────

@app.route(\'/cart\')
@login_required
def cart():
    conn=get_db()
    items=conn.execute(
        (\'SELECT ci.id,ci.quantity,p.name,p.price,p.image,p.stock,p.id as pid\'
         \' FROM cart_items ci JOIN products p ON ci.product_id=p.id WHERE ci.user_id=?\'),
        (session[\'user_id\'],)).fetchall()
    total=sum(i[\'price\']*i[\'quantity\'] for i in items)
    conn.close()
    return render_template(\'customer/cart.html\',items=items,total=total)

@app.route(\'/cart/add/<int:pid>\', methods=[\'POST\'])
@login_required
def add_to_cart(pid):
    qty=max(1,int(request.form.get(\'quantity\',1)))
    conn=get_db()
    p=conn.execute(\'SELECT * FROM products WHERE id=?\', (pid,)).fetchone()
    if not p or p[\'stock\']<1:
        flash(\'Product unavailable.\',\'error\'); conn.close()
        return redirect(url_for(\'index\'))
    ex=conn.execute(
        \'SELECT * FROM cart_items WHERE user_id=? AND product_id=?\',
        (session[\'user_id\'],pid)).fetchone()
    if ex:
        conn.execute(\'UPDATE cart_items SET quantity=? WHERE id=?\',
                     (min(ex[\'quantity\']+qty,p[\'stock\']),ex[\'id\']))
    else:
        conn.execute(
            \'INSERT INTO cart_items (user_id,product_id,quantity) VALUES (?,?,?)\',
            (session[\'user_id\'],pid,min(qty,p[\'stock\'])))
    conn.commit(); conn.close()
    flash(f\'"{p["name"]}" added to cart.\',\'success\')
    return redirect(request.referrer or url_for(\'cart\'))

@app.route(\'/cart/update/<int:iid>\', methods=[\'POST\'])
@login_required
def update_cart(iid):
    qty=int(request.form.get(\'quantity\',1)); conn=get_db()
    if qty<1:
        conn.execute(\'DELETE FROM cart_items WHERE id=? AND user_id=?\',
                     (iid,session[\'user_id\']))
    else:
        conn.execute(\'UPDATE cart_items SET quantity=? WHERE id=? AND user_id=?\',
                     (qty,iid,session[\'user_id\']))
    conn.commit(); conn.close()
    return redirect(url_for(\'cart\'))

@app.route(\'/cart/remove/<int:iid>\', methods=[\'POST\'])
@login_required
def remove_from_cart(iid):
    conn=get_db()
    conn.execute(\'DELETE FROM cart_items WHERE id=? AND user_id=?\',
                 (iid,session[\'user_id\']))
    conn.commit(); conn.close()
    flash(\'Item removed.\',\'info\')
    return redirect(url_for(\'cart\'))

# ── Coupon validation ─────────────────────────────────────────────────────────

@app.route(\'/coupon/validate\', methods=[\'POST\'])
@login_required
def validate_coupon():
    code=request.form.get(\'code\',\'\').strip().upper()
    total=float(request.form.get(\'total\',0))
    conn=get_db()
    c=conn.execute(\'SELECT * FROM coupons WHERE code=?\', (code,)).fetchone()
    conn.close()
    if not c: return jsonify(ok=False,message=\'Coupon not found.\')
    if not c[\'is_active\']: return jsonify(ok=False,message=\'Coupon is inactive.\')
    if c[\'expires_at\'] and datetime.utcnow().isoformat()>c[\'expires_at\']:
        return jsonify(ok=False,message=\'Coupon has expired.\')
    if c[\'max_uses\']>0 and c[\'used_count\']>=c[\'max_uses\']:
        return jsonify(ok=False,message=\'Usage limit reached.\')
    if total<c[\'min_order\']:
        return jsonify(ok=False,message=f\'Min order ${c["min_order"]:.0f} required.\')
    if c[\'discount_type\']==\'percent\':
        discount=round(total*c[\'discount_value\']/100,2)
        label=f\'{c["discount_value"]:.0f}% off\'
    else:
        discount=min(c[\'discount_value\'],total)
        label=f\'${c["discount_value"]:.0f} off\'
    return jsonify(ok=True,discount=discount,label=label,new_total=round(total-discount,2))

# ── Checkout ──────────────────────────────────────────────────────────────────

@app.route(\'/checkout\', methods=[\'GET\',\'POST\'])
@login_required
def checkout():
    conn=get_db()
    items=conn.execute(
        (\'SELECT ci.id,ci.quantity,p.id as pid,p.name,p.price,p.stock,p.seller_id,p.image\'
         \' FROM cart_items ci JOIN products p ON ci.product_id=p.id WHERE ci.user_id=?\'),
        (session[\'user_id\'],)).fetchall()
    if not items:
        flash(\'Your cart is empty.\',\'warning\'); conn.close()
        return redirect(url_for(\'cart\'))
    raw_total=sum(i[\'price\']*i[\'quantity\'] for i in items)
    if request.method==\'POST\':
        address=request.form.get(\'address\',\'\').strip()
        coupon_code=request.form.get(\'coupon_code\',\'\').strip().upper()
        if not address:
            flash(\'Please enter a delivery address.\',\'error\')
            conn.close(); return redirect(url_for(\'checkout\'))
        discount=0.0; coupon=None
        if coupon_code:
            coupon=conn.execute(\'SELECT * FROM coupons WHERE code=? AND is_active=1\',
                                (coupon_code,)).fetchone()
            if coupon:
                if coupon[\'discount_type\']==\'percent\':
                    discount=round(raw_total*coupon[\'discount_value\']/100,2)
                else:
                    discount=min(coupon[\'discount_value\'],raw_total)
                conn.execute(\'UPDATE coupons SET used_count=used_count+1 WHERE id=?\',
                             (coupon[\'id\'],))
        final_total=max(0.0,round(raw_total-discount,2))
        ref=\'PAY-\'+uuid.uuid4().hex[:10].upper()
        conn.execute(
            (\'INSERT INTO orders (customer_id,total_price,payment_ref,status,address,coupon_code,discount)\'
             \' VALUES (?,?,?,?,?,?,?)\'),
            (session[\'user_id\'],final_total,ref,\'paid\',address,
             coupon[\'code\'] if coupon and discount>0 else None,discount))
        oid=conn.execute(\'SELECT last_insert_rowid()\').fetchone()[0]
        seller_totals=defaultdict(float)
        for i in items:
            conn.execute(
                (\'INSERT INTO order_items (order_id,product_id,seller_id,quantity,price)\'
                 \' VALUES (?,?,?,?,?)\'),
                (oid,i[\'pid\'],i[\'seller_id\'],i[\'quantity\'],i[\'price\']))
            conn.execute(\'UPDATE products SET stock=MAX(0,stock-?) WHERE id=?\',
                         (i[\'quantity\'],i[\'pid\']))
            seller_totals[i[\'seller_id\']]+=i[\'price\']*i[\'quantity\']
        ratio=discount/raw_total if raw_total>0 else 0
        for sid,amt in seller_totals.items():
            net=amt*(1-ratio)
            conn.execute(
                \'INSERT INTO seller_earnings (seller_id,order_id,amount) VALUES (?,?,?)\',
                (sid,oid,round(net*SELLER_SHARE,2)))
        conn.execute(
            \'INSERT INTO platform_earnings (order_id,amount) VALUES (?,?)\',
            (oid,round(final_total*PLATFORM_SHARE,2)))
        record_timeline(conn,oid,\'paid\',f\'Order placed. Ref: {ref}\')
        notify(conn,session[\'user_id\'],f\'Order #{oid} placed! Ref: {ref}\',f\'/orders/{oid}\')
        for sid in seller_totals:
            notify(conn,sid,f\'New order #{oid} received.\',\'/seller/orders\')
        conn.execute(\'DELETE FROM cart_items WHERE user_id=?\', (session[\'user_id\'],))
        conn.commit(); conn.close()
        flash(f\'Order placed! Ref: {ref}\',\'success\')
        return redirect(url_for(\'order_detail\',oid=oid))
    conn.close()
    return render_template(\'customer/checkout.html\',items=items,total=raw_total)


# ── Orders ────────────────────────────────────────────────────────────────────

@app.route(\'/orders\')
@login_required
def my_orders():
    conn=get_db()
    orders=conn.execute(
        \'SELECT * FROM orders WHERE customer_id=? ORDER BY created_at DESC\',
        (session[\'user_id\'],)).fetchall()
    conn.close()
    return render_template(\'customer/orders.html\',orders=orders)

@app.route(\'/orders/<int:oid>\')
@login_required
def order_detail(oid):
    conn=get_db()
    order=conn.execute(\'SELECT * FROM orders WHERE id=?\', (oid,)).fetchone()
    if not order or (order[\'customer_id\']!=session[\'user_id\'] and session.get(\'role\')!=\'admin\'):
        conn.close(); return render_template(\'errors/403.html\'),403
    items=conn.execute(
        (\'SELECT oi.*,p.name,p.image FROM order_items oi\'
         \' JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?\'), (oid,)).fetchall()
    timeline=conn.execute(
        \'SELECT * FROM order_timeline WHERE order_id=? ORDER BY created_at\',
        (oid,)).fetchall()
    conn.close()
    return render_template(\'customer/order_detail.html\',order=order,items=items,timeline=timeline)

@app.route(\'/notifications\')
@login_required
def notifications():
    conn=get_db()
    notifs=conn.execute(
        \'SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC\',
        (session[\'user_id\'],)).fetchall()
    conn.execute(\'UPDATE notifications SET is_read=1 WHERE user_id=?\', (session[\'user_id\'],))
    conn.commit(); conn.close()
    return render_template(\'customer/notifications.html\',notifications=notifs)


# ── Seller ────────────────────────────────────────────────────────────────────

@app.route(\'/seller/dashboard\')
@login_required
@seller_required
def seller_dashboard():
    conn=get_db()
    products=conn.execute(
        \'SELECT * FROM products WHERE seller_id=? ORDER BY created_at DESC\',
        (session[\'user_id\'],)).fetchall()
    pids=[p[\'id\'] for p in products]
    total_earned=conn.execute(
        \'SELECT COALESCE(SUM(amount),0) FROM seller_earnings WHERE seller_id=?\',
        (session[\'user_id\'],)).fetchone()[0]
    withdrawn=conn.execute(
        \'SELECT COALESCE(SUM(amount),0) FROM withdrawal_requests WHERE seller_id=? AND status="approved"\',
        (session[\'user_id\'],)).fetchone()[0]
    total_orders=conn.execute(
        \'SELECT COUNT(DISTINCT order_id) FROM seller_earnings WHERE seller_id=?\',
        (session[\'user_id\'],)).fetchone()[0]
    recent=conn.execute(
        (\'SELECT o.id,o.created_at,o.status,o.total_price,u.name as customer_name\'
         \' FROM orders o JOIN users u ON o.customer_id=u.id\'
         \' WHERE o.id IN (SELECT DISTINCT order_id FROM order_items WHERE seller_id=?)\'
         \' ORDER BY o.created_at DESC LIMIT 5\'), (session[\'user_id\'],)).fetchall()
    profile=conn.execute(
        \'SELECT * FROM seller_profiles WHERE user_id=?\',
        (session[\'user_id\'],)).fetchone()
    unread=conn.execute(
        \'SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0\',
        (session[\'user_id\'],)).fetchone()[0]
    conn.close()
    return render_template(\'seller/dashboard.html\',products=products,
                           total_earned=total_earned,total_orders=total_orders,
                           wallet_balance=round(total_earned-withdrawn,2),
                           recent_orders=recent,profile=profile,unread=unread)

@app.route(\'/seller/product/add\', methods=[\'GET\',\'POST\'])
@login_required
@seller_required
def seller_add_product():
    if request.method==\'POST\':
        img=save_image(request.files.get(\'image\'))
        conn=get_db()
        conn.execute(
            (\'INSERT INTO products (seller_id,name,description,price,stock,category,image)\'
             \' VALUES (?,?,?,?,?,?,?)\'),
            (session[\'user_id\'],request.form[\'name\'].strip(),
             request.form.get(\'description\',\'\').strip(),
             float(request.form[\'price\']),int(request.form[\'stock\']),
             request.form.get(\'category\',\'General\'),img))
        conn.commit(); conn.close()
        flash(\'Product added!\',\'success\')
        return redirect(url_for(\'seller_dashboard\'))
    return render_template(\'seller/product_form.html\',product=None,categories=CATEGORIES)

@app.route(\'/seller/product/<int:pid>/edit\', methods=[\'GET\',\'POST\'])
@login_required
@seller_required
def seller_edit_product(pid):
    conn=get_db()
    p=conn.execute(\'SELECT * FROM products WHERE id=? AND seller_id=?\',
                   (pid,session[\'user_id\'])).fetchone()
    if not p:
        conn.close(); flash(\'Product not found.\',\'error\')
        return redirect(url_for(\'seller_dashboard\'))
    if request.method==\'POST\':
        img=save_image(request.files.get(\'image\'))
        if img==\'default.png\' and p[\'image\']: img=p[\'image\']
        conn.execute(
            (\'UPDATE products SET name=?,description=?,price=?,stock=?,category=?,image=?\'
             \' WHERE id=?\'),
            (request.form[\'name\'].strip(),request.form.get(\'description\',\'\').strip(),
             float(request.form[\'price\']),int(request.form[\'stock\']),
             request.form.get(\'category\',\'General\'),img,pid))
        conn.commit(); conn.close()
        flash(\'Product updated!\',\'success\')
        return redirect(url_for(\'seller_dashboard\'))
    conn.close()
    return render_template(\'seller/product_form.html\',product=p,categories=CATEGORIES)

@app.route(\'/seller/product/<int:pid>/delete\', methods=[\'POST\'])
@login_required
@seller_required
def seller_delete_product(pid):
    conn=get_db()
    conn.execute(\'DELETE FROM products WHERE id=? AND seller_id=?\',
                 (pid,session[\'user_id\']))
    conn.commit(); conn.close()
    flash(\'Product deleted.\',\'info\')
    return redirect(url_for(\'seller_dashboard\'))

@app.route(\'/seller/orders\')
@login_required
@seller_required
def seller_orders():
    conn=get_db()
    orders=conn.execute(
        (\'SELECT DISTINCT o.*,u.name as customer_name FROM orders o\'
         \' JOIN users u ON o.customer_id=u.id\'
         \' WHERE o.id IN (SELECT DISTINCT order_id FROM order_items WHERE seller_id=?)\'
         \' ORDER BY o.created_at DESC\'), (session[\'user_id\'],)).fetchall()
    pids=[r[0] for r in conn.execute(
        \'SELECT id FROM products WHERE seller_id=?\', (session[\'user_id\'],)).fetchall()]
    conn.close()
    return render_template(\'seller/orders.html\',orders=orders,pids=pids,statuses=STATUSES)

@app.route(\'/seller/orders/<int:oid>/status\', methods=[\'POST\'])
@login_required
@seller_required
def seller_update_status(oid):
    new_status=request.form.get(\'status\',\'pending\')
    if new_status not in STATUSES:
        flash(\'Invalid status.\',\'error\')
        return redirect(url_for(\'seller_orders\'))
    conn=get_db()
    conn.execute(\'UPDATE orders SET status=? WHERE id=?\', (new_status,oid))
    record_timeline(conn,oid,new_status,request.form.get(\'note\',\'\'))
    order=conn.execute(\'SELECT customer_id FROM orders WHERE id=?\', (oid,)).fetchone()
    if order:
        notify(conn,order[\'customer_id\'],f\'Your order #{oid} is now {new_status}.\',f\'/orders/{oid}\')
    conn.commit(); conn.close()
    flash(f\'Order #{oid} updated.\',\'success\')
    return redirect(url_for(\'seller_orders\'))

@app.route(\'/seller/earnings\')
@login_required
@seller_required
def seller_earnings():
    conn=get_db()
    rows=conn.execute(
        (\'SELECT se.*,o.payment_ref,o.total_price,u.name as customer_name\'
         \' FROM seller_earnings se JOIN orders o ON se.order_id=o.id\'
         \' JOIN users u ON o.customer_id=u.id WHERE se.seller_id=?\'
         \' ORDER BY se.created_at DESC\'), (session[\'user_id\'],)).fetchall()
    total=sum(r[\'amount\'] for r in rows)
    withdrawn=conn.execute(
        \'SELECT COALESCE(SUM(amount),0) FROM withdrawal_requests WHERE seller_id=? AND status="approved"\',
        (session[\'user_id\'],)).fetchone()[0]
    withdrawals=conn.execute(
        \'SELECT * FROM withdrawal_requests WHERE seller_id=? ORDER BY created_at DESC\',
        (session[\'user_id\'],)).fetchall()
    conn.close()
    return render_template(\'seller/earnings.html\',rows=rows,total=total,
                           wallet_balance=round(total-withdrawn,2),
                           total_orders=len(set(r[\'order_id\'] for r in rows)),
                           withdrawals=withdrawals)

@app.route(\'/seller/wallet/withdraw\', methods=[\'POST\'])
@login_required
@seller_required
def seller_withdraw():
    amount=float(request.form.get(\'amount\',0))
    upi_id=request.form.get(\'upi_id\',\'\').strip()
    conn=get_db()
    total_earned=conn.execute(
        \'SELECT COALESCE(SUM(amount),0) FROM seller_earnings WHERE seller_id=?\',
        (session[\'user_id\'],)).fetchone()[0]
    withdrawn=conn.execute(
        \'SELECT COALESCE(SUM(amount),0) FROM withdrawal_requests WHERE seller_id=? AND status="approved"\',
        (session[\'user_id\'],)).fetchone()[0]
    balance=round(total_earned-withdrawn,2)
    if amount<=0 or amount>balance:
        flash(f\'Invalid amount. Balance: ${balance:.2f}\',\'error\')
        conn.close(); return redirect(url_for(\'seller_earnings\'))
    if not upi_id:
        flash(\'Please enter UPI ID.\',\'error\')
        conn.close(); return redirect(url_for(\'seller_earnings\'))
    conn.execute(
        \'INSERT INTO withdrawal_requests (seller_id,amount,upi_id) VALUES (?,?,?)\',
        (session[\'user_id\'],amount,upi_id))
    conn.commit(); conn.close()
    flash(f\'Withdrawal request of ${amount:.2f} submitted!\',\'success\')
    return redirect(url_for(\'seller_earnings\'))

@app.route(\'/seller/profile\', methods=[\'GET\',\'POST\'])
@login_required
@seller_required
def seller_shop_profile():
    conn=get_db()
    profile=conn.execute(\'SELECT * FROM seller_profiles WHERE user_id=?\',
                         (session[\'user_id\'],)).fetchone()
    if not profile:
        conn.close(); flash(\'No shop profile found.\',\'error\')
        return redirect(url_for(\'seller_dashboard\'))
    if request.method==\'POST\':
        new_name=request.form.get(\'shop_name\',\'\').strip()
        desc=request.form.get(\'description\',\'\').strip()
        logo_f=request.files.get(\'logo\')
        if new_name and new_name!=profile[\'shop_name\']:
            slug=_slugify(new_name)
            existing=conn.execute(
                \'SELECT id FROM seller_profiles WHERE shop_slug=? AND user_id!=?\',
                (slug,session[\'user_id\'])).fetchone()
            if existing:
                flash(\'Shop name already taken.\',\'error\')
                conn.close(); return redirect(url_for(\'seller_shop_profile\'))
            conn.execute(
                \'UPDATE seller_profiles SET shop_name=?,shop_slug=? WHERE user_id=?\',
                (new_name,slug,session[\'user_id\']))
        conn.execute(\'UPDATE seller_profiles SET description=? WHERE user_id=?\',
                     (desc,session[\'user_id\']))
        if logo_f and logo_f.filename:
            logo=save_image(logo_f)
            conn.execute(\'UPDATE seller_profiles SET logo=? WHERE user_id=?\',
                         (logo,session[\'user_id\']))
        conn.commit(); conn.close()
        flash(\'Shop profile updated!\',\'success\')
        return redirect(url_for(\'seller_shop_profile\'))
    conn.close()
    return render_template(\'seller/shop_profile.html\',profile=profile)

@app.route(\'/seller/notifications\')
@login_required
@seller_required
def seller_notifications():
    conn=get_db()
    notifs=conn.execute(
        \'SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC\',
        (session[\'user_id\'],)).fetchall()
    conn.execute(\'UPDATE notifications SET is_read=1 WHERE user_id=?\', (session[\'user_id\'],))
    conn.commit(); conn.close()
    return render_template(\'seller/notifications.html\',notifications=notifs)


# ── Admin ─────────────────────────────────────────────────────────────────────

@app.route(\'/admin\')
@login_required
@admin_required
def admin_dashboard():
    conn=get_db()
    stats={
        \'users\':conn.execute(\'SELECT COUNT(*) FROM users\').fetchone()[0],
        \'sellers\':conn.execute(\'SELECT COUNT(*) FROM users WHERE role="seller"\').fetchone()[0],
        \'products\':conn.execute(\'SELECT COUNT(*) FROM products\').fetchone()[0],
        \'orders\':conn.execute(\'SELECT COUNT(*) FROM orders\').fetchone()[0],
        \'revenue\':conn.execute(\'SELECT COALESCE(SUM(total_price),0) FROM orders\').fetchone()[0],
        \'platform_income\':conn.execute(\'SELECT COALESCE(SUM(amount),0) FROM platform_earnings\').fetchone()[0],
        \'seller_payouts\':conn.execute(\'SELECT COALESCE(SUM(amount),0) FROM seller_earnings\').fetchone()[0],
        \'pending_withdrawals\':conn.execute(\'SELECT COUNT(*) FROM withdrawal_requests WHERE status="pending"\').fetchone()[0],
    }
    recent=conn.execute(
        (\'SELECT o.*,u.name as customer_name FROM orders o\'
         \' JOIN users u ON o.customer_id=u.id ORDER BY o.created_at DESC LIMIT 8\')).fetchall()
    top_products=conn.execute(
        (\'SELECT p.name,SUM(oi.quantity) as units FROM order_items oi\'
         \' JOIN products p ON oi.product_id=p.id\'
         \' GROUP BY p.id ORDER BY units DESC LIMIT 5\')).fetchall()
    top_sellers=conn.execute(
        (\'SELECT u.name,COALESCE(SUM(se.amount),0) as earned FROM users u\'
         \' LEFT JOIN seller_earnings se ON u.id=se.seller_id\'
         \' WHERE u.role="seller" GROUP BY u.id ORDER BY earned DESC LIMIT 5\')).fetchall()
    conn.close()
    return render_template(\'admin/dashboard.html\',stats=stats,recent=recent,
                           top_products=top_products,top_sellers=top_sellers)

@app.route(\'/admin/users\')
@login_required
@admin_required
def admin_users():
    role_filter=request.args.get(\'role\',\'\')
    conn=get_db()
    if role_filter:
        users=conn.execute(\'SELECT * FROM users WHERE role=? ORDER BY created_at DESC\',
                           (role_filter,)).fetchall()
    else:
        users=conn.execute(\'SELECT * FROM users ORDER BY created_at DESC\').fetchall()
    conn.close()
    return render_template(\'admin/users.html\',users=users,role_filter=role_filter)

@app.route(\'/admin/users/<int:uid>/delete\', methods=[\'POST\'])
@login_required
@admin_required
def admin_delete_user(uid):
    conn=get_db()
    u=conn.execute(\'SELECT role FROM users WHERE id=?\', (uid,)).fetchone()
    if u and u[\'role\']==\'admin\':
        flash(\'Cannot delete admin.\',\'danger\')
    else:
        conn.execute(\'DELETE FROM users WHERE id=?\', (uid,))
        conn.commit()
        flash(\'User deleted.\',\'info\')
    conn.close()
    return redirect(url_for(\'admin_users\'))

@app.route(\'/admin/sellers\')
@login_required
@admin_required
def admin_sellers():
    conn=get_db()
    sellers=conn.execute(
        (\'SELECT u.*,sp.shop_name,sp.shop_slug,sp.logo FROM users u\'
         \' LEFT JOIN seller_profiles sp ON u.id=sp.user_id\'
         \' WHERE u.role="seller" ORDER BY u.created_at DESC\')).fetchall()
    conn.close()
    return render_template(\'admin/sellers.html\',sellers=sellers)

@app.route(\'/admin/products\')
@login_required
@admin_required
def admin_products():
    conn=get_db()
    products=conn.execute(
        (\'SELECT p.*,u.name as seller_name FROM products p\'
         \' JOIN users u ON p.seller_id=u.id ORDER BY p.created_at DESC\')).fetchall()
    conn.close()
    return render_template(\'admin/products.html\',products=products)

@app.route(\'/admin/products/<int:pid>/delete\', methods=[\'POST\'])
@login_required
@admin_required
def admin_delete_product(pid):
    conn=get_db()
    conn.execute(\'DELETE FROM products WHERE id=?\', (pid,))
    conn.commit(); conn.close()
    flash(\'Product deleted.\',\'info\')
    return redirect(url_for(\'admin_products\'))

@app.route(\'/admin/orders\')
@login_required
@admin_required
def admin_orders():
    status_filter=request.args.get(\'status\',\'\')
    conn=get_db()
    if status_filter:
        orders=conn.execute(
            (\'SELECT o.*,u.name as customer_name FROM orders o\'
             \' JOIN users u ON o.customer_id=u.id WHERE o.status=?\'
             \' ORDER BY o.created_at DESC\'), (status_filter,)).fetchall()
    else:
        orders=conn.execute(
            (\'SELECT o.*,u.name as customer_name FROM orders o\'
             \' JOIN users u ON o.customer_id=u.id ORDER BY o.created_at DESC\')).fetchall()
    conn.close()
    return render_template(\'admin/orders.html\',orders=orders,
                           statuses=STATUSES,status_filter=status_filter)

@app.route(\'/admin/orders/<int:oid>/status\', methods=[\'POST\'])
@login_required
@admin_required
def admin_update_status(oid):
    new_status=request.form.get(\'status\',\'pending\')
    conn=get_db()
    conn.execute(\'UPDATE orders SET status=? WHERE id=?\', (new_status,oid))
    record_timeline(conn,oid,new_status,\'Admin updated status\')
    order=conn.execute(\'SELECT customer_id FROM orders WHERE id=?\', (oid,)).fetchone()
    if order:
        notify(conn,order[\'customer_id\'],f\'Your order #{oid} is now {new_status}.\',f\'/orders/{oid}\')
    conn.commit(); conn.close()
    flash(f\'Order #{oid} updated.\',\'success\')
    return redirect(url_for(\'admin_orders\'))

@app.route(\'/admin/earnings\')
@login_required
@admin_required
def admin_earnings():
    conn=get_db()
    rows=conn.execute(
        (\'SELECT pe.*,o.payment_ref,o.total_price,u.name as customer_name\'
         \' FROM platform_earnings pe JOIN orders o ON pe.order_id=o.id\'
         \' JOIN users u ON o.customer_id=u.id ORDER BY pe.created_at DESC\')).fetchall()
    total=sum(r[\'amount\'] for r in rows)
    seller_summary=conn.execute(
        (\'SELECT u.name,u.email,COALESCE(SUM(se.amount),0) as total\'
         \' FROM users u LEFT JOIN seller_earnings se ON u.id=se.seller_id\'
         \' WHERE u.role="seller" GROUP BY u.id ORDER BY total DESC\')).fetchall()
    conn.close()
    return render_template(\'admin/earnings.html\',rows=rows,total=total,
                           seller_summary=seller_summary)

@app.route(\'/admin/coupons\')
@login_required
@admin_required
def admin_coupons():
    conn=get_db()
    coupons=conn.execute(\'SELECT * FROM coupons ORDER BY created_at DESC\').fetchall()
    conn.close()
    return render_template(\'admin/coupons.html\',coupons=coupons)

@app.route(\'/admin/coupons/add\', methods=[\'POST\'])
@login_required
@admin_required
def admin_add_coupon():
    expires_raw=request.form.get(\'expires_at\',\'\').strip()
    conn=get_db()
    conn.execute(
        (\'INSERT INTO coupons (code,discount_type,discount_value,min_order,max_uses,expires_at)\'
         \' VALUES (?,?,?,?,?,?)\'),
        (request.form[\'code\'].strip().upper(),
         request.form.get(\'discount_type\',\'percent\'),
         float(request.form[\'discount_value\']),
         float(request.form.get(\'min_order\',0)),
         int(request.form.get(\'max_uses\',0)),
         expires_raw or None))
    conn.commit(); conn.close()
    flash(\'Coupon created!\',\'success\')
    return redirect(url_for(\'admin_coupons\'))

@app.route(\'/admin/coupons/<int:cid>/toggle\', methods=[\'POST\'])
@login_required
@admin_required
def admin_toggle_coupon(cid):
    conn=get_db()
    c=conn.execute(\'SELECT is_active FROM coupons WHERE id=?\', (cid,)).fetchone()
    if c:
        conn.execute(\'UPDATE coupons SET is_active=? WHERE id=?\', (0 if c[\'is_active\'] else 1,cid))
        conn.commit()
    conn.close()
    flash(\'Coupon toggled.\',\'info\')
    return redirect(url_for(\'admin_coupons\'))

@app.route(\'/admin/coupons/<int:cid>/delete\', methods=[\'POST\'])
@login_required
@admin_required
def admin_delete_coupon(cid):
    conn=get_db()
    conn.execute(\'DELETE FROM coupons WHERE id=?\', (cid,))
    conn.commit(); conn.close()
    flash(\'Coupon deleted.\',\'info\')
    return redirect(url_for(\'admin_coupons\'))

@app.route(\'/admin/withdrawals\')
@login_required
@admin_required
def admin_withdrawals():
    conn=get_db()
    reqs=conn.execute(
        (\'SELECT wr.*,u.name as seller_name FROM withdrawal_requests wr\'
         \' JOIN users u ON wr.seller_id=u.id ORDER BY wr.created_at DESC\')).fetchall()
    conn.close()
    return render_template(\'admin/withdrawals.html\',reqs=reqs)

@app.route(\'/admin/withdrawals/<int:rid>/action\', methods=[\'POST\'])
@login_required
@admin_required
def admin_withdrawal_action(rid):
    action=request.form.get(\'action\')
    note=request.form.get(\'note\',\'\').strip()
    if action in (\'approved\',\'rejected\'):
        conn=get_db()
        conn.execute(\'UPDATE withdrawal_requests SET status=?,note=? WHERE id=?\',
                     (action,note,rid))
        conn.commit(); conn.close()
        flash(f\'Withdrawal {action}.\',\'success\')
    return redirect(url_for(\'admin_withdrawals\'))

@app.route(\'/admin/reviews\')
@login_required
@admin_required
def admin_reviews():
    conn=get_db()
    reviews=conn.execute(
        (\'SELECT r.*,u.name as reviewer_name,p.name as product_name\'
         \' FROM reviews r JOIN users u ON r.user_id=u.id\'
         \' JOIN products p ON r.product_id=p.id ORDER BY r.created_at DESC\')).fetchall()
    conn.close()
    return render_template(\'admin/reviews.html\',reviews=reviews)

@app.route(\'/admin/reviews/<int:rid>/delete\', methods=[\'POST\'])
@login_required
@admin_required
def admin_delete_review(rid):
    conn=get_db()
    conn.execute(\'DELETE FROM reviews WHERE id=?\', (rid,))
    conn.commit(); conn.close()
    flash(\'Review deleted.\',\'info\')
    return redirect(url_for(\'admin_reviews\'))

# ── Public pages ──────────────────────────────────────────────────────────────

@app.route(\'/about/\')
def about():
    conn=get_db()
    stats={
        \'sellers\':conn.execute("SELECT COUNT(*) FROM users WHERE role=\'seller\'").fetchone()[0],
        \'products\':conn.execute(\'SELECT COUNT(*) FROM products\').fetchone()[0],
        \'orders\':conn.execute(\'SELECT COUNT(*) FROM orders\').fetchone()[0],
    }
    conn.close()
    return render_template(\'customer/about.html\',stats=stats)

@app.route(\'/deals/\')
def deals():
    conn=get_db()
    products=conn.execute(
        \'SELECT * FROM products WHERE discount_percent>20 AND stock>0 ORDER BY discount_percent DESC\'
    ).fetchall()
    conn.close()
    return render_template(\'customer/deals.html\',products=products)

@app.route(\'/new-arrivals/\')
def new_arrivals():
    conn=get_db()
    products=conn.execute(
        \'SELECT * FROM products WHERE stock>0 ORDER BY created_at DESC LIMIT 40\'
    ).fetchall()
    conn.close()
    return render_template(\'customer/new_arrivals.html\',products=products)

@app.route(\'/vendors/become-a-supplier/\')
def become_supplier():
    conn=get_db()
    stats={
        \'sellers\':conn.execute("SELECT COUNT(*) FROM users WHERE role=\'seller\'").fetchone()[0],
        \'products\':conn.execute(\'SELECT COUNT(*) FROM products\').fetchone()[0],
        \'orders\':conn.execute(\'SELECT COUNT(*) FROM orders\').fetchone()[0],
    }
    conn.close()
    return render_template(\'customer/become_supplier.html\',stats=stats)

@app.route(\'/newsletter/subscribe\', methods=[\'POST\'])
def newsletter_subscribe():
    email=request.form.get(\'email\',\'\').strip().lower()
    if not email or \'@\' not in email:
        flash(\'Please enter a valid email address.\',\'error\')
        return redirect(request.referrer or url_for(\'index\'))
    conn=get_db()
    existing=conn.execute(\'SELECT * FROM newsletter WHERE email=?\', (email,)).fetchone()
    if existing:
        if existing[\'is_active\']:
            flash(\'You\\\'re already subscribed!\',\'info\')
        else:
            conn.execute(\'UPDATE newsletter SET is_active=1 WHERE email=?\', (email,))
            conn.commit()
            flash(\'Welcome back!\',\'success\')
    else:
        conn.execute(\'INSERT INTO newsletter (email) VALUES (?)\', (email,))
        conn.commit()
        flash(\'Subscribed successfully!\',\'success\')
    conn.close()
    return redirect(request.referrer or url_for(\'index\'))

# ── OTP Auth ──────────────────────────────────────────────────────────────────

@app.route(\'/accounts/otp/request/\', methods=[\'GET\',\'POST\'])
def otp_request():
    if request.method==\'POST\':
        mobile=request.form.get(\'mobile\',\'\').strip()
        if not mobile or len(mobile)<10:
            flash(\'Please enter a valid mobile number.\',\'error\')
            return redirect(url_for(\'otp_request\'))
        conn=get_db()
        from datetime import timedelta
        one_hour_ago=(datetime.utcnow()-timedelta(hours=1)).isoformat()
        count=conn.execute(
            \'SELECT COUNT(*) FROM otp_codes WHERE mobile=? AND created_at>=?\',
            (mobile,one_hour_ago)).fetchone()[0]
        if count>=3:
            conn.close()
            flash(\'Too many OTP requests. Try again after 1 hour.\',\'error\')
            return redirect(url_for(\'otp_request\'))
        import random
        code=str(random.randint(100000,999999))
        expires=(datetime.utcnow()+timedelta(minutes=10)).isoformat()
        conn.execute(\'INSERT INTO otp_codes (mobile,code,expires_at) VALUES (?,?,?)\',
                     (mobile,code,expires))
        conn.commit(); conn.close()
        session[\'otp_mobile\']=mobile
        if app.debug:
            print(f\'[DEV OTP] {mobile}: {code}\')
        flash(f\'OTP sent to {mobile[:4]}****{mobile[-2:]}. (Dev: check console)\',\'info\')
        return redirect(url_for(\'otp_verify\'))
    return render_template(\'auth/otp_request.html\')

@app.route(\'/accounts/otp/verify/\', methods=[\'GET\',\'POST\'])
def otp_verify():
    mobile=session.get(\'otp_mobile\',\'\')
    if not mobile:
        return redirect(url_for(\'otp_request\'))
    if request.method==\'POST\':
        code=request.form.get(\'code\',\'\').strip()
        conn=get_db()
        now=datetime.utcnow().isoformat()
        record=conn.execute(
            \'SELECT * FROM otp_codes WHERE mobile=? AND code=? AND is_used=0 AND expires_at>? ORDER BY created_at DESC LIMIT 1\',
            (mobile,code,now)).fetchone()
        if not record:
            conn.close()
            flash(\'Invalid or expired OTP.\',\'error\')
            return redirect(url_for(\'otp_verify\'))
        conn.execute(\'UPDATE otp_codes SET is_used=1 WHERE id=?\', (record[\'id\'],))
        user=conn.execute(\'SELECT * FROM users WHERE mobile=?\', (mobile,)).fetchone()
        if not user:
            import secrets
            dummy_pw=generate_password_hash(secrets.token_hex(16))
            conn.execute(\'INSERT INTO users (name,email,password,role,mobile) VALUES (?,?,?,?,?)\',
                         (f\'User_{mobile[-4:]}\',f\'otp_{mobile}@noemail.local\',dummy_pw,\'customer\',mobile))
            uid=conn.execute(\'SELECT last_insert_rowid()\').fetchone()[0]
            conn.commit()
            user=conn.execute(\'SELECT * FROM users WHERE id=?\', (uid,)).fetchone()
        else:
            conn.commit()
        conn.close()
        session[\'user_id\']=user[\'id\']; session[\'user_name\']=user[\'name\']; session[\'role\']=user[\'role\']
        session.pop(\'otp_mobile\',None)
        flash(\'Logged in successfully!\',\'success\')
        if user[\'role\']==\'admin\': return redirect(url_for(\'admin_dashboard\'))
        if user[\'role\']==\'seller\': return redirect(url_for(\'seller_dashboard\'))
        return redirect(url_for(\'index\'))
    return render_template(\'auth/otp_verify.html\',mobile=mobile)

# ── Return requests ───────────────────────────────────────────────────────────

@app.route(\'/orders/<int:oid>/return\', methods=[\'POST\'])
@login_required
def request_return(oid):
    reason=request.form.get(\'reason\',\'\').strip()
    if not reason:
        flash(\'Please provide a reason for the return.\',\'error\')
        return redirect(url_for(\'order_detail\',oid=oid))
    conn=get_db()
    order=conn.execute(\'SELECT * FROM orders WHERE id=? AND customer_id=?\',
                       (oid,session[\'user_id\'])).fetchone()
    if not order or order[\'status\']!=\'delivered\':
        conn.close()
        flash(\'Return can only be requested for delivered orders.\',\'error\')
        return redirect(url_for(\'my_orders\'))
    existing=conn.execute(
        \'SELECT id FROM returns WHERE order_id=? AND status!=\\\'rejected\\\'\',
        (oid,)).fetchone()
    if existing:
        conn.close()
        flash(\'A return request already exists for this order.\',\'error\')
        return redirect(url_for(\'order_detail\',oid=oid))
    conn.execute(
        \'INSERT INTO returns (order_id,customer_id,reason) VALUES (?,?,?)\',
        (oid,session[\'user_id\'],reason))
    conn.commit(); conn.close()
    flash(\'Return request submitted. We will review it shortly.\',\'success\')
    return redirect(url_for(\'order_detail\',oid=oid))

# ── Seller inventory ──────────────────────────────────────────────────────────

@app.route(\'/seller/inventory\')
@login_required
@seller_required
def seller_inventory():
    conn=get_db()
    products=conn.execute(
        \'SELECT * FROM products WHERE seller_id=? ORDER BY name\',
        (session[\'user_id\'],)).fetchall()
    variants={}
    for p in products:
        variants[p[\'id\']]=conn.execute(
            \'SELECT * FROM product_variants WHERE product_id=?\', (p[\'id\'],)).fetchall()
    conn.close()
    return render_template(\'seller/inventory.html\',products=products,variants=variants)

@app.route(\'/seller/inventory/<int:pid>/update\', methods=[\'POST\'])
@login_required
@seller_required
def update_inventory(pid):
    stock=int(request.form.get(\'stock\',0))
    conn=get_db()
    conn.execute(\'UPDATE products SET stock=? WHERE id=? AND seller_id=?\',
                 (stock,pid,session[\'user_id\']))
    conn.commit(); conn.close()
    flash(\'Stock updated.\',\'success\')
    return redirect(url_for(\'seller_inventory\'))

# ── Seller shipments ──────────────────────────────────────────────────────────

@app.route(\'/seller/shipments\')
@login_required
@seller_required
def seller_shipments():
    conn=get_db()
    pids=[r[0] for r in conn.execute(
        \'SELECT id FROM products WHERE seller_id=?\', (session[\'user_id\'],)).fetchall()]
    if not pids:
        conn.close()
        return render_template(\'seller/shipments.html\',shipments=[])
    placeholders=\',\'.join(\'?\' for _ in pids)
    oids=[r[0] for r in conn.execute(
        f\'SELECT DISTINCT order_id FROM order_items WHERE seller_id=?\',
        (session[\'user_id\'],)).fetchall()]
    shipments=[]
    if oids:
        op=\',\'.join(\'?\' for _ in oids)
        shipments=conn.execute(
            f\'SELECT s.*,o.status as order_status FROM shipping s JOIN orders o ON s.order_id=o.id WHERE s.order_id IN ({op})\',
            oids).fetchall()
    conn.close()
    return render_template(\'seller/shipments.html\',shipments=shipments)

@app.route(\'/seller/shipments/<int:oid>/update\', methods=[\'POST\'])
@login_required
@seller_required
def update_shipment(oid):
    carrier=request.form.get(\'carrier\',\'\').strip()
    tracking=request.form.get(\'tracking_number\',\'\').strip()
    status=request.form.get(\'status\',\'pending\')
    conn=get_db()
    existing=conn.execute(\'SELECT id FROM shipping WHERE order_id=?\', (oid,)).fetchone()
    if existing:
        conn.execute(
            \'UPDATE shipping SET carrier=?,tracking_number=?,status=?,updated_at=? WHERE order_id=?\',
            (carrier,tracking,status,datetime.utcnow().isoformat(),oid))
    else:
        conn.execute(
            \'INSERT INTO shipping (order_id,carrier,tracking_number,status) VALUES (?,?,?,?)\',
            (oid,carrier,tracking,status))
    if status==\'delivered\':
        conn.execute(\'UPDATE orders SET status=\\\'delivered\\\' WHERE id=?\', (oid,))
    conn.commit(); conn.close()
    flash(\'Shipment updated.\',\'success\')
    return redirect(url_for(\'seller_shipments\'))

# ── Seller returns ────────────────────────────────────────────────────────────

@app.route(\'/seller/returns\')
@login_required
@seller_required
def seller_returns():
    conn=get_db()
    oids=[r[0] for r in conn.execute(
        \'SELECT DISTINCT order_id FROM order_items WHERE seller_id=?\',
        (session[\'user_id\'],)).fetchall()]
    returns=[]
    if oids:
        op=\',\'.join(\'?\' for _ in oids)
        returns=conn.execute(
            f\'SELECT r.*,u.name as customer_name FROM returns r JOIN users u ON r.customer_id=u.id WHERE r.order_id IN ({op}) ORDER BY r.created_at DESC\',
            oids).fetchall()
    conn.close()
    return render_template(\'seller/returns.html\',returns=returns)

@app.route(\'/seller/returns/<int:rid>/respond\', methods=[\'POST\'])
@login_required
@seller_required
def respond_return(rid):
    action=request.form.get(\'action\',\'\')
    note=request.form.get(\'note\',\'\').strip()
    conn=get_db()
    ret=conn.execute(\'SELECT * FROM returns WHERE id=?\', (rid,)).fetchone()
    if ret:
        new_status=\'approved\' if action==\'approve\' else \'rejected\'
        conn.execute(\'UPDATE returns SET status=?,admin_note=?,updated_at=? WHERE id=?\',
                     (new_status,note,datetime.utcnow().isoformat(),rid))
        notify(conn,ret[\'customer_id\'],
               f\'Your return request has been {new_status}.\',
               f\'/orders/{ret["order_id"]}\')
        conn.commit()
    conn.close()
    flash(f\'Return {action}d.\',\'success\')
    return redirect(url_for(\'seller_returns\'))

# ── Seller support tickets ────────────────────────────────────────────────────

@app.route(\'/seller/support\')
@login_required
@seller_required
def seller_support():
    conn=get_db()
    tickets=conn.execute(
        \'SELECT * FROM support_tickets WHERE user_id=? ORDER BY created_at DESC\',
        (session[\'user_id\'],)).fetchall()
    conn.close()
    return render_template(\'seller/support.html\',tickets=tickets)

@app.route(\'/seller/support/new\', methods=[\'POST\'])
@login_required
@seller_required
def create_support_ticket():
    subject=request.form.get(\'subject\',\'\').strip()
    description=request.form.get(\'description\',\'\').strip()
    priority=request.form.get(\'priority\',\'normal\')
    if not subject or not description:
        flash(\'Subject and description are required.\',\'error\')
        return redirect(url_for(\'seller_support\'))
    conn=get_db()
    conn.execute(
        \'INSERT INTO support_tickets (user_id,subject,description,priority) VALUES (?,?,?,?)\',
        (session[\'user_id\'],subject,description,priority))
    conn.commit(); conn.close()
    flash(\'Support ticket created.\',\'success\')
    return redirect(url_for(\'seller_support\'))

# ── Admin KYC ─────────────────────────────────────────────────────────────────

@app.route(\'/admin/kyc\')
@login_required
@admin_required
def admin_kyc():
    conn=get_db()
    sellers=conn.execute(
        \'SELECT u.*,sp.shop_name FROM users u JOIN seller_profiles sp ON u.id=sp.user_id WHERE u.kyc_status="pending" ORDER BY u.created_at DESC\'
    ).fetchall()
    conn.close()
    return render_template(\'admin/kyc.html\',sellers=sellers)

@app.route(\'/admin/kyc/<int:uid>/action\', methods=[\'POST\'])
@login_required
@admin_required
def admin_kyc_action(uid):
    action=request.form.get(\'action\',\'\')
    reason=request.form.get(\'reason\',\'\').strip()
    new_status=\'approved\' if action==\'approve\' else \'rejected\'
    conn=get_db()
    conn.execute(\'UPDATE users SET kyc_status=? WHERE id=?\', (new_status,uid))
    msg=f\'Your KYC has been {new_status}.\'
    if new_status==\'rejected\' and reason: msg+=f\' Reason: {reason}\'
    notify(conn,uid,msg,\'/seller/profile\')
    conn.commit(); conn.close()
    flash(f\'KYC {new_status} for user #{uid}.\',\'success\')
    return redirect(url_for(\'admin_kyc\'))

# ── Admin disputes ────────────────────────────────────────────────────────────

@app.route(\'/admin/disputes\')
@login_required
@admin_required
def admin_disputes():
    conn=get_db()
    returns=conn.execute(
        \'SELECT r.*,u.name as customer_name FROM returns r JOIN users u ON r.customer_id=u.id ORDER BY r.created_at DESC\'
    ).fetchall()
    conn.close()
    return render_template(\'admin/disputes.html\',returns=returns)

@app.route(\'/admin/disputes/<int:rid>/action\', methods=[\'POST\'])
@login_required
@admin_required
def admin_dispute_action(rid):
    action=request.form.get(\'action\',\'\')
    refund_amount=float(request.form.get(\'refund_amount\',0))
    admin_note=request.form.get(\'admin_note\',\'\').strip()
    status_map={\'approve\':\'approved\',\'reject\':\'rejected\',\'refund\':\'refunded\'}
    new_status=status_map.get(action,\'requested\')
    conn=get_db()
    ret=conn.execute(\'SELECT * FROM returns WHERE id=?\', (rid,)).fetchone()
    if ret:
        conn.execute(
            \'UPDATE returns SET status=?,refund_amount=?,admin_note=?,updated_at=? WHERE id=?\',
            (new_status,refund_amount,admin_note,datetime.utcnow().isoformat(),rid))
        notify(conn,ret[\'customer_id\'],
               f\'Your return/dispute has been {new_status}.\',
               f\'/orders/{ret["order_id"]}\')
        conn.commit()
    conn.close()
    flash(f\'Dispute {new_status}.\',\'success\')
    return redirect(url_for(\'admin_disputes\'))

# ── Admin banners ─────────────────────────────────────────────────────────────

@app.route(\'/admin/banners\')
@login_required
@admin_required
def admin_banners():
    conn=get_db()
    banners=conn.execute(\'SELECT * FROM banners ORDER BY position\').fetchall()
    conn.close()
    return render_template(\'admin/banners.html\',banners=banners)

@app.route(\'/admin/banners/add\', methods=[\'POST\'])
@login_required
@admin_required
def admin_add_banner():
    title=request.form.get(\'title\',\'\').strip()
    link=request.form.get(\'link\',\'\').strip()
    position=int(request.form.get(\'position\',0))
    img=save_image(request.files.get(\'image\'))
    if not title:
        flash(\'Title is required.\',\'error\')
        return redirect(url_for(\'admin_banners\'))
    conn=get_db()
    active_count=conn.execute(\'SELECT COUNT(*) FROM banners WHERE is_active=1\').fetchone()[0]
    if active_count>=3:
        oldest=conn.execute(\'SELECT id FROM banners WHERE is_active=1 ORDER BY position LIMIT 1\').fetchone()
        if oldest: conn.execute(\'UPDATE banners SET is_active=0 WHERE id=?\', (oldest[\'id\'],))
    conn.execute(\'INSERT INTO banners (title,image,link,position) VALUES (?,?,?,?)\',
                 (title,img,link,position))
    conn.commit(); conn.close()
    flash(\'Banner added.\',\'success\')
    return redirect(url_for(\'admin_banners\'))

@app.route(\'/admin/banners/<int:bid>/delete\', methods=[\'POST\'])
@login_required
@admin_required
def admin_delete_banner(bid):
    conn=get_db()
    conn.execute(\'DELETE FROM banners WHERE id=?\', (bid,))
    conn.commit(); conn.close()
    flash(\'Banner deleted.\',\'info\')
    return redirect(url_for(\'admin_banners\'))

# ── Admin newsletter ──────────────────────────────────────────────────────────

@app.route(\'/admin/newsletter\')
@login_required
@admin_required
def admin_newsletter():
    conn=get_db()
    subscribers=conn.execute(
        \'SELECT * FROM newsletter ORDER BY subscribed_at DESC\'
    ).fetchall()
    conn.close()
    return render_template(\'admin/newsletter.html\',subscribers=subscribers)

if __name__ == \'__main__\':
    init_db()
    app.run(debug=True)
'''



def _ecom_base_html(site_name: str, font: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{% block title %}}{site_name}{{% endblock %}}</title>
  <link href="https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@300;400;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}"/>
</head>
<body>
<header class="site-header">
  <nav class="navbar">
    <div class="logo">🛍️ {site_name}</div>
    <ul class="nav-links" id="navLinks">
      <li><a href="{{{{ url_for('index') }}}}">Shop</a></li>
      {{%- if session.seller_id %}}
        <li><a href="{{{{ url_for('dashboard') }}}}">Dashboard</a></li>
        <li><a href="{{{{ url_for('orders') }}}}">Orders</a></li>
        <li><a href="{{{{ url_for('logout') }}}}">Logout</a></li>
      {{%- else %}}
        <li><a href="{{{{ url_for('login') }}}}">Seller Login</a></li>
        <li><a href="{{{{ url_for('signup') }}}}">Register</a></li>
      {{%- endif %}}
    </ul>
    <button class="hamburger" onclick="toggleNav()">&#9776;</button>
  </nav>
</header>
{{%- with messages = get_flashed_messages(with_categories=true) %}}
  {{%- if messages %}}{{%- for cat, msg in messages %}}
    <div class="flash flash-{{{{ cat }}}}">{{{{ msg }}}}</div>
  {{%- endfor %}}{{%- endif %}}
{{%- endwith %}}
{{%- block content %}}{{%- endblock %}}
<footer class="site-footer">
  <div class="footer-bottom"><p>&copy; 2025 {site_name}. All rights reserved.</p></div>
</footer>
<script src="{{{{ url_for('static', filename='js/script.js') }}}}"></script>
</body>
</html>"""


def _ecom_index_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}Shop{{% endblock %}}
{{% block content %}}
<section class="shop-hero">
  <h1>Discover Amazing Products</h1>
  <p>Shop from our curated collection</p>
</section>

<!-- Category filter -->
{{% if categories %}}
<div class="category-bar">
  <a href="{{{{ url_for('index') }}}}" class="cat-btn {{% if not selected_category %}}active{{% endif %}}">All</a>
  {{% for c in categories %}}
    <a href="{{{{ url_for('index', category=c.category) }}}}" class="cat-btn {{% if selected_category==c.category %}}active{{% endif %}}">{{{{ c.category }}}}</a>
  {{% endfor %}}
</div>
{{% endif %}}

<section class="products section">
  <div class="container">
    {{% if products %}}
    <div class="cards-grid">
      {{% for p in products %}}
      <div class="product-card">
        {{% if p.image %}}
          <img src="{{{{ url_for('static', filename='uploads/' + p.image) }}}}" alt="{{{{ p.name }}}}"/>
        {{% else %}}
          <img src="https://picsum.photos/seed/{{{{ p.id }}}}/300/200" alt="{{{{ p.name }}}}"/>
        {{% endif %}}
        <div class="product-info">
          {{% if p.category %}}
            <span class="tag">{{{{ p.category }}}}</span>
          {{% endif %}}
          <h3>{{{{ p.name }}}}</h3>
          <p class="product-desc">{{{{ p.description or '' }}}}</p>
          <div class="product-footer">
            <span class="price">₹{{{{ p.price }}}}</span>
            <span class="stock-badge">{{{{ p.stock }}}} left</span>
          </div>
          <button class="btn-primary btn-sm" onclick="openBuyModal({{{{ p.id }}}}, '{{{{ p.name }}}}', {{{{ p.stock }}}})">Buy Now</button>
        </div>
      </div>
      {{% endfor %}}
    </div>
    {{% else %}}
    <div class="empty-state">
      <p>No products available yet.</p>
      <a href="{{{{ url_for('login') }}}}" class="btn-primary">Sellers: Add your products</a>
    </div>
    {{% endif %}}
  </div>
</section>

<!-- Buy Modal -->
<div id="buyModal" class="modal-overlay" style="display:none" onclick="closeBuyModal(event)">
  <div class="modal-card">
    <h3 id="modalTitle">Place Order</h3>
    <form method="POST" id="buyForm">
      <div class="form-group"><label>Your Name</label><input name="buyer_name" type="text" required/></div>
      <div class="form-group"><label>Your Email</label><input name="buyer_email" type="email" required/></div>
      <div class="form-group"><label>Quantity</label><input name="quantity" type="number" value="1" min="1" id="modalQty"/></div>
      <div class="modal-actions">
        <button type="submit" class="btn-primary">Confirm Order</button>
        <button type="button" class="btn-outline" onclick="document.getElementById('buyModal').style.display='none'">Cancel</button>
      </div>
    </form>
  </div>
</div>
{{% endblock %}}"""


def _ecom_dashboard_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}Dashboard — {{{{ session.shop_name }}}}{{% endblock %}}
{{% block content %}}
<section class="dashboard section">
  <div class="container">
    <div class="dash-header">
      <div><h2>Seller Dashboard</h2><p>Welcome, {{{{ session.shop_name }}}}</p></div>
      <a href="{{{{ url_for('add_product') }}}}" class="btn-primary">+ Add Product</a>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card"><span class="stat-icon">📦</span><div><h3>{{{{ products|length }}}}</h3><p>Products</p></div></div>
      <div class="stat-card"><span class="stat-icon">🛒</span><div><h3>{{{{ stats.total_orders }}}}</h3><p>Orders</p></div></div>
      <div class="stat-card"><span class="stat-icon">💰</span><div><h3>₹{{{{ "%.2f"|format(stats.revenue) }}}}</h3><p>Revenue</p></div></div>
    </div>

    <!-- Products table -->
    <div class="section-card">
      <h3>Your Products</h3>
      {{% if products %}}
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>Image</th><th>Name</th><th>Category</th><th>Price</th><th>Stock</th><th>Actions</th></tr></thead>
          <tbody>
          {{% for p in products %}}
          <tr>
            <td>{{% if p.image %}}<img src="{{{{ url_for('static', filename='uploads/'+p.image) }}}}" style="width:48px;height:48px;object-fit:cover;border-radius:6px"/>{{% else %}}—{{% endif %}}</td>
            <td>{{{{ p.name }}}}</td>
            <td>{{{{ p.category or '—' }}}}</td>
            <td>₹{{{{ p.price }}}}</td>
            <td><span class="{{% if p.stock < 5 %}}low-stock{{% endif %}}">{{{{ p.stock }}}}</span></td>
            <td>
              <a href="{{{{ url_for('edit_product', pid=p.id) }}}}" class="btn-sm">Edit</a>
              <form method="POST" action="{{{{ url_for('delete_product', pid=p.id) }}}}" style="display:inline" onsubmit="return confirm('Delete this product?')">
                <button type="submit" class="btn-sm btn-danger">Delete</button>
              </form>
            </td>
          </tr>
          {{% endfor %}}
          </tbody>
        </table>
      </div>
      {{% else %}}<p class="empty-msg">No products yet. <a href="{{{{ url_for('add_product') }}}}">Add your first product →</a></p>{{% endif %}}
    </div>

    <!-- Recent orders -->
    <div class="section-card">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <h3>Recent Orders</h3>
        <a href="{{{{ url_for('orders') }}}}" class="link-more">View all →</a>
      </div>
      {{% if recent_orders %}}
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>#</th><th>Product</th><th>Buyer</th><th>Qty</th><th>Total</th><th>Status</th></tr></thead>
          <tbody>
          {{% for o in recent_orders %}}
          <tr>
            <td>#{{{{ o.id }}}}</td><td>{{{{ o.product_name }}}}</td><td>{{{{ o.buyer_name }}}}</td>
            <td>{{{{ o.quantity }}}}</td><td>₹{{{{ o.total_price }}}}</td>
            <td><span class="badge badge-{{{{ o.status }}}}">{{{{ o.status }}}}</span></td>
          </tr>
          {{% endfor %}}
          </tbody>
        </table>
      </div>
      {{% else %}}<p class="empty-msg">No orders yet.</p>{{% endif %}}
    </div>
  </div>
</section>
{{% endblock %}}"""


def _ecom_add_product_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}Add Product{{% endblock %}}
{{% block content %}}
<section class="auth-section">
  <div class="auth-card" style="max-width:580px">
    <h2>Add New Product</h2>
    <form method="POST" enctype="multipart/form-data">
      <div class="form-group"><label>Product Name *</label><input name="name" type="text" required/></div>
      <div class="form-group"><label>Description</label><textarea name="description" rows="3"></textarea></div>
      <div class="form-row">
        <div class="form-group"><label>Price (₹) *</label><input name="price" type="number" step="0.01" min="0" required/></div>
        <div class="form-group"><label>Stock *</label><input name="stock" type="number" min="0" required/></div>
      </div>
      <div class="form-group"><label>Category</label><input name="category" type="text" placeholder="e.g. Electronics, Clothing"/></div>
      <div class="form-group"><label>Product Image</label><input name="image" type="file" accept="image/*"/></div>
      <div class="form-actions">
        <button type="submit" class="btn-primary">Add Product</button>
        <a href="{{{{ url_for('dashboard') }}}}" class="btn-outline">Cancel</a>
      </div>
    </form>
  </div>
</section>
{{% endblock %}}"""


def _ecom_edit_product_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}Edit Product{{% endblock %}}
{{% block content %}}
<section class="auth-section">
  <div class="auth-card" style="max-width:580px">
    <h2>Edit Product</h2>
    <form method="POST" enctype="multipart/form-data">
      <div class="form-group"><label>Product Name *</label><input name="name" type="text" value="{{{{ product.name }}}}" required/></div>
      <div class="form-group"><label>Description</label><textarea name="description" rows="3">{{{{ product.description or '' }}}}</textarea></div>
      <div class="form-row">
        <div class="form-group"><label>Price (₹) *</label><input name="price" type="number" step="0.01" value="{{{{ product.price }}}}" required/></div>
        <div class="form-group"><label>Stock *</label><input name="stock" type="number" value="{{{{ product.stock }}}}" required/></div>
      </div>
      <div class="form-group"><label>Category</label><input name="category" type="text" value="{{{{ product.category or '' }}}}"/></div>
      <div class="form-group">
        <label>Replace Image (optional)</label>
        {{% if product.image %}}<p style="font-size:.85rem;color:#888">Current: {{{{ product.image }}}}</p>{{% endif %}}
        <input name="image" type="file" accept="image/*"/>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn-primary">Save Changes</button>
        <a href="{{{{ url_for('dashboard') }}}}" class="btn-outline">Cancel</a>
      </div>
    </form>
  </div>
</section>
{{% endblock %}}"""


def _ecom_orders_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}Orders{{% endblock %}}
{{% block content %}}
<section class="dashboard section">
  <div class="container">
    <h2>All Orders</h2>
    {{% if orders %}}
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>#</th><th>Product</th><th>Buyer</th><th>Email</th><th>Qty</th><th>Total</th><th>Status</th><th>Date</th><th>Update</th></tr></thead>
        <tbody>
        {{% for o in orders %}}
        <tr>
          <td>#{{{{ o.id }}}}</td><td>{{{{ o.product_name }}}}</td><td>{{{{ o.buyer_name }}}}</td>
          <td>{{{{ o.buyer_email }}}}</td><td>{{{{ o.quantity }}}}</td><td>₹{{{{ o.total_price }}}}</td>
          <td><span class="badge badge-{{{{ o.status }}}}">{{{{ o.status }}}}</span></td>
          <td style="font-size:.8rem">{{{{ o.created_at }}}}</td>
          <td>
            <form method="POST" action="{{{{ url_for('update_order', oid=o.id) }}}}">
              <select name="status" onchange="this.form.submit()">
                {{% for s in ['pending','processing','shipped','delivered','cancelled'] %}}
                  <option value="{{{{ s }}}}" {{% if o.status==s %}}selected{{% endif %}}>{{{{ s|capitalize }}}}</option>
                {{% endfor %}}
              </select>
            </form>
          </td>
        </tr>
        {{% endfor %}}
        </tbody>
      </table>
    </div>
    {{% else %}}<p class="empty-msg">No orders yet.</p>{{% endif %}}
  </div>
</section>
{{% endblock %}}"""


def _ecom_login_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}{{% if signup %}}Register{{% else %}}Login{{% endif %}}{{% endblock %}}
{{% block content %}}
<section class="auth-section">
  <div class="auth-card">
    {{% if signup %}}
    <h2>Create Seller Account</h2>
    <form method="POST" action="{{{{ url_for('signup') }}}}">
      <div class="form-group"><label>Username *</label><input name="username" type="text" required/></div>
      <div class="form-group"><label>Shop Name</label><input name="shop_name" type="text" placeholder="Your shop name"/></div>
      <div class="form-group"><label>Password *</label><input name="password" type="password" required/></div>
      <button type="submit" class="btn-primary" style="width:100%">Create Account</button>
    </form>
    <p class="auth-switch">Already a seller? <a href="{{{{ url_for('login') }}}}">Login</a></p>
    {{% else %}}
    <h2>Seller Login</h2>
    <form method="POST">
      <div class="form-group"><label>Username</label><input name="username" type="text" required/></div>
      <div class="form-group"><label>Password</label><input name="password" type="password" required/></div>
      <button type="submit" class="btn-primary" style="width:100%">Login</button>
    </form>
    <p class="auth-switch">New seller? <a href="{{{{ url_for('signup') }}}}">Create account</a></p>
    {{% endif %}}
  </div>
</section>
{{% endblock %}}"""


def _ecom_extra_css() -> str:
    return """
/* Shop hero */
.shop-hero{background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;text-align:center;padding:4rem 1.5rem}
.shop-hero h1{font-size:2.2rem;margin-bottom:.5rem}
/* Category bar */
.category-bar{display:flex;flex-wrap:wrap;gap:.5rem;padding:1rem 1.5rem;background:#f9f9f9;border-bottom:1px solid #eee}
.cat-btn{padding:.35rem .9rem;border-radius:20px;border:1px solid #ddd;background:#fff;color:#555;font-size:.85rem;text-decoration:none;transition:all .2s}
.cat-btn.active,.cat-btn:hover{background:var(--primary);color:#fff;border-color:var(--primary)}
/* Product card */
.product-card{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);transition:transform .2s}
.product-card:hover{transform:translateY(-4px)}
.product-card img{width:100%;height:180px;object-fit:cover}
.product-info{padding:1rem}
.product-desc{font-size:.85rem;color:#666;margin:.4rem 0 .75rem;min-height:2.5rem}
.product-footer{display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem}
.price{color:var(--primary);font-weight:700;font-size:1.1rem}
.stock-badge{font-size:.78rem;color:#888}
.low-stock{color:#e53935;font-weight:600}
/* Dashboard */
.dashboard{padding:2rem 0}
.dash-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.5rem}
.dash-header p{color:#888;font-size:.9rem}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin-bottom:1.5rem}
.stat-card{background:var(--primary);color:#fff;padding:1.25rem 1.5rem;border-radius:12px;display:flex;align-items:center;gap:1rem}
.stat-icon{font-size:1.8rem}
.stat-card h3{font-size:1.6rem;margin-bottom:.1rem}
.stat-card p{font-size:.85rem;opacity:.85}
.section-card{background:#fff;border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.section-card h3{margin-bottom:1rem}
.link-more{color:var(--primary);font-size:.9rem;text-decoration:none}
.empty-msg{color:#888;font-size:.9rem}
/* Table */
.table-wrap{overflow-x:auto}
.data-table{width:100%;border-collapse:collapse}
.data-table th{background:var(--primary);color:#fff;padding:.65rem 1rem;text-align:left;font-size:.85rem}
.data-table td{padding:.65rem 1rem;border-bottom:1px solid #f0f0f0;font-size:.88rem}
.data-table tr:last-child td{border-bottom:none}
.btn-sm{padding:.3rem .75rem;border-radius:6px;border:none;cursor:pointer;font-size:.82rem;background:var(--primary);color:#fff;text-decoration:none;display:inline-block;margin-right:.25rem}
.btn-danger{background:#e53935}
.btn-outline{padding:.6rem 1.4rem;border-radius:8px;border:1px solid var(--primary);background:transparent;color:var(--primary);cursor:pointer;font-family:inherit;font-size:.9rem;text-decoration:none;display:inline-block}
/* Badges */
.badge{padding:.2rem .6rem;border-radius:20px;font-size:.75rem;font-weight:600}
.badge-pending{background:#fff3cd;color:#856404}
.badge-processing{background:#cce5ff;color:#004085}
.badge-shipped{background:#d4edda;color:#155724}
.badge-delivered{background:#d1ecf1;color:#0c5460}
.badge-cancelled{background:#f8d7da;color:#721c24}
/* Auth */
.auth-section{min-height:80vh;display:flex;align-items:center;justify-content:center;padding:2rem}
.auth-card{background:#fff;padding:2.5rem;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.1);width:100%;max-width:440px}
.auth-card h2{text-align:center;margin-bottom:1.5rem;color:var(--primary)}
.form-group{margin-bottom:1rem}
.form-group label{display:block;margin-bottom:.4rem;font-size:.88rem;color:#555;font-weight:500}
.form-group input,.form-group textarea,.form-group select{width:100%;padding:.75rem 1rem;border:1px solid #ddd;border-radius:8px;font-size:.95rem;font-family:inherit}
.form-group input:focus,.form-group textarea:focus{outline:none;border-color:var(--primary)}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.form-actions{display:flex;gap:1rem;margin-top:1rem}
.auth-switch{text-align:center;margin-top:1rem;color:#666;font-size:.9rem}
.auth-switch a{color:var(--primary);font-weight:600}
.flash{padding:.75rem 1.5rem;text-align:center;font-weight:500;font-size:.9rem}
.flash-success{background:#d4edda;color:#155724}
.flash-error{background:#f8d7da;color:#721c24}
/* Modal */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:999}
.modal-card{background:#fff;padding:2rem;border-radius:16px;width:100%;max-width:420px;margin:1rem}
.modal-card h3{margin-bottom:1.25rem;color:var(--primary)}
.modal-actions{display:flex;gap:1rem;margin-top:1rem}
"""


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
    <form method="POST" action="{{ url_for('signup') }}">
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
        <select name="role">
          <option value="customer">Shop (Customer)</option>
          <option value="seller">Sell Products (Seller)</option>
        </select>
      </div>
      <button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Create Account</button>
    </form>
    <p class="mv-auth-switch">Already have an account? <a href="{{ url_for('login') }}">Login</a></p>
  </div>
</div>
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


# New template functions for the expanded marketplace
# Injected into generator.py via _inject_new_templates.py


def _mv_about_html(site_name: str) -> str:
    return f"""{{% extends 'base.html' %}}
{{% block title %}}About — {site_name}{{% endblock %}}
{{% block content %}}
<div class="mv-dash" style="max-width:900px;margin:0 auto">
  <div style="text-align:center;padding:3rem 1rem 2rem">
    <h1 style="font-size:2rem;font-weight:800;margin-bottom:.75rem">About <span style="color:var(--mv-pink)">{site_name}</span></h1>
    <p style="color:#666;font-size:1.05rem;max-width:600px;margin:0 auto">
      {site_name} is India's fastest-growing multi-vendor marketplace, connecting millions of sellers with customers across the country.
    </p>
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin-bottom:3rem">
    <div class="mv-stat" style="border-top:4px solid var(--mv-pink)">
      <div class="mv-stat-val">{{{{ stats.sellers }}}}+</div>
      <div class="mv-stat-label">Active Sellers</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #ff5722">
      <div class="mv-stat-val">{{{{ stats.products }}}}+</div>
      <div class="mv-stat-label">Products Listed</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #4caf50">
      <div class="mv-stat-val">{{{{ stats.orders }}}}+</div>
      <div class="mv-stat-label">Orders Delivered</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;margin-bottom:3rem">
    <div style="background:#fff;border-radius:16px;padding:2rem;box-shadow:0 2px 8px rgba(0,0,0,.06)">
      <h3 style="font-weight:800;margin-bottom:.75rem">🎯 Our Mission</h3>
      <p style="color:#666;line-height:1.7">To empower every seller — from home entrepreneurs to established businesses — with the tools to reach millions of customers and grow their income.</p>
    </div>
    <div style="background:#fff;border-radius:16px;padding:2rem;box-shadow:0 2px 8px rgba(0,0,0,.06)">
      <h3 style="font-weight:800;margin-bottom:.75rem">💡 Our Vision</h3>
      <p style="color:#666;line-height:1.7">A marketplace where quality products from every corner of India are accessible to every customer, at the best prices, with zero friction.</p>
    </div>
  </div>
  <div style="text-align:center;padding:2rem;background:linear-gradient(135deg,var(--mv-pink),#ff5722);border-radius:16px;color:#fff">
    <h2 style="font-weight:800;margin-bottom:.5rem">Want to sell on {site_name}?</h2>
    <p style="opacity:.9;margin-bottom:1.25rem">Join thousands of sellers already earning on our platform.</p>
    <a href="{{{{ url_for('become_supplier') }}}}" style="background:#fff;color:var(--mv-pink);padding:.7rem 2rem;border-radius:30px;font-weight:700;text-decoration:none">Become a Seller</a>
  </div>
</div>
{{% endblock %}}"""


def _mv_deals_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Deals of the Day{%- endblock %}
{%- block content %}
<div style="max-width:1400px;margin:0 auto;padding:1.5rem">
  <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1.5rem">
    <span style="font-size:1.8rem">🔥</span>
    <h2 style="font-size:1.5rem;font-weight:800;margin:0">Deals of the Day</h2>
    <span style="background:#ffebee;color:#e91e63;padding:.2rem .75rem;border-radius:20px;font-size:.82rem;font-weight:700">Up to 80% OFF</span>
  </div>
  {%- if products %}
  <div class="mv-grid">
    {%- for p in products %}
    <div class="mv-card" onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
      <div style="position:relative">
        <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
             alt="{{ p.name }}" onerror="this.src='https://placehold.co/300x300/fce4ec/e91e63?text=No+Image'"/>
        <span style="position:absolute;top:8px;left:8px;background:#e91e63;color:#fff;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:700">
          {{ p.discount_percent|int }}% OFF
        </span>
      </div>
      <div class="mv-card-body">
        <div class="mv-card-name">{{ p.name }}</div>
        <div style="display:flex;align-items:center;gap:.5rem">
          <div class="mv-card-price">₹{{ '%.0f'|format(p.price) }}</div>
          {%- if p.mrp and p.mrp > p.price %}
          <div style="font-size:.78rem;color:#888;text-decoration:line-through">₹{{ '%.0f'|format(p.mrp) }}</div>
          {%- endif %}
        </div>
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
    <div style="font-size:4rem">🏷️</div>
    <h3 style="margin:.75rem 0;color:#555">No deals right now</h3>
    <p style="color:#888">Check back soon for amazing offers!</p>
    <a href="{{ url_for('index') }}" class="mv-btn mv-btn-primary" style="display:inline-block;margin-top:1rem">Browse All Products</a>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_new_arrivals_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}New Arrivals{%- endblock %}
{%- block content %}
<div style="max-width:1400px;margin:0 auto;padding:1.5rem">
  <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1.5rem">
    <span style="font-size:1.8rem">✨</span>
    <h2 style="font-size:1.5rem;font-weight:800;margin:0">New Arrivals</h2>
    <span style="background:#e8f5e9;color:#2e7d32;padding:.2rem .75rem;border-radius:20px;font-size:.82rem;font-weight:700">Just In</span>
  </div>
  {%- if products %}
  <div class="mv-grid">
    {%- for p in products %}
    <div class="mv-card" onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
      <div style="position:relative">
        <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
             alt="{{ p.name }}" onerror="this.src='https://placehold.co/300x300/fce4ec/e91e63?text=No+Image'"/>
        <span style="position:absolute;top:8px;left:8px;background:#4caf50;color:#fff;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:700">NEW</span>
      </div>
      <div class="mv-card-body">
        <div class="mv-card-name">{{ p.name }}</div>
        <div class="mv-card-price">₹{{ '%.0f'|format(p.price) }}</div>
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
    <div style="font-size:4rem">📦</div>
    <h3 style="margin:.75rem 0;color:#555">No new arrivals yet</h3>
    <a href="{{ url_for('index') }}" class="mv-btn mv-btn-primary" style="display:inline-block;margin-top:1rem">Browse All Products</a>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""



def _mv_become_supplier_html(site_name: str) -> str:
    return f"""{{% extends 'base.html' %}}
{{% block title %}}Become a Seller — {site_name}{{% endblock %}}
{{% block content %}}
<div style="max-width:900px;margin:0 auto;padding:2rem 1rem">
  <div style="text-align:center;padding:3rem 1rem;background:linear-gradient(135deg,var(--mv-pink),#ff5722);border-radius:20px;color:#fff;margin-bottom:2.5rem">
    <h1 style="font-size:2.2rem;font-weight:800;margin-bottom:.75rem">Start Selling on {site_name}</h1>
    <p style="opacity:.9;font-size:1.05rem;margin-bottom:1.5rem">Join {{{{ stats.sellers }}}}+ sellers already earning on our platform</p>
    <a href="{{{{ url_for('signup') }}}}?role=seller" style="background:#fff;color:var(--mv-pink);padding:.85rem 2.5rem;border-radius:30px;font-weight:800;font-size:1.05rem;text-decoration:none">Register as Seller →</a>
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin-bottom:2.5rem">
    <div class="mv-stat" style="border-top:4px solid var(--mv-pink)">
      <div class="mv-stat-val">{{{{ stats.sellers }}}}+</div><div class="mv-stat-label">Active Sellers</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #ff5722">
      <div class="mv-stat-val">{{{{ stats.products }}}}+</div><div class="mv-stat-label">Products Listed</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #4caf50">
      <div class="mv-stat-val">{{{{ stats.orders }}}}+</div><div class="mv-stat-label">Orders Placed</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #2196f3">
      <div class="mv-stat-val">90%</div><div class="mv-stat-label">Seller Payout</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:2.5rem">
    {{% for icon, title, desc in [
      ('🚀','Easy Onboarding','Register, complete KYC, and start listing products in minutes.'),
      ('💰','High Payouts','Earn 90% of every sale. Withdraw to your bank anytime.'),
      ('📦','Logistics Support','We handle shipping tracking and returns for you.'),
      ('📊','Real-time Dashboard','Track orders, earnings, and inventory in one place.')
    ] %}}
    <div style="background:#fff;border-radius:14px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06)">
      <div style="font-size:2rem;margin-bottom:.5rem">{{{{ icon }}}}</div>
      <h4 style="font-weight:700;margin-bottom:.4rem">{{{{ title }}}}</h4>
      <p style="color:#666;font-size:.88rem;line-height:1.6">{{{{ desc }}}}</p>
    </div>
    {{% endfor %}}
  </div>
  <div style="text-align:center">
    <a href="{{{{ url_for('signup') }}}}?role=seller" class="mv-btn mv-btn-primary" style="font-size:1.05rem;padding:.85rem 2.5rem">Get Started Free →</a>
  </div>
</div>
{{% endblock %}}"""


def _mv_otp_request_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Login with OTP{%- endblock %}
{%- block content %}
<div class="mv-auth">
  <div class="mv-auth-card">
    <h2>Login with OTP</h2>
    <p class="subtitle">Enter your mobile number to receive a 6-digit OTP</p>
    <form method="POST" action="{{ url_for('otp_request') }}">
      <div class="mv-form-group">
        <label>Mobile Number</label>
        <input type="tel" name="mobile" placeholder="10-digit mobile number"
               pattern="[0-9]{10}" maxlength="10" required autofocus
               style="letter-spacing:.1em;font-size:1.1rem"/>
      </div>
      <button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Send OTP</button>
    </form>
    <p class="mv-auth-switch">
      Or <a href="{{ url_for('login') }}">login with email & password</a>
    </p>
    <p class="mv-auth-switch">
      New here? <a href="{{ url_for('signup') }}">Create account</a>
    </p>
  </div>
</div>
{%- endblock %}"""


def _mv_otp_verify_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Verify OTP{%- endblock %}
{%- block content %}
<div class="mv-auth">
  <div class="mv-auth-card">
    <h2>Enter OTP</h2>
    <p class="subtitle">
      We sent a 6-digit code to
      <strong>{{ mobile[:4] }}****{{ mobile[-2:] }}</strong>
    </p>
    <form method="POST" action="{{ url_for('otp_verify') }}">
      <div class="mv-form-group">
        <label>6-Digit OTP</label>
        <input type="text" name="code" placeholder="Enter OTP"
               pattern="[0-9]{6}" maxlength="6" required autofocus
               style="letter-spacing:.3em;font-size:1.4rem;text-align:center"/>
      </div>
      <button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Verify & Login</button>
    </form>
    <p class="mv-auth-switch">
      Wrong number? <a href="{{ url_for('otp_request') }}">Go back</a>
    </p>
    <p style="text-align:center;font-size:.78rem;color:#aaa;margin-top:.75rem">OTP expires in 10 minutes</p>
  </div>
</div>
{%- endblock %}"""


def _mv_seller_inventory_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Inventory — Seller{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>📦 Inventory Management</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>Stock Levels</h3></div>
    {%- if products %}
    <table class="mv-table">
      <thead><tr><th>Image</th><th>Product</th><th>Category</th><th>Current Stock</th><th>Status</th><th>Update Stock</th></tr></thead>
      <tbody>
        {%- for p in products %}
        <tr>
          <td><img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
                   style="width:44px;height:44px;object-fit:cover;border-radius:8px"
                   onerror="this.src='https://placehold.co/44x44/fce4ec/e91e63?text=?'"/></td>
          <td style="font-weight:700">{{ p.name }}</td>
          <td><span class="badge badge-confirmed">{{ p.category }}</span></td>
          <td>
            <span class="badge {% if p.stock == 0 %}badge-cancelled{% elif p.stock < 5 %}badge-pending{% else %}badge-paid{% endif %}">
              {{ p.stock }} units
            </span>
          </td>
          <td>
            {%- if p.stock == 0 %}<span style="color:#e53935;font-size:.82rem">Out of Stock</span>
            {%- elif p.stock < 5 %}<span style="color:#ff9800;font-size:.82rem">⚠ Low Stock</span>
            {%- else %}<span style="color:#4caf50;font-size:.82rem">In Stock</span>{%- endif %}
          </td>
          <td>
            <form method="POST" action="{{ url_for('update_inventory', pid=p.id) }}" style="display:flex;gap:.4rem">
              <input type="number" name="stock" value="{{ p.stock }}" min="0"
                     style="width:80px;padding:.35rem .6rem;border:1.5px solid #eee;border-radius:6px;font-size:.88rem"/>
              <button type="submit" class="mv-btn mv-btn-primary mv-btn-sm">Save</button>
            </form>
          </td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
    {%- else %}
    <div style="text-align:center;padding:3rem"><p style="color:#888">No products yet.</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""


def _mv_seller_shipments_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Shipments — Seller{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🚚 Shipment Tracking</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>All Shipments</h3></div>
    {%- if shipments %}
    <table class="mv-table">
      <thead><tr><th>Order #</th><th>Carrier</th><th>Tracking No.</th><th>Status</th><th>Est. Delivery</th><th>Update</th></tr></thead>
      <tbody>
        {%- for s in shipments %}
        <tr>
          <td style="font-weight:700">#{{ s.order_id }}</td>
          <td>{{ s.carrier or '—' }}</td>
          <td style="font-family:monospace;font-size:.85rem">{{ s.tracking_number or '—' }}</td>
          <td><span class="badge badge-{{ 'paid' if s.status=='delivered' else 'confirmed' if s.status=='in_transit' else 'pending' }}">{{ s.status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ s.estimated_delivery[:10] if s.estimated_delivery else '—' }}</td>
          <td>
            <form method="POST" action="{{ url_for('update_shipment', oid=s.order_id) }}" style="display:flex;gap:.4rem;flex-wrap:wrap">
              <input type="text" name="carrier" value="{{ s.carrier or '' }}" placeholder="Carrier" style="width:90px;padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <input type="text" name="tracking_number" value="{{ s.tracking_number or '' }}" placeholder="Tracking #" style="width:110px;padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <select name="status" style="padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem">
                {%- for st in ['pending','dispatched','in_transit','out_for_delivery','delivered'] %}
                <option value="{{ st }}" {{ 'selected' if s.status==st else '' }}>{{ st|replace('_',' ')|capitalize }}</option>
                {%- endfor %}
              </select>
              <button type="submit" class="mv-btn mv-btn-primary mv-btn-sm">Update</button>
            </form>
          </td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
    {%- else %}
    <div style="text-align:center;padding:3rem"><p style="color:#888">No shipments yet.</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""


def _mv_seller_returns_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Returns — Seller{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>↩️ Return Requests</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  {%- if returns %}
  {%- for r in returns %}
  <div class="mv-table-wrap" style="margin-bottom:1rem">
    <div class="mv-table-head">
      <div>
        <strong>Return #{{ r.id }}</strong> — Order #{{ r.order_id }}
        <span style="color:#888;font-size:.82rem;margin-left:.75rem">{{ r.created_at[:10] }}</span>
        <span style="margin-left:.75rem">Customer: <strong>{{ r.customer_name }}</strong></span>
      </div>
      <span class="badge badge-{{ 'paid' if r.status=='refunded' else 'pending' if r.status=='requested' else 'confirmed' }}">{{ r.status|capitalize }}</span>
    </div>
    <div style="padding:1rem">
      <p style="color:#555;margin-bottom:.75rem"><strong>Reason:</strong> {{ r.reason }}</p>
      {%- if r.status == 'requested' %}
      <form method="POST" action="{{ url_for('respond_return', rid=r.id) }}" style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap">
        <input type="text" name="note" placeholder="Add a note (optional)" style="flex:1;min-width:200px;padding:.4rem .75rem;border:1.5px solid #eee;border-radius:8px;font-size:.88rem"/>
        <button name="action" value="approve" class="mv-btn mv-btn-primary mv-btn-sm">Approve</button>
        <button name="action" value="reject" class="mv-btn mv-btn-danger mv-btn-sm">Reject</button>
      </form>
      {%- else %}
      <p style="color:#888;font-size:.85rem">Admin note: {{ r.admin_note or '—' }}</p>
      {%- endif %}
    </div>
  </div>
  {%- endfor %}
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">✅</div>
    <h5 style="margin:.75rem 0;color:#555">No return requests</h5>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_seller_support_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Support Tickets — Seller{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🎫 Support Tickets</h2>
    <a href="{{ url_for('seller_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap" style="margin-bottom:1.5rem">
    <div class="mv-table-head"><h3>New Ticket</h3></div>
    <div style="padding:1.25rem">
      <form method="POST" action="{{ url_for('create_support_ticket') }}" style="display:grid;grid-template-columns:1fr 1fr auto;gap:.75rem;align-items:end">
        <div>
          <label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Subject *</label>
          <input type="text" name="subject" class="mv-form-input" placeholder="Describe your issue" required/>
        </div>
        <div>
          <label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Priority</label>
          <select name="priority" class="mv-form-input">
            <option value="low">Low</option>
            <option value="normal" selected>Normal</option>
            <option value="high">High</option>
          </select>
        </div>
        <button type="submit" class="mv-btn mv-btn-primary">Submit</button>
        <div style="grid-column:1/-1">
          <label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Description *</label>
          <textarea name="description" class="mv-form-input" rows="3" placeholder="Provide details…" required></textarea>
        </div>
      </form>
    </div>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head"><h3>My Tickets</h3></div>
    {%- if tickets %}
    <table class="mv-table">
      <thead><tr><th>#</th><th>Subject</th><th>Priority</th><th>Status</th><th>Admin Reply</th><th>Date</th></tr></thead>
      <tbody>
        {%- for t in tickets %}
        <tr>
          <td>{{ t.id }}</td>
          <td style="font-weight:600">{{ t.subject }}</td>
          <td><span class="badge badge-{{ 'cancelled' if t.priority=='high' else 'pending' if t.priority=='normal' else 'confirmed' }}">{{ t.priority|capitalize }}</span></td>
          <td><span class="badge badge-{{ 'paid' if t.status=='resolved' else 'confirmed' if t.status=='in_progress' else 'pending' }}">{{ t.status|replace('_',' ')|capitalize }}</span></td>
          <td style="color:#666;font-size:.85rem">{{ t.admin_reply or '—' }}</td>
          <td style="color:#888;font-size:.82rem">{{ t.created_at[:10] }}</td>
        </tr>
        {%- endfor %}
      </tbody>
    </table>
    {%- else %}
    <div style="text-align:center;padding:2rem"><p style="color:#888">No tickets yet.</p></div>
    {%- endif %}
  </div>
</div>
{%- endblock %}"""



def _mv_admin_kyc_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}KYC Queue — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🪪 KYC Approval Queue</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>Seller</th><th>Email</th><th>Shop Name</th><th>KYC Status</th><th>Joined</th><th>Action</th></tr></thead>
      <tbody>
        {%- for s in sellers %}
        <tr>
          <td style="font-weight:700">{{ s.name }}</td>
          <td style="color:#888;font-size:.85rem">{{ s.email }}</td>
          <td>{{ s.shop_name or '—' }}</td>
          <td><span class="badge badge-pending">{{ s.kyc_status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ s.created_at[:10] }}</td>
          <td>
            <form method="POST" action="{{ url_for('admin_kyc_action', uid=s.id) }}" style="display:flex;gap:.4rem;align-items:center">
              <input type="text" name="reason" placeholder="Reason (for rejection)" style="width:160px;padding:.3rem .6rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <button name="action" value="approve" class="mv-btn mv-btn-primary mv-btn-sm">Approve</button>
              <button name="action" value="reject" class="mv-btn mv-btn-danger mv-btn-sm">Reject</button>
            </form>
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="6" style="text-align:center;color:#888;padding:2rem">No pending KYC submissions.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_disputes_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Disputes — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>⚖️ Disputes & Returns</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>#</th><th>Order</th><th>Customer</th><th>Reason</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
      <tbody>
        {%- for r in returns %}
        <tr>
          <td>{{ r.id }}</td>
          <td style="font-weight:700">#{{ r.order_id }}</td>
          <td>{{ r.customer_name }}</td>
          <td style="max-width:180px;font-size:.85rem;color:#555">{{ r.reason[:80] }}{% if r.reason|length > 80 %}…{% endif %}</td>
          <td><span class="badge badge-{{ 'paid' if r.status=='refunded' else 'pending' if r.status=='requested' else 'confirmed' if r.status=='approved' else 'cancelled' }}">{{ r.status|capitalize }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ r.created_at[:10] }}</td>
          <td>
            {%- if r.status in ['requested','approved'] %}
            <form method="POST" action="{{ url_for('admin_dispute_action', rid=r.id) }}" style="display:flex;gap:.4rem;flex-wrap:wrap">
              <input type="number" name="refund_amount" placeholder="Refund ₹" step="0.01" style="width:90px;padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <input type="text" name="admin_note" placeholder="Note" style="width:110px;padding:.3rem .5rem;border:1.5px solid #eee;border-radius:6px;font-size:.8rem"/>
              <button name="action" value="approve" class="mv-btn mv-btn-primary mv-btn-sm">Approve</button>
              <button name="action" value="refund" class="mv-btn mv-btn-outline mv-btn-sm">Refund</button>
              <button name="action" value="reject" class="mv-btn mv-btn-danger mv-btn-sm">Reject</button>
            </form>
            {%- else %}
            <span style="color:#888;font-size:.82rem">{{ r.admin_note or '—' }}</span>
            {%- endif %}
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="7" style="text-align:center;color:#888;padding:2rem">No disputes.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_banners_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Banners — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>🖼️ Banner Management</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap" style="margin-bottom:1.5rem">
    <div style="padding:1.25rem;border-bottom:1px solid #eee;font-weight:700">Add New Banner (max 3 active)</div>
    <div style="padding:1.25rem">
      <form method="POST" action="{{ url_for('admin_add_banner') }}" enctype="multipart/form-data"
            style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.75rem;align-items:end">
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Title *</label>
          <input type="text" name="title" class="mv-form-input" placeholder="Banner title" required/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Link URL</label>
          <input type="text" name="link" class="mv-form-input" placeholder="/deals/"/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Position</label>
          <input type="number" name="position" class="mv-form-input" value="0" min="0"/></div>
        <div><label style="font-size:.82rem;font-weight:600;display:block;margin-bottom:.3rem">Image *</label>
          <input type="file" name="image" accept="image/*" required style="width:100%"/></div>
        <div><button type="submit" class="mv-btn mv-btn-primary" style="width:100%">Add Banner</button></div>
      </form>
    </div>
  </div>
  <div class="mv-table-wrap">
    <table class="mv-table">
      <thead><tr><th>Preview</th><th>Title</th><th>Link</th><th>Position</th><th>Status</th><th>Action</th></tr></thead>
      <tbody>
        {%- for b in banners %}
        <tr>
          <td><img src="{{ url_for('static', filename='uploads/' + b.image) }}"
                   style="width:80px;height:44px;object-fit:cover;border-radius:6px"
                   onerror="this.src='https://placehold.co/80x44/eee/999?text=Banner'"/></td>
          <td style="font-weight:700">{{ b.title }}</td>
          <td style="font-size:.82rem;color:#888">{{ b.link or '—' }}</td>
          <td>{{ b.position }}</td>
          <td><span class="badge badge-{{ 'paid' if b.is_active else 'cancelled' }}">{{ 'Active' if b.is_active else 'Inactive' }}</span></td>
          <td>
            <form method="POST" action="{{ url_for('admin_delete_banner', bid=b.id) }}" onsubmit="return confirm('Delete banner?')">
              <button class="mv-btn mv-btn-danger mv-btn-sm">Delete</button>
            </form>
          </td>
        </tr>
        {%- else %}
        <tr><td colspan="6" style="text-align:center;color:#888;padding:2rem">No banners yet.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


def _mv_admin_newsletter_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Newsletter — Admin{%- endblock %}
{%- block content %}
<div class="mv-dash">
  <div class="mv-dash-header">
    <h2>📧 Newsletter Subscribers</h2>
    <a href="{{ url_for('admin_dashboard') }}" class="mv-btn mv-btn-outline mv-btn-sm">← Dashboard</a>
  </div>
  <div class="mv-table-wrap">
    <div class="mv-table-head">
      <h3>Subscribers ({{ subscribers|length }})</h3>
    </div>
    <table class="mv-table">
      <thead><tr><th>#</th><th>Email</th><th>Status</th><th>Subscribed</th></tr></thead>
      <tbody>
        {%- for s in subscribers %}
        <tr>
          <td style="color:#888">{{ loop.index }}</td>
          <td>{{ s.email }}</td>
          <td><span class="badge badge-{{ 'paid' if s.is_active else 'cancelled' }}">{{ 'Active' if s.is_active else 'Unsubscribed' }}</span></td>
          <td style="color:#888;font-size:.82rem">{{ s.subscribed_at[:10] }}</td>
        </tr>
        {%- else %}
        <tr><td colspan="4" style="text-align:center;color:#888;padding:2rem">No subscribers yet.</td></tr>
        {%- endfor %}
      </tbody>
    </table>
  </div>
</div>
{%- endblock %}"""


# ─────────────────────────────────────────────────────────────────────────────
# 4. SHARED CSS / JS
# ─────────────────────────────────────────────────────────────────────────────

def _base_css(primary: str, secondary: str, font: str) -> str:
    return f"""/* Generated by WebGen Platform */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--primary:{primary};--secondary:{secondary};--text:#333;--bg:#fff;--surface:#f8f9fa;--border:#e0e0e0}}
body{{font-family:'{font}',sans-serif;color:var(--text);background:var(--bg);line-height:1.6}}
a{{text-decoration:none;color:inherit}}
img{{max-width:100%;display:block}}
.container{{max-width:1100px;margin:0 auto;padding:0 1.5rem}}
.section{{padding:5rem 0}}
.section-title{{text-align:center;font-size:2rem;margin-bottom:2.5rem;color:var(--primary);position:relative}}
.section-title::after{{content:'';display:block;width:60px;height:3px;background:var(--secondary);margin:.6rem auto 0}}

/* Navbar */
.site-header{{background:var(--primary);color:#fff;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.2)}}
.navbar{{display:flex;align-items:center;justify-content:space-between;padding:.85rem 1.5rem;max-width:1200px;margin:0 auto}}
.logo{{font-size:1.3rem;font-weight:700;color:#fff}}
.nav-links{{list-style:none;display:flex;gap:1.5rem}}
.nav-links a{{color:rgba(255,255,255,.9);font-weight:500;transition:color .2s;font-size:.95rem}}
.nav-links a:hover{{color:#fff}}
.hamburger{{display:none;background:none;border:none;color:#fff;font-size:1.5rem;cursor:pointer}}

/* Hero */
.hero{{background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:2rem}}
.hero-content h1{{font-size:clamp(2rem,5vw,3.5rem);margin-bottom:1rem;line-height:1.2}}
.hero-content p{{font-size:1.15rem;margin-bottom:2rem;opacity:.9;max-width:600px;margin-left:auto;margin-right:auto}}

/* Buttons */
.btn-primary{{background:var(--secondary);color:#fff;border:none;padding:.75rem 2rem;border-radius:30px;font-size:1rem;cursor:pointer;transition:transform .2s,box-shadow .2s;display:inline-block;font-family:inherit;font-weight:600}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.2)}}
.btn-sm{{padding:.45rem 1.1rem;font-size:.88rem}}

/* Cards grid */
.cards-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem}}
.card{{background:#fff;border-radius:12px;padding:1.75rem;box-shadow:0 2px 12px rgba(0,0,0,.07);transition:transform .2s}}
.card:hover{{transform:translateY(-4px)}}
.card-icon{{font-size:2.2rem;margin-bottom:1rem}}
.card h3{{margin-bottom:.5rem;font-size:1.1rem}}
.card p{{color:#666;font-size:.92rem;line-height:1.6}}
.tag{{display:inline-block;padding:.2rem .65rem;border-radius:20px;background:var(--primary);color:#fff;font-size:.75rem;margin-bottom:.5rem}}
.read-more{{color:var(--primary);font-weight:600;font-size:.9rem;display:inline-block;margin-top:.75rem}}

/* About */
.about-grid{{display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:center}}
.about-text p{{color:#555;margin-bottom:1rem;line-height:1.8}}
.about-stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;text-align:center}}
.stat{{background:var(--surface);padding:1.5rem 1rem;border-radius:12px}}
.stat-num{{display:block;font-size:1.8rem;font-weight:700;color:var(--primary)}}

/* Portfolio */
.portfolio-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem}}
.portfolio-item{{position:relative;border-radius:12px;overflow:hidden;cursor:pointer}}
.portfolio-item img{{width:100%;height:200px;object-fit:cover;transition:transform .3s}}
.portfolio-item:hover img{{transform:scale(1.05)}}
.portfolio-overlay{{position:absolute;inset:0;background:rgba(0,0,0,.6);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;opacity:0;transition:opacity .3s}}
.portfolio-item:hover .portfolio-overlay{{opacity:1}}
.portfolio-overlay h3{{font-size:1.1rem}}
.portfolio-overlay p{{font-size:.85rem;opacity:.8}}

/* Testimonials */
.testimonials-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem}}
.testimonial{{background:#fff;padding:1.75rem;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.07)}}
.testimonial p{{color:#555;font-style:italic;margin-bottom:1.25rem;line-height:1.7}}
.testimonial-author{{display:flex;align-items:center;gap:.75rem}}
.testimonial-author img{{width:44px;height:44px;border-radius:50%;object-fit:cover}}
.testimonial-author strong{{display:block;font-size:.95rem}}
.testimonial-author span{{font-size:.82rem;color:#888}}

/* Contact */
.contact-layout{{display:grid;grid-template-columns:1fr 2fr;gap:3rem;align-items:start}}
.contact-info{{display:flex;flex-direction:column;gap:1.25rem}}
.contact-item{{display:flex;align-items:center;gap:.75rem;font-size:.95rem;color:#555}}
.contact-item span{{font-size:1.3rem}}
.contact-form{{display:flex;flex-direction:column;gap:1rem}}
.contact-form input,.contact-form textarea{{padding:.85rem 1rem;border:1px solid var(--border);border-radius:8px;font-size:1rem;font-family:inherit;transition:border-color .2s}}
.contact-form input:focus,.contact-form textarea:focus{{outline:none;border-color:var(--primary)}}

/* Footer */
.site-footer{{background:#1a1a2e;color:#aaa}}
.footer-content{{max-width:1100px;margin:0 auto;padding:3rem 1.5rem;display:grid;grid-template-columns:2fr 1fr 1fr;gap:2rem}}
.footer-brand .logo{{color:#fff;margin-bottom:.75rem}}
.footer-brand p{{font-size:.9rem;line-height:1.7}}
.footer-links h4,.footer-social h4{{color:#fff;margin-bottom:1rem;font-size:.95rem}}
.footer-links ul{{list-style:none;display:flex;flex-direction:column;gap:.5rem}}
.footer-links a{{color:#aaa;font-size:.9rem;transition:color .2s}}
.footer-links a:hover{{color:#fff}}
.social-icons{{display:flex;gap:1rem}}
.social-icons a{{color:#aaa;font-size:.9rem;transition:color .2s}}
.social-icons a:hover{{color:#fff}}
.footer-bottom{{border-top:1px solid #2a2a4a;text-align:center;padding:1.25rem;font-size:.85rem}}

/* Responsive */
@media(max-width:900px){{
  .about-grid{{grid-template-columns:1fr}}
  .contact-layout{{grid-template-columns:1fr}}
  .footer-content{{grid-template-columns:1fr}}
}}
@media(max-width:768px){{
  .nav-links{{display:none;flex-direction:column;position:absolute;top:60px;left:0;right:0;background:var(--primary);padding:1rem 1.5rem;gap:.75rem}}
  .nav-links.open{{display:flex}}
  .hamburger{{display:block}}
  .hero{{min-height:70vh}}
}}
"""


def _base_js() -> str:
    return """// Generated by WebGen Platform

// Mobile nav toggle
function toggleNav() {
  document.getElementById('navLinks').classList.toggle('open');
}

// Contact form handler (static sites)
function handleContact(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.textContent = 'Sending...';
  btn.disabled = true;
  setTimeout(() => {
    alert('Message sent! We will get back to you soon.');
    e.target.reset();
    btn.textContent = 'Send Message';
    btn.disabled = false;
  }, 800);
}

// Buy modal (e-commerce)
function openBuyModal(pid, name, stock) {
  document.getElementById('modalTitle').textContent = 'Order: ' + name;
  document.getElementById('buyForm').action = '/buy/' + pid;
  document.getElementById('modalQty').max = stock;
  document.getElementById('buyModal').style.display = 'flex';
}
function closeBuyModal(e) {
  if (e.target.id === 'buyModal') {
    document.getElementById('buyModal').style.display = 'none';
  }
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});

// Scroll reveal animation
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card, .product-card, .testimonial, .portfolio-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = 'opacity .5s ease, transform .5s ease';
  revealObserver.observe(el);
});
"""


# ─────────────────────────────────────────────────────────────────────────────
# 5. README generators
# ─────────────────────────────────────────────────────────────────────────────

def _readme_static(name: str) -> str:
    return f"""{name} — Static Website
Generated by WebGen Platform

HOW TO RUN:
  1. Open index.html in any web browser — that's it!

FILES:
  index.html  — Main page
  style.css   — All styles
  script.js   — Interactivity
"""


def _readme_flask(name: str, has_auth: bool) -> str:
    auth_note = "\n  - Login/Signup at /login and /signup" if has_auth else ""
    return f"""{name} — Flask Website
Generated by WebGen Platform

HOW TO RUN:
  1. pip install -r requirements.txt
  2. python app.py
  3. Open http://localhost:5000{auth_note}

FILES:
  app.py              — Flask application
  templates/          — Jinja2 HTML templates
  static/css/         — Stylesheets
  static/js/          — JavaScript
  database.db         — SQLite database (auto-created)
"""


def _readme_ecom(name: str) -> str:
    return f"""{name} — E-commerce Platform
Generated by WebGen Platform

HOW TO RUN:
  1. pip install -r requirements.txt
  2. python app.py
  3. Open http://localhost:5000

SELLER WORKFLOW:
  1. Go to /signup to create a seller account
  2. Login at /login
  3. Use /dashboard to manage products
  4. View orders at /orders

PUBLIC STOREFRONT:
  - Browse products at /
  - Click "Buy Now" to place an order

FILES:
  app.py              — Flask application + all routes
  templates/          — Jinja2 HTML templates
  static/css/         — Stylesheets
  static/js/          — JavaScript
  static/uploads/     — Product images
  database.db         — SQLite database (auto-created)
"""


# ─────────────────────────────────────────────────────────────────────────────
# 4. STARTUP LANDING PAGE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def _gen_startup(config: dict) -> dict:
    """Generate a SaaS/startup landing page with Flask + waitlist DB."""
    name      = _c(config, "site_name", "My Startup")
    tagline   = _c(config, "tagline", "The future starts here")
    primary   = _c(config, "primary_color", "#6c63ff")
    secondary = _c(config, "secondary_color", "#f50057")
    font      = _c(config, "font", "Poppins")
    sections  = config.get("sections", ["header","hero","services","pricing","testimonials","faq","contact","footer"])

    return {
        "app.py":                   _startup_app_py(name),
        "templates/base.html":      _startup_base_html(name, font, primary, secondary),
        "templates/index.html":     _startup_index_html(name, tagline, sections),
        "templates/admin.html":     _startup_admin_html(),
        "static/css/style.css":     _startup_css(primary, secondary, font),
        "static/js/script.js":      _startup_js(),
        "requirements.txt":         "Flask==3.0.0\nWerkzeug==3.0.1\n",
        "README.txt":               _readme_startup(name),
    }


def _startup_app_py(name: str) -> str:
    return f'''"""
app.py — {name} Startup Landing Page
Generated by WebGen Platform
"""
import os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-in-production")

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            source TEXT DEFAULT 'landing',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)
    # Create default admin if not exists
    admin = conn.execute("SELECT id FROM admins WHERE username='admin'").fetchone()
    if not admin:
        conn.execute("INSERT INTO admins (username, password) VALUES (?,?)",
                     ("admin", generate_password_hash("admin123")))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0]
    conn.close()
    return render_template("index.html", waitlist_count=count)

@app.route("/waitlist", methods=["POST"])
def join_waitlist():
    email = request.form.get("email", "").strip()
    name  = request.form.get("name", "").strip()
    if not email:
        flash("Please enter a valid email.", "error")
        return redirect(url_for("index") + "#waitlist")
    try:
        conn = get_db()
        conn.execute("INSERT INTO waitlist (email, name) VALUES (?,?)", (email, name))
        conn.commit()
        conn.close()
        flash("You are on the list! We will notify you at launch.", "success")
    except Exception:
        flash("You are already on the waitlist!", "info")
    return redirect(url_for("index") + "#waitlist")

@app.route("/contact", methods=["POST"])
def contact():
    name    = request.form.get("name", "")
    email   = request.form.get("email", "")
    message = request.form.get("message", "")
    conn = get_db()
    conn.execute("INSERT INTO contacts (name,email,message) VALUES (?,?,?)", (name,email,message))
    conn.commit()
    conn.close()
    flash("Message received! We will get back to you soon.", "success")
    return redirect(url_for("index") + "#contact")

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        admin = conn.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        conn.close()
        if admin and check_password_hash(admin["password"], password):
            session["admin"] = username
            return redirect(url_for("admin"))
        flash("Invalid credentials.", "error")
    return render_template("admin.html", login=True)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = get_db()
    waitlist = conn.execute("SELECT * FROM waitlist ORDER BY joined_at DESC").fetchall()
    contacts = conn.execute("SELECT * FROM contacts ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("admin.html", login=False, waitlist=waitlist, contacts=contacts)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
'''


def _startup_base_html(name: str, font: str, primary: str, secondary: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{% block title %}}{name}{{% endblock %}}</title>
  <meta name="description" content="{{% block desc %}}Built with WebGen{{% endblock %}}"/>
  <link href="https://fonts.googleapis.com/css2?family={font.replace(' ','+')}:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}"/>
</head>
<body>
<nav class="startup-nav" id="mainNav">
  <div class="nav-inner">
    <a href="/" class="nav-logo">{name}</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="#features">Features</a></li>
      <li><a href="#pricing">Pricing</a></li>
      <li><a href="#faq">FAQ</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
    <a href="#waitlist" class="nav-cta">Get Early Access</a>
    <button class="hamburger" onclick="toggleNav()">&#9776;</button>
  </div>
</nav>
{{%- with messages = get_flashed_messages(with_categories=true) %}}
  {{%- if messages %}}{{%- for cat, msg in messages %}}
    <div class="flash flash-{{{{ cat }}}}">{{{{ msg }}}}</div>
  {{%- endfor %}}{{%- endif %}}
{{%- endwith %}}
{{%- block content %}}{{%- endblock %}}
<footer class="startup-footer">
  <div class="sf-inner">
    <div class="sf-brand"><span class="sf-logo">{name}</span><p>Building the future, one product at a time.</p></div>
    <div class="sf-links"><h4>Product</h4><ul><li><a href="#features">Features</a></li><li><a href="#pricing">Pricing</a></li></ul></div>
    <div class="sf-links"><h4>Company</h4><ul><li><a href="#about">About</a></li><li><a href="#contact">Contact</a></li></ul></div>
  </div>
  <div class="sf-bottom"><p>&copy; 2025 {name}. All rights reserved.</p></div>
</footer>
<script src="{{{{ url_for('static', filename='js/script.js') }}}}"></script>
</body>
</html>"""


def _startup_index_html(name: str, tagline: str, sections: list) -> str:
    parts = ["{{% extends 'base.html' %}}", "{{% block content %}}"]

    # Hero
    parts.append(f"""<section class="startup-hero" id="home">
  <div class="sh-bg-grid"></div>
  <div class="sh-content">
    <div class="sh-badge">✨ Now in Beta</div>
    <h1 class="sh-title">{name}<br/><span class="sh-gradient">Reimagined</span></h1>
    <p class="sh-sub">{tagline}</p>
    <div class="sh-cta">
      <a href="#waitlist" class="btn-hero-primary">Get Early Access →</a>
      <a href="#features" class="btn-hero-outline">See Features</a>
    </div>
    <div class="sh-social-proof">
      <div class="sp-avatars">
        <img src="https://i.pravatar.cc/32?img=1" alt="user"/>
        <img src="https://i.pravatar.cc/32?img=2" alt="user"/>
        <img src="https://i.pravatar.cc/32?img=3" alt="user"/>
        <img src="https://i.pravatar.cc/32?img=4" alt="user"/>
      </div>
      <span>Join <strong>{{{{ waitlist_count + 1200 }}}}</strong> people on the waitlist</span>
    </div>
  </div>
  <div class="sh-visual">
    <div class="sh-mockup">
      <div class="sm-bar"><span></span><span></span><span></span></div>
      <div class="sm-content">
        <div class="sm-row sm-wide"></div>
        <div class="sm-row sm-med"></div>
        <div class="sm-row sm-short"></div>
        <div class="sm-cards">
          <div class="sm-card"></div><div class="sm-card"></div><div class="sm-card"></div>
        </div>
      </div>
    </div>
  </div>
</section>""")

    # Logos bar
    parts.append("""<section class="logos-bar">
  <p>Trusted by teams at</p>
  <div class="logos-row">
    <span>Acme Corp</span><span>TechFlow</span><span>BuildFast</span>
    <span>LaunchPad</span><span>ScaleUp</span>
  </div>
</section>""")

    # Features
    if "services" in sections or "features" in sections:
        parts.append(f"""<section class="startup-features" id="features">
  <div class="container">
    <div class="section-header">
      <span class="section-tag">Features</span>
      <h2>Everything you need to <span class="text-gradient">ship faster</span></h2>
      <p>Powerful tools designed for modern teams.</p>
    </div>
    <div class="features-grid">
      <div class="feature-card fc-highlight">
        <div class="fc-icon">⚡</div>
        <h3>Lightning Fast</h3>
        <p>Built for speed from the ground up. Zero compromises on performance.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">🔐</div>
        <h3>Secure by Default</h3>
        <p>Enterprise-grade security baked in. Your data is always protected.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">🤖</div>
        <h3>AI-Powered</h3>
        <p>Smart automation that learns from your workflow and adapts.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">📊</div>
        <h3>Real-time Analytics</h3>
        <p>Deep insights into every metric that matters to your business.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">🔗</div>
        <h3>Integrations</h3>
        <p>Connect with 100+ tools you already use. Slack, Notion, GitHub and more.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">🌍</div>
        <h3>Global Scale</h3>
        <p>Deploy anywhere. Serve users worldwide with sub-100ms latency.</p>
      </div>
    </div>
  </div>
</section>""")

    # How it works
    parts.append("""<section class="how-it-works" id="how">
  <div class="container">
    <div class="section-header">
      <span class="section-tag">How It Works</span>
      <h2>Up and running in <span class="text-gradient">3 minutes</span></h2>
    </div>
    <div class="steps-row">
      <div class="step-item"><div class="step-num">01</div><h3>Sign Up</h3><p>Create your account in seconds. No credit card required.</p></div>
      <div class="step-arrow">→</div>
      <div class="step-item"><div class="step-num">02</div><h3>Configure</h3><p>Set up your workspace with our guided onboarding flow.</p></div>
      <div class="step-arrow">→</div>
      <div class="step-item"><div class="step-num">03</div><h3>Launch</h3><p>Go live and start seeing results from day one.</p></div>
    </div>
  </div>
</section>""")

    # Pricing
    if "pricing" in sections:
        parts.append("""<section class="startup-pricing" id="pricing">
  <div class="container">
    <div class="section-header">
      <span class="section-tag">Pricing</span>
      <h2>Simple, <span class="text-gradient">transparent</span> pricing</h2>
      <p>No hidden fees. Cancel anytime.</p>
    </div>
    <div class="pricing-grid">
      <div class="pricing-card">
        <div class="pc-name">Starter</div>
        <div class="pc-price"><span>$0</span><small>/month</small></div>
        <ul class="pc-features">
          <li>✓ Up to 3 projects</li><li>✓ 5GB storage</li>
          <li>✓ Basic analytics</li><li>✓ Email support</li>
        </ul>
        <a href="#waitlist" class="pc-btn pc-btn-outline">Get Started Free</a>
      </div>
      <div class="pricing-card pc-popular">
        <div class="pc-badge">Most Popular</div>
        <div class="pc-name">Pro</div>
        <div class="pc-price"><span>$29</span><small>/month</small></div>
        <ul class="pc-features">
          <li>✓ Unlimited projects</li><li>✓ 50GB storage</li>
          <li>✓ Advanced analytics</li><li>✓ Priority support</li>
          <li>✓ API access</li><li>✓ Team collaboration</li>
        </ul>
        <a href="#waitlist" class="pc-btn pc-btn-primary">Start Free Trial</a>
      </div>
      <div class="pricing-card">
        <div class="pc-name">Enterprise</div>
        <div class="pc-price"><span>$99</span><small>/month</small></div>
        <ul class="pc-features">
          <li>✓ Everything in Pro</li><li>✓ Unlimited storage</li>
          <li>✓ Custom integrations</li><li>✓ Dedicated support</li>
          <li>✓ SLA guarantee</li><li>✓ SSO / SAML</li>
        </ul>
        <a href="#contact" class="pc-btn pc-btn-outline">Contact Sales</a>
      </div>
    </div>
  </div>
</section>""")

    # Testimonials
    if "testimonials" in sections:
        parts.append("""<section class="startup-testimonials" id="testimonials">
  <div class="container">
    <div class="section-header">
      <span class="section-tag">Testimonials</span>
      <h2>Loved by <span class="text-gradient">thousands</span> of teams</h2>
    </div>
    <div class="testimonials-grid">
      <div class="t-card"><p>"This product completely transformed how our team works. We ship 3x faster now."</p><div class="t-author"><img src="https://i.pravatar.cc/44?img=5" alt=""/><div><strong>Sarah Chen</strong><span>CTO, TechFlow</span></div></div></div>
      <div class="t-card t-featured"><p>"The best investment we made this year. ROI was visible within the first week."</p><div class="t-author"><img src="https://i.pravatar.cc/44?img=8" alt=""/><div><strong>Marcus Johnson</strong><span>Founder, BuildFast</span></div></div></div>
      <div class="t-card"><p>"Incredibly intuitive. Our non-technical team members use it daily without any training."</p><div class="t-author"><img src="https://i.pravatar.cc/44?img=12" alt=""/><div><strong>Priya Sharma</strong><span>PM, ScaleUp</span></div></div></div>
    </div>
  </div>
</section>""")

    # FAQ
    if "faq" in sections:
        parts.append("""<section class="startup-faq" id="faq">
  <div class="container">
    <div class="section-header">
      <span class="section-tag">FAQ</span>
      <h2>Frequently asked <span class="text-gradient">questions</span></h2>
    </div>
    <div class="faq-list">
      <div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">Is there a free plan? <span>+</span></button><div class="faq-a"><p>Yes! Our Starter plan is completely free forever with no credit card required.</p></div></div>
      <div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">Can I cancel anytime? <span>+</span></button><div class="faq-a"><p>Absolutely. No contracts, no lock-in. Cancel with one click from your dashboard.</p></div></div>
      <div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">Do you offer a free trial? <span>+</span></button><div class="faq-a"><p>Yes, all paid plans come with a 14-day free trial. No credit card needed to start.</p></div></div>
      <div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">How secure is my data? <span>+</span></button><div class="faq-a"><p>We use AES-256 encryption at rest and TLS 1.3 in transit. SOC 2 Type II certified.</p></div></div>
    </div>
  </div>
</section>""")

    # Waitlist CTA
    parts.append(f"""<section class="waitlist-section" id="waitlist">
  <div class="container">
    <div class="wl-card">
      <h2>Be the first to experience <span class="text-gradient">{name}</span></h2>
      <p>Join the waitlist and get 3 months free when we launch.</p>
      <form class="wl-form" method="POST" action="/waitlist">
        <input type="text" name="name" placeholder="Your name (optional)"/>
        <input type="email" name="email" placeholder="Enter your email" required/>
        <button type="submit" class="btn-hero-primary">Join Waitlist →</button>
      </form>
      <p class="wl-note">🔒 No spam. Unsubscribe anytime.</p>
    </div>
  </div>
</section>""")

    # Contact
    if "contact" in sections:
        parts.append("""<section class="startup-contact" id="contact">
  <div class="container">
    <div class="section-header">
      <span class="section-tag">Contact</span>
      <h2>Get in <span class="text-gradient">touch</span></h2>
    </div>
    <form class="contact-form-startup" method="POST" action="/contact">
      <div class="cf-row">
        <input type="text" name="name" placeholder="Your Name" required/>
        <input type="email" name="email" placeholder="Your Email" required/>
      </div>
      <textarea name="message" rows="5" placeholder="Your message..." required></textarea>
      <button type="submit" class="btn-hero-primary">Send Message</button>
    </form>
  </div>
</section>""")

    parts.append("{{% endblock %}}")
    return "\n\n".join(parts)


def _startup_admin_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block content %}}
{{% if login %}}
<section style="min-height:80vh;display:flex;align-items:center;justify-content:center">
  <div style="background:#fff;padding:2.5rem;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.1);width:100%;max-width:380px">
    <h2 style="text-align:center;margin-bottom:1.5rem;color:var(--primary)">Admin Login</h2>
    <form method="POST">
      <div style="margin-bottom:1rem"><label style="display:block;margin-bottom:.4rem;font-size:.9rem">Username</label><input name="username" type="text" style="width:100%;padding:.75rem;border:1px solid #ddd;border-radius:8px" required/></div>
      <div style="margin-bottom:1.5rem"><label style="display:block;margin-bottom:.4rem;font-size:.9rem">Password</label><input name="password" type="password" style="width:100%;padding:.75rem;border:1px solid #ddd;border-radius:8px" required/></div>
      <button type="submit" style="width:100%;padding:.8rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;cursor:pointer">Login</button>
    </form>
  </div>
</section>
{{% else %}}
<div style="max-width:1000px;margin:2rem auto;padding:0 1.5rem">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem">
    <h2>Admin Dashboard</h2>
    <a href="/admin/logout" style="color:#e53935;font-size:.9rem">Logout</a>
  </div>
  <h3 style="margin-bottom:1rem">Waitlist ({{{{ waitlist|length }}}} signups)</h3>
  <table style="width:100%;border-collapse:collapse;margin-bottom:2rem;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06)">
    <thead><tr style="background:var(--primary);color:#fff"><th style="padding:.75rem 1rem;text-align:left">Name</th><th style="padding:.75rem 1rem;text-align:left">Email</th><th style="padding:.75rem 1rem;text-align:left">Joined</th></tr></thead>
    <tbody>
    {{% for w in waitlist %}}
    <tr style="border-bottom:1px solid #f0f0f0"><td style="padding:.65rem 1rem">{{{{ w.name or '—' }}}}</td><td style="padding:.65rem 1rem">{{{{ w.email }}}}</td><td style="padding:.65rem 1rem;font-size:.82rem;color:#888">{{{{ w.joined_at }}}}</td></tr>
    {{% endfor %}}
    </tbody>
  </table>
  <h3 style="margin-bottom:1rem">Contact Messages ({{{{ contacts|length }}}})</h3>
  <table style="width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06)">
    <thead><tr style="background:var(--primary);color:#fff"><th style="padding:.75rem 1rem;text-align:left">Name</th><th style="padding:.75rem 1rem;text-align:left">Email</th><th style="padding:.75rem 1rem;text-align:left">Message</th><th style="padding:.75rem 1rem;text-align:left">Date</th></tr></thead>
    <tbody>
    {{% for c in contacts %}}
    <tr style="border-bottom:1px solid #f0f0f0"><td style="padding:.65rem 1rem">{{{{ c.name }}}}</td><td style="padding:.65rem 1rem">{{{{ c.email }}}}</td><td style="padding:.65rem 1rem;font-size:.85rem">{{{{ c.message[:80] }}}}...</td><td style="padding:.65rem 1rem;font-size:.82rem;color:#888">{{{{ c.created_at }}}}</td></tr>
    {{% endfor %}}
    </tbody>
  </table>
</div>
{{% endif %}}
{{% endblock %}}"""


def _startup_css(primary: str, secondary: str, font: str) -> str:
    return f"""/* {font} Startup Landing — Generated by WebGen */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--primary:{primary};--secondary:{secondary};--bg:#0a0a0f;--surface:#111118;--surface2:#1a1a24;--border:#2a2a3a;--text:#f0f0f8;--muted:#8888aa}}
body{{font-family:'{font}',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;overflow-x:hidden}}
a{{text-decoration:none;color:inherit}}
img{{max-width:100%;display:block}}
.container{{max-width:1100px;margin:0 auto;padding:0 1.5rem}}
.text-gradient{{background:linear-gradient(135deg,var(--primary),var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}

/* Nav */
.startup-nav{{position:fixed;top:0;left:0;right:0;z-index:200;padding:.85rem 0;transition:background .3s,box-shadow .3s}}
.startup-nav.scrolled{{background:rgba(10,10,15,.95);backdrop-filter:blur(12px);box-shadow:0 1px 0 var(--border)}}
.nav-inner{{max-width:1200px;margin:0 auto;padding:0 1.5rem;display:flex;align-items:center;gap:2rem}}
.nav-logo{{font-size:1.2rem;font-weight:800;background:linear-gradient(135deg,var(--primary),var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.nav-links{{list-style:none;display:flex;gap:1.75rem;margin-left:auto}}
.nav-links a{{color:var(--muted);font-size:.9rem;transition:color .2s}}
.nav-links a:hover{{color:var(--text)}}
.nav-cta{{padding:.5rem 1.25rem;border-radius:20px;background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;font-size:.88rem;font-weight:600;transition:transform .2s,box-shadow .2s;white-space:nowrap}}
.nav-cta:hover{{transform:translateY(-1px);box-shadow:0 4px 16px rgba(108,99,255,.4)}}
.hamburger{{display:none;background:none;border:none;color:var(--text);font-size:1.4rem;cursor:pointer;margin-left:auto}}

/* Hero */
.startup-hero{{min-height:100vh;display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:3rem;padding:8rem 1.5rem 4rem;max-width:1200px;margin:0 auto;position:relative}}
.sh-bg-grid{{position:fixed;inset:0;background-image:linear-gradient(rgba(108,99,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(108,99,255,.04) 1px,transparent 1px);background-size:60px 60px;pointer-events:none;z-index:-1}}
.sh-badge{{display:inline-flex;align-items:center;gap:.4rem;padding:.35rem .9rem;border-radius:20px;border:1px solid rgba(108,99,255,.3);background:rgba(108,99,255,.08);color:var(--primary);font-size:.82rem;margin-bottom:1.25rem}}
.sh-title{{font-size:clamp(2.5rem,5vw,4rem);font-weight:800;line-height:1.1;margin-bottom:1.25rem}}
.sh-sub{{font-size:1.1rem;color:var(--muted);margin-bottom:2rem;max-width:480px;line-height:1.7}}
.sh-cta{{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:2rem}}
.btn-hero-primary{{padding:.8rem 2rem;border-radius:30px;background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;font-weight:700;font-size:1rem;transition:transform .2s,box-shadow .2s;display:inline-block}}
.btn-hero-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(108,99,255,.4)}}
.btn-hero-outline{{padding:.8rem 2rem;border-radius:30px;border:1px solid var(--border);color:var(--text);font-size:1rem;transition:border-color .2s;display:inline-block}}
.btn-hero-outline:hover{{border-color:var(--primary);color:var(--primary)}}
.sh-social-proof{{display:flex;align-items:center;gap:.75rem;font-size:.88rem;color:var(--muted)}}
.sp-avatars{{display:flex}}
.sp-avatars img{{width:28px;height:28px;border-radius:50%;border:2px solid var(--bg);margin-left:-6px}}
.sp-avatars img:first-child{{margin-left:0}}
.sh-social-proof strong{{color:var(--text)}}

/* Mockup */
.sh-visual{{display:flex;justify-content:center}}
.sh-mockup{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1rem;width:100%;max-width:420px;box-shadow:0 24px 64px rgba(0,0,0,.4)}}
.sm-bar{{display:flex;gap:.4rem;margin-bottom:1rem}}
.sm-bar span{{width:10px;height:10px;border-radius:50%;background:var(--border)}}
.sm-bar span:nth-child(1){{background:#ff5f57}}
.sm-bar span:nth-child(2){{background:#febc2e}}
.sm-bar span:nth-child(3){{background:#28c840}}
.sm-row{{height:10px;border-radius:4px;background:var(--surface2);margin-bottom:.6rem}}
.sm-wide{{width:80%}}.sm-med{{width:60%}}.sm-short{{width:40%}}
.sm-cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin-top:1rem}}
.sm-card{{height:60px;border-radius:8px;background:linear-gradient(135deg,rgba(108,99,255,.2),rgba(245,0,87,.1))}}

/* Logos */
.logos-bar{{text-align:center;padding:2.5rem 1.5rem;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}}
.logos-bar p{{color:var(--muted);font-size:.85rem;margin-bottom:1.25rem}}
.logos-row{{display:flex;justify-content:center;gap:2.5rem;flex-wrap:wrap}}
.logos-row span{{color:var(--muted);font-weight:700;font-size:1rem;letter-spacing:.05em;opacity:.5}}

/* Section header */
.section-header{{text-align:center;margin-bottom:3rem}}
.section-tag{{display:inline-block;padding:.25rem .85rem;border-radius:20px;background:rgba(108,99,255,.12);color:var(--primary);font-size:.78rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.75rem}}
.section-header h2{{font-size:clamp(1.8rem,3.5vw,2.6rem);font-weight:800;margin-bottom:.75rem}}
.section-header p{{color:var(--muted);font-size:1rem;max-width:520px;margin:0 auto}}

/* Features */
.startup-features{{padding:6rem 0}}
.features-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.25rem}}
.feature-card{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.75rem;transition:border-color .2s,transform .2s}}
.feature-card:hover{{border-color:var(--primary);transform:translateY(-3px)}}
.fc-highlight{{background:linear-gradient(135deg,rgba(108,99,255,.12),rgba(245,0,87,.06));border-color:rgba(108,99,255,.3)}}
.fc-icon{{font-size:1.8rem;margin-bottom:.85rem}}
.feature-card h3{{font-size:1.05rem;margin-bottom:.5rem}}
.feature-card p{{color:var(--muted);font-size:.9rem;line-height:1.6}}

/* How it works */
.how-it-works{{padding:5rem 0;background:var(--surface)}}
.steps-row{{display:flex;align-items:center;justify-content:center;gap:1.5rem;flex-wrap:wrap}}
.step-item{{text-align:center;max-width:200px}}
.step-num{{font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,var(--primary),var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.5rem}}
.step-item h3{{margin-bottom:.4rem}}
.step-item p{{color:var(--muted);font-size:.88rem}}
.step-arrow{{font-size:1.5rem;color:var(--muted)}}

/* Pricing */
.startup-pricing{{padding:6rem 0}}
.pricing-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem;max-width:900px;margin:0 auto}}
.pricing-card{{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:2rem;position:relative}}
.pc-popular{{border-color:var(--primary);background:linear-gradient(135deg,rgba(108,99,255,.1),rgba(245,0,87,.05))}}
.pc-badge{{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;padding:.25rem .85rem;border-radius:20px;font-size:.75rem;font-weight:700;white-space:nowrap}}
.pc-name{{font-size:.9rem;font-weight:600;color:var(--muted);margin-bottom:.5rem}}
.pc-price{{margin-bottom:1.5rem}}
.pc-price span{{font-size:2.5rem;font-weight:800}}
.pc-price small{{color:var(--muted);font-size:.9rem}}
.pc-features{{list-style:none;display:flex;flex-direction:column;gap:.6rem;margin-bottom:1.75rem}}
.pc-features li{{font-size:.9rem;color:var(--muted)}}
.pc-btn{{display:block;text-align:center;padding:.75rem;border-radius:10px;font-weight:600;font-size:.95rem;transition:all .2s}}
.pc-btn-primary{{background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff}}
.pc-btn-outline{{border:1px solid var(--border);color:var(--text)}}
.pc-btn-outline:hover{{border-color:var(--primary);color:var(--primary)}}

/* Testimonials */
.startup-testimonials{{padding:6rem 0;background:var(--surface)}}
.testimonials-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.25rem}}
.t-card{{background:var(--surface2);border:1px solid var(--border);border-radius:16px;padding:1.75rem}}
.t-featured{{border-color:rgba(108,99,255,.4);background:linear-gradient(135deg,rgba(108,99,255,.08),rgba(245,0,87,.04))}}
.t-card p{{color:var(--muted);font-style:italic;margin-bottom:1.25rem;line-height:1.7}}
.t-author{{display:flex;align-items:center;gap:.75rem}}
.t-author img{{width:40px;height:40px;border-radius:50%}}
.t-author strong{{display:block;font-size:.9rem}}
.t-author span{{font-size:.8rem;color:var(--muted)}}

/* FAQ */
.startup-faq{{padding:6rem 0}}
.faq-list{{max-width:700px;margin:0 auto;display:flex;flex-direction:column;gap:.75rem}}
.faq-item{{background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden}}
.faq-q{{width:100%;padding:1.1rem 1.25rem;background:transparent;border:none;color:var(--text);font-size:.95rem;font-weight:500;text-align:left;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-family:inherit}}
.faq-q span{{font-size:1.2rem;color:var(--primary);transition:transform .2s}}
.faq-q.open span{{transform:rotate(45deg)}}
.faq-a{{display:none;padding:0 1.25rem 1.1rem}}
.faq-a p{{color:var(--muted);font-size:.9rem;line-height:1.7}}
.faq-a.open{{display:block}}

/* Waitlist */
.waitlist-section{{padding:6rem 0}}
.wl-card{{background:linear-gradient(135deg,rgba(108,99,255,.12),rgba(245,0,87,.06));border:1px solid rgba(108,99,255,.25);border-radius:24px;padding:3.5rem;text-align:center;max-width:680px;margin:0 auto}}
.wl-card h2{{font-size:clamp(1.6rem,3vw,2.2rem);font-weight:800;margin-bottom:.75rem}}
.wl-card p{{color:var(--muted);margin-bottom:2rem}}
.wl-form{{display:flex;gap:.75rem;flex-wrap:wrap;justify-content:center;margin-bottom:1rem}}
.wl-form input{{padding:.75rem 1.25rem;border-radius:10px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:.95rem;font-family:inherit;min-width:200px;flex:1}}
.wl-form input:focus{{outline:none;border-color:var(--primary)}}
.wl-note{{font-size:.82rem;color:var(--muted)}}

/* Contact */
.startup-contact{{padding:6rem 0;background:var(--surface)}}
.contact-form-startup{{max-width:600px;margin:0 auto;display:flex;flex-direction:column;gap:1rem}}
.cf-row{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}
.contact-form-startup input,.contact-form-startup textarea{{padding:.85rem 1rem;border:1px solid var(--border);border-radius:10px;background:var(--surface2);color:var(--text);font-size:.95rem;font-family:inherit}}
.contact-form-startup input:focus,.contact-form-startup textarea:focus{{outline:none;border-color:var(--primary)}}

/* Footer */
.startup-footer{{border-top:1px solid var(--border);padding:3rem 0 1.5rem}}
.sf-inner{{max-width:1100px;margin:0 auto;padding:0 1.5rem;display:grid;grid-template-columns:2fr 1fr 1fr;gap:2rem;margin-bottom:2rem}}
.sf-logo{{font-size:1.2rem;font-weight:800;background:linear-gradient(135deg,var(--primary),var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:block;margin-bottom:.5rem}}
.sf-brand p{{color:var(--muted);font-size:.88rem}}
.sf-links h4{{font-size:.85rem;font-weight:600;margin-bottom:.75rem;color:var(--muted)}}
.sf-links ul{{list-style:none;display:flex;flex-direction:column;gap:.4rem}}
.sf-links a{{color:var(--muted);font-size:.88rem;transition:color .2s}}
.sf-links a:hover{{color:var(--text)}}
.sf-bottom{{border-top:1px solid var(--border);padding-top:1.25rem;text-align:center;color:var(--muted);font-size:.82rem;max-width:1100px;margin:0 auto;padding-left:1.5rem;padding-right:1.5rem}}

/* Flash */
.flash{{padding:.75rem 1.5rem;text-align:center;font-size:.9rem;font-weight:500}}
.flash-success{{background:rgba(76,175,80,.15);color:#81c784;border-bottom:1px solid rgba(76,175,80,.2)}}
.flash-error{{background:rgba(244,67,54,.15);color:#ef9a9a;border-bottom:1px solid rgba(244,67,54,.2)}}
.flash-info{{background:rgba(33,150,243,.15);color:#90caf9;border-bottom:1px solid rgba(33,150,243,.2)}}

/* Responsive */
@media(max-width:900px){{
  .startup-hero{{grid-template-columns:1fr;text-align:center;padding-top:6rem}}
  .sh-sub,.sh-cta,.sh-social-proof{{margin-left:auto;margin-right:auto;justify-content:center}}
  .sh-visual{{display:none}}
  .sf-inner{{grid-template-columns:1fr}}
  .cf-row{{grid-template-columns:1fr}}
}}
@media(max-width:600px){{
  .nav-links{{display:none;flex-direction:column;position:fixed;top:60px;left:0;right:0;background:rgba(10,10,15,.98);padding:1.5rem;gap:1rem}}
  .nav-links.open{{display:flex}}
  .hamburger{{display:block}}
  .nav-cta{{display:none}}
  .pricing-grid{{grid-template-columns:1fr}}
  .wl-form{{flex-direction:column}}
}}"""


def _startup_js() -> str:
    return """// Startup Landing JS — Generated by WebGen

// Sticky nav on scroll
window.addEventListener('scroll', () => {
  document.getElementById('mainNav').classList.toggle('scrolled', window.scrollY > 50);
});

// Mobile nav
function toggleNav() {
  document.getElementById('navLinks').classList.toggle('open');
}

// FAQ accordion
function toggleFaq(btn) {
  const item = btn.closest('.faq-item');
  const answer = item.querySelector('.faq-a');
  const isOpen = answer.classList.contains('open');
  // Close all
  document.querySelectorAll('.faq-a').forEach(a => a.classList.remove('open'));
  document.querySelectorAll('.faq-q').forEach(b => b.classList.remove('open'));
  if (!isOpen) {
    answer.classList.add('open');
    btn.classList.add('open');
  }
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});

// Scroll reveal
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.feature-card, .pricing-card, .t-card, .step-item, .faq-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(28px)';
  el.style.transition = 'opacity .6s ease, transform .6s ease';
  observer.observe(el);
});

// Number counter animation
function animateCounter(el, target) {
  let current = 0;
  const step = Math.ceil(target / 60);
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = current.toLocaleString();
    if (current >= target) clearInterval(timer);
  }, 16);
}
document.querySelectorAll('[data-count]').forEach(el => {
  const io = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      animateCounter(el, parseInt(el.dataset.count));
      io.disconnect();
    }
  });
  io.observe(el);
});
"""


def _readme_startup(name: str) -> str:
    return f"""{name} — Startup Landing Page
Generated by WebGen Platform

HOW TO RUN:
  1. pip install -r requirements.txt
  2. python app.py
  3. Open http://localhost:5000

ADMIN PANEL:
  - Visit http://localhost:5000/admin/login
  - Default credentials: admin / admin123
  - Change password in app.py before deploying!

FEATURES:
  - Waitlist email capture with SQLite storage
  - Contact form with database storage
  - Admin panel to view signups and messages
  - Responsive dark SaaS design
  - FAQ accordion, pricing cards, testimonials
"""


# ─────────────────────────────────────────────────────────────────────────────
# 5. BLOG CMS GENERATOR
# ─────────────────────────────────────────────────────────────────────────────


def _gen_blog(config: dict) -> dict:
    """Generate a full Blog CMS with Flask + SQLite + admin panel."""
    name    = _c(config, "site_name", "My Blog")
    primary = _c(config, "primary_color", "#6c63ff")
    secondary = _c(config, "secondary_color", "#f50057")
    font    = _c(config, "font", "Inter")
    return {
        "app.py":                      _blog_app_py(name),
        "templates/base.html":         _blog_base_html(name, font, primary),
        "templates/index.html":        _blog_index_html(),
        "templates/post.html":         _blog_post_html(),
        "templates/admin.html":        _blog_admin_html(),
        "templates/admin_post.html":   _blog_admin_post_html(),
        "templates/login.html":        _blog_login_html(),
        "static/css/style.css":        _base_css(primary, secondary, font) + _blog_extra_css(),
        "static/js/script.js":         _base_js(),
        "requirements.txt":            "Flask==3.0.0\nWerkzeug==3.0.1\n",
        "README.txt":                  _readme_blog(name),
    }


def _blog_app_py(name: str) -> str:
    return f'''"""
app.py — {name} Blog CMS
Generated by WebGen Platform
"""
import os, sqlite3, re
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, abort)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-production")
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\\w\\s-]", "", text)
    return re.sub(r"[\\s_-]+", "-", text)

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL REFERENCES users(id),
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            excerpt TEXT,
            category TEXT DEFAULT 'General',
            tags TEXT,
            status TEXT DEFAULT 'draft',
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL REFERENCES posts(id),
            author_name TEXT NOT NULL,
            author_email TEXT NOT NULL,
            content TEXT NOT NULL,
            approved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── Public routes ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    conn = get_db()
    category = request.args.get("category", "")
    if category:
        posts = conn.execute(
            "SELECT * FROM posts WHERE status=\\'published\\' AND category=? ORDER BY published_at DESC",
            (category,)).fetchall()
    else:
        posts = conn.execute(
            "SELECT * FROM posts WHERE status=\\'published\\' ORDER BY published_at DESC").fetchall()
    categories = conn.execute(
        "SELECT DISTINCT category FROM posts WHERE status=\\'published\\'").fetchall()
    conn.close()
    return render_template("index.html", posts=posts, categories=categories,
                           selected_category=category)

@app.route("/post/<slug>")
def post(slug):
    conn = get_db()
    p = conn.execute("SELECT * FROM posts WHERE slug=? AND status=\\'published\\'", (slug,)).fetchone()
    if not p:
        abort(404)
    comments = conn.execute(
        "SELECT * FROM comments WHERE post_id=? AND approved=1 ORDER BY created_at",
        (p["id"],)).fetchall()
    conn.close()
    return render_template("post.html", post=p, comments=comments)

@app.route("/post/<int:pid>/comment", methods=["POST"])
def add_comment(pid):
    name    = request.form.get("name", "").strip()
    email   = request.form.get("email", "").strip()
    content = request.form.get("content", "").strip()
    if name and email and content:
        conn = get_db()
        conn.execute("INSERT INTO comments (post_id,author_name,author_email,content) VALUES (?,?,?,?)",
                     (pid, name, email, content))
        conn.commit()
        conn.close()
        flash("Comment submitted! Awaiting moderation.", "success")
    return redirect(url_for("post", slug=request.form.get("slug", "")))

# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"]   = user["id"]
            session["username"]  = user["username"]
            return redirect(url_for("admin"))
        flash("Invalid credentials.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ── Admin ─────────────────────────────────────────────────────────────────────
@app.route("/admin")
@login_required
def admin():
    conn = get_db()
    posts    = conn.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    comments = conn.execute(
        "SELECT c.*, p.title as post_title FROM comments c JOIN posts p ON c.post_id=p.id ORDER BY c.created_at DESC"
    ).fetchall()
    conn.close()
    return render_template("admin.html", posts=posts, comments=comments)

@app.route("/admin/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title    = request.form["title"]
        content  = request.form["content"]
        category = request.form.get("category", "General")
        excerpt  = request.form.get("excerpt", content[:150])
        status   = request.form.get("status", "draft")
        slug     = slugify(title)
        pub_at   = datetime.now() if status == "published" else None
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO posts (author_id,title,slug,content,excerpt,category,status,published_at) VALUES (?,?,?,?,?,?,?,?)",
                (session["user_id"], title, slug, content, excerpt, category, status, pub_at))
            conn.commit()
            flash("Post created!", "success")
        except Exception:
            flash("Slug already exists. Change the title.", "error")
        conn.close()
        return redirect(url_for("admin"))
    return render_template("admin_post.html", post=None)

@app.route("/admin/post/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def edit_post(pid):
    conn = get_db()
    p = conn.execute("SELECT * FROM posts WHERE id=?", (pid,)).fetchone()
    if not p:
        conn.close()
        abort(404)
    if request.method == "POST":
        title    = request.form["title"]
        content  = request.form["content"]
        category = request.form.get("category", "General")
        excerpt  = request.form.get("excerpt", content[:150])
        status   = request.form.get("status", "draft")
        pub_at   = datetime.now() if status == "published" and not p["published_at"] else p["published_at"]
        conn.execute(
            "UPDATE posts SET title=?,content=?,category=?,excerpt=?,status=?,published_at=? WHERE id=?",
            (title, content, category, excerpt, status, pub_at, pid))
        conn.commit()
        conn.close()
        flash("Post updated!", "success")
        return redirect(url_for("admin"))
    conn.close()
    return render_template("admin_post.html", post=p)

@app.route("/admin/post/delete/<int:pid>", methods=["POST"])
@login_required
def delete_post(pid):
    conn = get_db()
    conn.execute("DELETE FROM posts WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    flash("Post deleted.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/comment/approve/<int:cid>", methods=["POST"])
@login_required
def approve_comment(cid):
    conn = get_db()
    conn.execute("UPDATE comments SET approved=1 WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/admin/comment/delete/<int:cid>", methods=["POST"])
@login_required
def delete_comment(cid):
    conn = get_db()
    conn.execute("DELETE FROM comments WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
'''


def _blog_base_html(name: str, font: str, primary: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{% block title %}}{name}{{% endblock %}}</title>
  <link href="https://fonts.googleapis.com/css2?family={font.replace(' ','+')}:wght@400;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}"/>
</head>
<body>
<header class="site-header">
  <nav class="navbar">
    <a href="{{{{ url_for('index') }}}}" class="logo">{name}</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="{{{{ url_for('index') }}}}">Home</a></li>
      <li><a href="{{{{ url_for('index', category='Tech') }}}}">Tech</a></li>
      <li><a href="{{{{ url_for('index', category='Design') }}}}">Design</a></li>
      <li><a href="{{{{ url_for('index', category='Business') }}}}">Business</a></li>
    </ul>
    <a href="{{{{ url_for('login') }}}}" class="btn-primary btn-sm">Admin</a>
    <button class="hamburger" onclick="toggleNav()">&#9776;</button>
  </nav>
</header>
{{%- with messages = get_flashed_messages(with_categories=true) %}}
  {{%- if messages %}}{{%- for cat, msg in messages %}}
    <div class="flash flash-{{{{ cat }}}}">{{{{ msg }}}}</div>
  {{%- endfor %}}{{%- endif %}}
{{%- endwith %}}
{{%- block content %}}{{%- endblock %}}
<footer class="site-footer">
  <div class="footer-bottom"><p>&copy; 2025 {name}. All rights reserved.</p></div>
</footer>
<script src="{{{{ url_for('static', filename='js/script.js') }}}}"></script>
</body>
</html>"""


def _blog_index_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block content %}}
<section class="blog-hero section">
  <div class="container">
    <h1 class="section-title">Latest Posts</h1>
    {{% if categories %}}
    <div class="category-bar">
      <a href="{{{{ url_for('index') }}}}" class="cat-btn {{% if not selected_category %}}active{{% endif %}}">All</a>
      {{% for c in categories %}}<a href="{{{{ url_for('index', category=c.category) }}}}" class="cat-btn {{% if selected_category==c.category %}}active{{% endif %}}">{{{{ c.category }}}}</a>{{% endfor %}}
    </div>
    {{% endif %}}
    {{% if posts %}}
    <div class="cards-grid">
      {{% for post in posts %}}
      <article class="card">
        <span class="tag">{{{{ post.category }}}}</span>
        <h3><a href="{{{{ url_for('post', slug=post.slug) }}}}">{{{{ post.title }}}}</a></h3>
        <p>{{{{ post.excerpt or post.content[:120] }}}}</p>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:1rem">
          <span style="font-size:.82rem;color:#888">{{{{ post.published_at[:10] if post.published_at else '' }}}}</span>
          <a href="{{{{ url_for('post', slug=post.slug) }}}}" class="read-more">Read more →</a>
        </div>
      </article>
      {{% endfor %}}
    </div>
    {{% else %}}<p style="text-align:center;color:#888;padding:3rem">No posts yet.</p>{{% endif %}}
  </div>
</section>
{{% endblock %}}"""


def _blog_post_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}{{{{ post.title }}}}{{% endblock %}}
{{% block content %}}
<article class="post-page section">
  <div class="container post-container">
    <div class="post-meta"><span class="tag">{{{{ post.category }}}}</span> <span>{{{{ post.published_at[:10] if post.published_at else '' }}}}</span></div>
    <h1 class="post-title">{{{{ post.title }}}}</h1>
    <div class="post-content">{{{{ post.content | replace('\\n','<br>') | safe }}}}</div>
    <div class="post-comments">
      <h3>Comments ({{{{ comments|length }}}})</h3>
      {{% for c in comments %}}
      <div class="comment"><strong>{{{{ c.author_name }}}}</strong><span>{{{{ c.created_at[:10] }}}}</span><p>{{{{ c.content }}}}</p></div>
      {{% endfor %}}
      <h4 style="margin-top:2rem">Leave a Comment</h4>
      <form method="POST" action="{{{{ url_for('add_comment', pid=post.id) }}}}" class="contact-form">
        <input type="hidden" name="slug" value="{{{{ post.slug }}}}"/>
        <input name="name" type="text" placeholder="Your Name" required/>
        <input name="email" type="email" placeholder="Your Email" required/>
        <textarea name="content" rows="4" placeholder="Your comment..." required></textarea>
        <button type="submit" class="btn-primary">Post Comment</button>
      </form>
    </div>
  </div>
</article>
{{% endblock %}}"""


def _blog_admin_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}Admin — Dashboard{{% endblock %}}
{{% block content %}}
<section class="section">
  <div class="container">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem">
      <h2>Admin Dashboard</h2>
      <div style="display:flex;gap:.75rem">
        <a href="{{{{ url_for('new_post') }}}}" class="btn-primary">+ New Post</a>
        <a href="{{{{ url_for('logout') }}}}" class="btn-primary" style="background:#e53935">Logout</a>
      </div>
    </div>
    <h3 style="margin-bottom:1rem">Posts</h3>
    <table style="width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.07)">
      <thead><tr style="background:var(--primary);color:#fff"><th style="padding:.65rem 1rem;text-align:left">Title</th><th>Category</th><th>Status</th><th>Date</th><th>Actions</th></tr></thead>
      <tbody>
      {{% for p in posts %}}
      <tr style="border-bottom:1px solid #f0f0f0">
        <td style="padding:.65rem 1rem">{{{{ p.title }}}}</td>
        <td style="padding:.65rem 1rem">{{{{ p.category }}}}</td>
        <td style="padding:.65rem 1rem"><span style="padding:.2rem .6rem;border-radius:20px;font-size:.78rem;background:{{'#d4edda' if p.status=='published' else '#fff3cd'}};color:{{'#155724' if p.status=='published' else '#856404'}}">{{{{ p.status }}}}</span></td>
        <td style="padding:.65rem 1rem;font-size:.82rem">{{{{ p.created_at[:10] }}}}</td>
        <td style="padding:.65rem 1rem">
          <a href="{{{{ url_for('edit_post', pid=p.id) }}}}" style="color:var(--primary);margin-right:.5rem">Edit</a>
          <form method="POST" action="{{{{ url_for('delete_post', pid=p.id) }}}}" style="display:inline" onsubmit="return confirm('Delete?')">
            <button type="submit" style="background:none;border:none;color:#e53935;cursor:pointer">Delete</button>
          </form>
        </td>
      </tr>
      {{% endfor %}}
      </tbody>
    </table>
    <h3 style="margin:2rem 0 1rem">Pending Comments</h3>
    {{% for c in comments if not c.approved %}}
    <div style="background:#fff;border:1px solid #eee;border-radius:8px;padding:1rem;margin-bottom:.75rem">
      <strong>{{{{ c.author_name }}}}</strong> on <em>{{{{ c.post_title }}}}</em>
      <p style="margin:.5rem 0;color:#555">{{{{ c.content }}}}</p>
      <form method="POST" action="{{{{ url_for('approve_comment', cid=c.id) }}}}" style="display:inline">
        <button type="submit" class="btn-primary btn-sm">Approve</button>
      </form>
      <form method="POST" action="{{{{ url_for('delete_comment', cid=c.id) }}}}" style="display:inline">
        <button type="submit" class="btn-primary btn-sm" style="background:#e53935">Delete</button>
      </form>
    </div>
    {{% else %}}<p style="color:#888">No pending comments.</p>
    {{% endfor %}}
  </div>
</section>
{{% endblock %}}"""


def _blog_admin_post_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}{{% if post %}}Edit Post{{% else %}}New Post{{% endif %}}{{% endblock %}}
{{% block content %}}
<section class="section">
  <div class="container" style="max-width:800px">
    <h2>{{% if post %}}Edit Post{{% else %}}New Post{{% endif %}}</h2>
    <form method="POST" style="display:flex;flex-direction:column;gap:1rem;margin-top:1.5rem">
      <div><label style="display:block;margin-bottom:.4rem;font-weight:500">Title *</label>
        <input name="title" type="text" value="{{% if post %}}{{{{ post.title }}}}{{% endif %}}" required style="width:100%;padding:.75rem;border:1px solid #ddd;border-radius:8px;font-size:1rem"/></div>
      <div><label style="display:block;margin-bottom:.4rem;font-weight:500">Category</label>
        <input name="category" type="text" value="{{% if post %}}{{{{ post.category }}}}{{% else %}}General{{% endif %}}" style="width:100%;padding:.75rem;border:1px solid #ddd;border-radius:8px"/></div>
      <div><label style="display:block;margin-bottom:.4rem;font-weight:500">Excerpt</label>
        <input name="excerpt" type="text" value="{{% if post %}}{{{{ post.excerpt or '' }}}}{{% endif %}}" placeholder="Short summary..." style="width:100%;padding:.75rem;border:1px solid #ddd;border-radius:8px"/></div>
      <div><label style="display:block;margin-bottom:.4rem;font-weight:500">Content *</label>
        <textarea name="content" rows="15" required style="width:100%;padding:.75rem;border:1px solid #ddd;border-radius:8px;font-size:.95rem;font-family:inherit">{{% if post %}}{{{{ post.content }}}}{{% endif %}}</textarea></div>
      <div><label style="display:block;margin-bottom:.4rem;font-weight:500">Status</label>
        <select name="status" style="padding:.75rem;border:1px solid #ddd;border-radius:8px">
          <option value="draft" {{% if not post or post.status=='draft' %}}selected{{% endif %}}>Draft</option>
          <option value="published" {{% if post and post.status=='published' %}}selected{{% endif %}}>Published</option>
        </select></div>
      <div style="display:flex;gap:1rem">
        <button type="submit" class="btn-primary">Save Post</button>
        <a href="{{{{ url_for('admin') }}}}" class="btn-primary" style="background:#888">Cancel</a>
      </div>
    </form>
  </div>
</section>
{{% endblock %}}"""


def _blog_login_html() -> str:
    return """{{% extends 'base.html' %}}
{{% block title %}}Admin Login{{% endblock %}}
{{% block content %}}
<section class="auth-section">
  <div class="auth-card">
    <h2>Admin Login</h2>
    <form method="POST">
      <div class="form-group"><label>Username</label><input name="username" type="text" required/></div>
      <div class="form-group"><label>Password</label><input name="password" type="password" required/></div>
      <button type="submit" class="btn-primary" style="width:100%">Login</button>
    </form>
  </div>
</section>
{{% endblock %}}"""


def _blog_extra_css() -> str:
    return """
.blog-hero{padding:3rem 0 1rem}
.category-bar{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:2rem}
.cat-btn{padding:.35rem .9rem;border-radius:20px;border:1px solid var(--border);background:#fff;color:#555;font-size:.85rem;text-decoration:none;transition:all .2s}
.cat-btn.active,.cat-btn:hover{background:var(--primary);color:#fff;border-color:var(--primary)}
.post-page{padding:3rem 0}
.post-container{max-width:780px}
.post-meta{display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;font-size:.85rem;color:#888}
.post-title{font-size:2rem;margin-bottom:1.5rem;line-height:1.3}
.post-content{font-size:1.05rem;line-height:1.9;color:#444}
.post-comments{margin-top:3rem;padding-top:2rem;border-top:1px solid #eee}
.post-comments h3{margin-bottom:1.25rem}
.comment{padding:1rem;background:#f9f9f9;border-radius:8px;margin-bottom:.75rem}
.comment strong{display:block;margin-bottom:.25rem}
.comment span{font-size:.78rem;color:#888}
.comment p{margin-top:.4rem;color:#555}
.auth-section{min-height:80vh;display:flex;align-items:center;justify-content:center}
.auth-card{background:#fff;padding:2.5rem;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.1);width:100%;max-width:420px}
.auth-card h2{text-align:center;margin-bottom:1.5rem;color:var(--primary)}
.form-group{margin-bottom:1rem}
.form-group label{display:block;margin-bottom:.4rem;font-size:.88rem;font-weight:500}
.form-group input{width:100%;padding:.75rem 1rem;border:1px solid #ddd;border-radius:8px;font-size:.95rem}
.flash{padding:.75rem 1.5rem;text-align:center;font-weight:500}
.flash-success{background:#d4edda;color:#155724}
.flash-error{background:#f8d7da;color:#721c24}
"""


def _readme_blog(name: str) -> str:
    return f"""{name} — Blog CMS
Generated by WebGen Platform

HOW TO RUN:
  1. pip install -r requirements.txt
  2. python app.py
  3. Open http://localhost:5000

ADMIN SETUP:
  After first run, create an admin user by running:
    python -c "
    import sqlite3
    from werkzeug.security import generate_password_hash
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO users (username,password) VALUES (?,?)',
                 ('admin', generate_password_hash('admin123')))
    conn.commit()
    "
  Then login at /login with username: admin, password: admin123

FEATURES:
  - Public blog with category filtering
  - Single post view with comments
  - Admin dashboard (post CRUD, comment moderation)
  - SQLite database (auto-created)
"""


# ─────────────────────────────────────────────────────────────────────────────
# 6. PORTFOLIO ADVANCED GENERATOR (with animations)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_portfolio_advanced(config: dict) -> dict:
    """Generate an animated portfolio website (static HTML/CSS/JS)."""
    name      = _c(config, "site_name", "My Portfolio")
    tagline   = _c(config, "tagline", "Designer & Developer")
    primary   = _c(config, "primary_color", "#6c63ff")
    secondary = _c(config, "secondary_color", "#f50057")
    font      = _c(config, "font", "Poppins")
    return {
        "index.html": _portfolio_adv_html(name, tagline, font),
        "style.css":  _portfolio_adv_css(primary, secondary, font),
        "script.js":  _portfolio_adv_js(),
        "README.txt": _readme_static(name),
    }


def _portfolio_adv_html(name: str, tagline: str, font: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{name} — Portfolio</title>
  <link href="https://fonts.googleapis.com/css2?family={font.replace(' ','+')}:wght@300;400;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="style.css"/>
</head>
<body class="dark-portfolio">

<!-- Cursor -->
<div class="cursor" id="cursor"></div>
<div class="cursor-follower" id="cursorFollower"></div>

<!-- Navbar -->
<header class="pf-header" id="pfHeader">
  <nav class="pf-nav">
    <div class="pf-logo">{name}</div>
    <ul class="pf-nav-links" id="pfNavLinks">
      <li><a href="#home">Home</a></li>
      <li><a href="#about">About</a></li>
      <li><a href="#skills">Skills</a></li>
      <li><a href="#work">Work</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
    <button class="pf-hamburger" onclick="togglePfNav()">&#9776;</button>
  </nav>
</header>

<!-- Hero -->
<section class="pf-hero" id="home">
  <div class="pf-hero-bg"></div>
  <div class="pf-hero-content">
    <p class="pf-greeting reveal-up">Hello, I'm</p>
    <h1 class="pf-name reveal-up">{name}</h1>
    <div class="pf-typewriter reveal-up">
      <span id="typewriterText"></span><span class="tw-cursor">|</span>
    </div>
    <p class="pf-tagline reveal-up">{tagline}</p>
    <div class="pf-hero-btns reveal-up">
      <a href="#work" class="pf-btn-primary">View My Work</a>
      <a href="#contact" class="pf-btn-outline">Hire Me</a>
    </div>
  </div>
  <div class="pf-hero-visual reveal-right">
    <div class="pf-avatar-ring">
      <div class="pf-avatar">
        <span>{name[0].upper()}</span>
      </div>
    </div>
    <div class="pf-floating-badge pf-fb1">React</div>
    <div class="pf-floating-badge pf-fb2">Python</div>
    <div class="pf-floating-badge pf-fb3">Design</div>
  </div>
  <div class="pf-scroll-hint">
    <span>Scroll</span>
    <div class="pf-scroll-line"></div>
  </div>
</section>

<!-- About -->
<section class="pf-about section" id="about">
  <div class="container">
    <h2 class="section-title reveal-up">About Me</h2>
    <div class="pf-about-grid">
      <div class="pf-about-text reveal-left">
        <p>I'm a passionate creative professional who loves building beautiful, functional digital experiences. With a keen eye for design and strong technical skills, I bring ideas to life.</p>
        <p>When I'm not coding, you'll find me exploring new design trends, contributing to open source, or enjoying a good cup of coffee.</p>
        <div class="pf-stats">
          <div class="pf-stat reveal-up"><span class="pf-stat-num" data-target="50">0</span><span>Projects</span></div>
          <div class="pf-stat reveal-up"><span class="pf-stat-num" data-target="5">0</span><span>Years Exp</span></div>
          <div class="pf-stat reveal-up"><span class="pf-stat-num" data-target="30">0</span><span>Clients</span></div>
        </div>
      </div>
      <div class="pf-about-img reveal-right">
        <div class="pf-img-card">
          <img src="https://picsum.photos/seed/portfolio/400/500" alt="Profile"/>
          <div class="pf-img-decoration"></div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Skills -->
<section class="pf-skills section" id="skills">
  <div class="container">
    <h2 class="section-title reveal-up">Skills</h2>
    <div class="pf-skills-grid">
      <div class="pf-skill-card reveal-up"><div class="pf-skill-icon">🎨</div><h3>UI/UX Design</h3><div class="pf-skill-bar"><div class="pf-skill-fill" data-width="90"></div></div></div>
      <div class="pf-skill-card reveal-up"><div class="pf-skill-icon">⚛️</div><h3>React / JS</h3><div class="pf-skill-bar"><div class="pf-skill-fill" data-width="85"></div></div></div>
      <div class="pf-skill-card reveal-up"><div class="pf-skill-icon">🐍</div><h3>Python / Flask</h3><div class="pf-skill-bar"><div class="pf-skill-fill" data-width="80"></div></div></div>
      <div class="pf-skill-card reveal-up"><div class="pf-skill-icon">📱</div><h3>Responsive Design</h3><div class="pf-skill-bar"><div class="pf-skill-fill" data-width="95"></div></div></div>
      <div class="pf-skill-card reveal-up"><div class="pf-skill-icon">🗄️</div><h3>Databases</h3><div class="pf-skill-bar"><div class="pf-skill-fill" data-width="75"></div></div></div>
      <div class="pf-skill-card reveal-up"><div class="pf-skill-icon">🚀</div><h3>Deployment</h3><div class="pf-skill-bar"><div class="pf-skill-fill" data-width="70"></div></div></div>
    </div>
  </div>
</section>

<!-- Work -->
<section class="pf-work section" id="work">
  <div class="container">
    <h2 class="section-title reveal-up">My Work</h2>
    <div class="portfolio-grid">
      <div class="portfolio-item reveal-up"><img src="https://picsum.photos/seed/w1/600/400" alt="Project 1"/><div class="portfolio-overlay"><h3>E-commerce Platform</h3><p>React · Python · SQLite</p><a href="#" class="pf-btn-sm">View Project</a></div></div>
      <div class="portfolio-item reveal-up"><img src="https://picsum.photos/seed/w2/600/400" alt="Project 2"/><div class="portfolio-overlay"><h3>SaaS Dashboard</h3><p>Vue.js · Flask · PostgreSQL</p><a href="#" class="pf-btn-sm">View Project</a></div></div>
      <div class="portfolio-item reveal-up"><img src="https://picsum.photos/seed/w3/600/400" alt="Project 3"/><div class="portfolio-overlay"><h3>Mobile App UI</h3><p>Figma · React Native</p><a href="#" class="pf-btn-sm">View Project</a></div></div>
      <div class="portfolio-item reveal-up"><img src="https://picsum.photos/seed/w4/600/400" alt="Project 4"/><div class="portfolio-overlay"><h3>Brand Identity</h3><p>Illustrator · Photoshop</p><a href="#" class="pf-btn-sm">View Project</a></div></div>
      <div class="portfolio-item reveal-up"><img src="https://picsum.photos/seed/w5/600/400" alt="Project 5"/><div class="portfolio-overlay"><h3>Blog Platform</h3><p>Next.js · Tailwind · Prisma</p><a href="#" class="pf-btn-sm">View Project</a></div></div>
      <div class="portfolio-item reveal-up"><img src="https://picsum.photos/seed/w6/600/400" alt="Project 6"/><div class="portfolio-overlay"><h3>Analytics Tool</h3><p>D3.js · Python · FastAPI</p><a href="#" class="pf-btn-sm">View Project</a></div></div>
    </div>
  </div>
</section>

<!-- Contact -->
<section class="pf-contact section" id="contact">
  <div class="container">
    <h2 class="section-title reveal-up">Get In Touch</h2>
    <div class="contact-layout">
      <div class="contact-info reveal-left">
        <div class="contact-item"><span>📧</span><p>hello@{name.lower().replace(' ','')}.com</p></div>
        <div class="contact-item"><span>📞</span><p>+1 (555) 000-0000</p></div>
        <div class="contact-item"><span>📍</span><p>Available Worldwide (Remote)</p></div>
        <div class="pf-social">
          <a href="#" class="pf-social-btn">GitHub</a>
          <a href="#" class="pf-social-btn">LinkedIn</a>
          <a href="#" class="pf-social-btn">Twitter</a>
        </div>
      </div>
      <form class="contact-form reveal-right" onsubmit="handleContact(event)">
        <input type="text" name="name" placeholder="Your Name" required/>
        <input type="email" name="email" placeholder="Your Email" required/>
        <input type="text" name="subject" placeholder="Subject"/>
        <textarea name="message" rows="5" placeholder="Your Message" required></textarea>
        <button type="submit" class="pf-btn-primary">Send Message</button>
      </form>
    </div>
  </div>
</section>

<footer class="site-footer">
  <div class="footer-bottom"><p>&copy; 2025 {name}. Crafted with ❤️</p></div>
</footer>

<button class="back-to-top" id="backToTop" onclick="scrollToTop()">↑</button>
<script src="script.js"></script>
</body>
</html>"""


def _portfolio_adv_css(primary: str, secondary: str, font: str) -> str:
    base = _base_css(primary, secondary, font)
    return base + f"""
/* ── Dark Portfolio Theme ─────────────────────────────────────────────── */
.dark-portfolio {{ background: #0a0a0f; color: #e8e8f0; }}
.dark-portfolio a {{ color: {primary}; }}

/* Custom cursor */
.cursor {{ width:10px;height:10px;border-radius:50%;background:{primary};position:fixed;pointer-events:none;z-index:9999;transform:translate(-50%,-50%);transition:transform .1s; }}
.cursor-follower {{ width:30px;height:30px;border-radius:50%;border:1px solid {primary};position:fixed;pointer-events:none;z-index:9998;transform:translate(-50%,-50%);transition:transform .15s,width .2s,height .2s; }}

/* Navbar */
.pf-header {{ position:fixed;top:0;left:0;right:0;z-index:100;padding:.85rem 2rem;transition:background .3s,box-shadow .3s; }}
.pf-header.scrolled {{ background:rgba(10,10,15,.95);backdrop-filter:blur(10px);box-shadow:0 2px 20px rgba(0,0,0,.3); }}
.pf-nav {{ display:flex;align-items:center;justify-content:space-between;max-width:1200px;margin:0 auto; }}
.pf-logo {{ font-size:1.3rem;font-weight:700;color:{primary}; }}
.pf-nav-links {{ list-style:none;display:flex;gap:2rem; }}
.pf-nav-links a {{ color:rgba(255,255,255,.8);font-size:.95rem;transition:color .2s; }}
.pf-nav-links a:hover {{ color:{primary}; }}
.pf-hamburger {{ display:none;background:none;border:none;color:#fff;font-size:1.5rem;cursor:pointer; }}

/* Hero */
.pf-hero {{ min-height:100vh;display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:6rem 2rem 2rem;max-width:1200px;margin:0 auto;position:relative; }}
.pf-hero-bg {{ position:fixed;inset:0;background:radial-gradient(ellipse at 20% 50%,rgba(108,99,255,.15) 0%,transparent 60%),radial-gradient(ellipse at 80% 20%,rgba(245,0,87,.1) 0%,transparent 50%);pointer-events:none;z-index:-1; }}
.pf-greeting {{ color:{primary};font-size:1.1rem;font-weight:500;margin-bottom:.5rem; }}
.pf-name {{ font-size:clamp(2.5rem,6vw,4.5rem);font-weight:700;line-height:1.1;margin-bottom:1rem; }}
.pf-typewriter {{ font-size:1.4rem;color:{secondary};margin-bottom:1rem;min-height:2rem; }}
.tw-cursor {{ animation:blink 1s infinite; }}
@keyframes blink {{ 0%,100%{{opacity:1}}50%{{opacity:0}} }}
.pf-tagline {{ color:rgba(255,255,255,.6);font-size:1.05rem;margin-bottom:2rem; }}
.pf-hero-btns {{ display:flex;gap:1rem;flex-wrap:wrap; }}
.pf-btn-primary {{ background:linear-gradient(135deg,{primary},{secondary});color:#fff;padding:.8rem 2rem;border-radius:30px;font-weight:600;transition:transform .2s,box-shadow .2s;display:inline-block; }}
.pf-btn-primary:hover {{ transform:translateY(-2px);box-shadow:0 8px 24px rgba(108,99,255,.4); }}
.pf-btn-outline {{ border:1px solid {primary};color:{primary};padding:.8rem 2rem;border-radius:30px;font-weight:600;transition:all .2s;display:inline-block; }}
.pf-btn-outline:hover {{ background:{primary};color:#fff; }}
.pf-btn-sm {{ background:{primary};color:#fff;padding:.4rem 1rem;border-radius:20px;font-size:.85rem;display:inline-block; }}

/* Avatar */
.pf-hero-visual {{ display:flex;align-items:center;justify-content:center;position:relative; }}
.pf-avatar-ring {{ width:280px;height:280px;border-radius:50%;border:2px solid rgba(108,99,255,.3);display:flex;align-items:center;justify-content:center;animation:rotate 20s linear infinite; }}
.pf-avatar {{ width:240px;height:240px;border-radius:50%;background:linear-gradient(135deg,{primary},{secondary});display:flex;align-items:center;justify-content:center;font-size:5rem;font-weight:700;color:#fff;animation:rotate 20s linear infinite reverse; }}
@keyframes rotate {{ to{{transform:rotate(360deg)}} }}
.pf-floating-badge {{ position:absolute;background:rgba(255,255,255,.1);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.2);padding:.4rem .9rem;border-radius:20px;font-size:.82rem;font-weight:600;animation:float 3s ease-in-out infinite; }}
.pf-fb1 {{ top:10%;right:5%;animation-delay:0s; }}
.pf-fb2 {{ bottom:20%;right:0%;animation-delay:.5s; }}
.pf-fb3 {{ top:50%;left:0%;animation-delay:1s; }}
@keyframes float {{ 0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}} }}
.pf-scroll-hint {{ position:absolute;bottom:2rem;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:.5rem;color:rgba(255,255,255,.4);font-size:.78rem; }}
.pf-scroll-line {{ width:1px;height:40px;background:linear-gradient(to bottom,rgba(108,99,255,.8),transparent);animation:scrollLine 1.5s ease-in-out infinite; }}
@keyframes scrollLine {{ 0%{{transform:scaleY(0);transform-origin:top}}50%{{transform:scaleY(1);transform-origin:top}}100%{{transform:scaleY(0);transform-origin:bottom}} }}

/* About */
.pf-about {{ background:rgba(255,255,255,.02); }}
.pf-about-grid {{ display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center; }}
.pf-about-text p {{ color:rgba(255,255,255,.7);line-height:1.8;margin-bottom:1rem; }}
.pf-stats {{ display:flex;gap:2rem;margin-top:2rem; }}
.pf-stat {{ text-align:center; }}
.pf-stat-num {{ display:block;font-size:2.2rem;font-weight:700;color:{primary}; }}
.pf-stat span:last-child {{ font-size:.85rem;color:rgba(255,255,255,.5); }}
.pf-img-card {{ position:relative;border-radius:20px;overflow:hidden; }}
.pf-img-card img {{ width:100%;border-radius:20px; }}
.pf-img-decoration {{ position:absolute;inset:-4px;border-radius:24px;border:2px solid {primary};opacity:.4;pointer-events:none; }}

/* Skills */
.pf-skills-grid {{ display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.5rem; }}
.pf-skill-card {{ background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:1.5rem;transition:border-color .2s; }}
.pf-skill-card:hover {{ border-color:{primary}; }}
.pf-skill-icon {{ font-size:1.8rem;margin-bottom:.75rem; }}
.pf-skill-card h3 {{ margin-bottom:.75rem;font-size:1rem; }}
.pf-skill-bar {{ background:rgba(255,255,255,.1);border-radius:20px;height:6px;overflow:hidden; }}
.pf-skill-fill {{ height:100%;background:linear-gradient(90deg,{primary},{secondary});border-radius:20px;width:0;transition:width 1.5s ease; }}

/* Social */
.pf-social {{ display:flex;gap:.75rem;margin-top:1.5rem; }}
.pf-social-btn {{ padding:.4rem 1rem;border-radius:20px;border:1px solid rgba(255,255,255,.2);color:rgba(255,255,255,.7);font-size:.85rem;transition:all .2s; }}
.pf-social-btn:hover {{ border-color:{primary};color:{primary}; }}

/* Back to top */
.back-to-top {{ position:fixed;bottom:2rem;right:2rem;width:44px;height:44px;border-radius:50%;background:{primary};color:#fff;border:none;font-size:1.2rem;cursor:pointer;display:none;align-items:center;justify-content:center;box-shadow:0 4px 16px rgba(108,99,255,.4);transition:transform .2s; }}
.back-to-top.visible {{ display:flex; }}
.back-to-top:hover {{ transform:translateY(-3px); }}

/* Reveal animations */
.reveal-up,.reveal-left,.reveal-right {{ opacity:0;transition:opacity .7s ease,transform .7s ease; }}
.reveal-up {{ transform:translateY(40px); }}
.reveal-left {{ transform:translateX(-40px); }}
.reveal-right {{ transform:translateX(40px); }}
.revealed {{ opacity:1!important;transform:none!important; }}

/* Responsive */
@media(max-width:900px){{
  .pf-hero {{ grid-template-columns:1fr;text-align:center;padding-top:8rem; }}
  .pf-hero-visual {{ display:none; }}
  .pf-hero-btns {{ justify-content:center; }}
  .pf-about-grid {{ grid-template-columns:1fr; }}
  .pf-about-img {{ display:none; }}
  .pf-stats {{ justify-content:center; }}
}}
@media(max-width:768px){{
  .pf-nav-links {{ display:none;flex-direction:column;position:absolute;top:60px;left:0;right:0;background:rgba(10,10,15,.98);padding:1.5rem;gap:1rem; }}
  .pf-nav-links.open {{ display:flex; }}
  .pf-hamburger {{ display:block; }}
}}
"""


def _portfolio_adv_js() -> str:
    return """// Portfolio Advanced JS — Generated by WebGen

// ── Custom cursor ─────────────────────────────────────────────────────────────
const cursor = document.getElementById('cursor');
const follower = document.getElementById('cursorFollower');
if (cursor && follower) {
  document.addEventListener('mousemove', e => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top  = e.clientY + 'px';
    setTimeout(() => {
      follower.style.left = e.clientX + 'px';
      follower.style.top  = e.clientY + 'px';
    }, 80);
  });
}

// ── Navbar scroll effect ──────────────────────────────────────────────────────
const header = document.getElementById('pfHeader');
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) header?.classList.add('scrolled');
  else header?.classList.remove('scrolled');
  // Back to top
  const btn = document.getElementById('backToTop');
  if (btn) btn.classList.toggle('visible', window.scrollY > 400);
});

// ── Mobile nav ────────────────────────────────────────────────────────────────
function togglePfNav() {
  document.getElementById('pfNavLinks')?.classList.toggle('open');
}

// ── Typewriter effect ─────────────────────────────────────────────────────────
const roles = ['Full Stack Developer', 'UI/UX Designer', 'Creative Coder', 'Problem Solver'];
let roleIdx = 0, charIdx = 0, deleting = false;
const twEl = document.getElementById('typewriterText');
function typeWriter() {
  if (!twEl) return;
  const current = roles[roleIdx];
  if (!deleting) {
    twEl.textContent = current.slice(0, ++charIdx);
    if (charIdx === current.length) { deleting = true; setTimeout(typeWriter, 1800); return; }
  } else {
    twEl.textContent = current.slice(0, --charIdx);
    if (charIdx === 0) { deleting = false; roleIdx = (roleIdx + 1) % roles.length; }
  }
  setTimeout(typeWriter, deleting ? 60 : 100);
}
typeWriter();

// ── Scroll reveal ─────────────────────────────────────────────────────────────
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('revealed'); });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right').forEach(el => {
  revealObserver.observe(el);
});

// ── Skill bar animation ───────────────────────────────────────────────────────
const skillObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.querySelectorAll('.pf-skill-fill').forEach(bar => {
        bar.style.width = bar.dataset.width + '%';
      });
    }
  });
}, { threshold: 0.3 });
document.querySelectorAll('.pf-skills-grid').forEach(el => skillObserver.observe(el));

// ── Counter animation ─────────────────────────────────────────────────────────
const counterObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.querySelectorAll('.pf-stat-num').forEach(el => {
        const target = parseInt(el.dataset.target);
        let count = 0;
        const step = Math.ceil(target / 40);
        const timer = setInterval(() => {
          count = Math.min(count + step, target);
          el.textContent = count + '+';
          if (count >= target) clearInterval(timer);
        }, 40);
      });
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.pf-stats').forEach(el => counterObserver.observe(el));

// ── Smooth scroll ─────────────────────────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});

// ── Back to top ───────────────────────────────────────────────────────────────
function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); }

// ── Contact form ──────────────────────────────────────────────────────────────
function handleContact(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button');
  btn.textContent = 'Sending...'; btn.disabled = true;
  setTimeout(() => {
    alert('Message sent! I will get back to you soon.');
    e.target.reset(); btn.textContent = 'Send Message'; btn.disabled = false;
  }, 800);
}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SHOPWAVE-QUALITY OVERRIDES — Tailwind CSS + Alpine.js
# These definitions override the old CSS-based versions above.
# Python uses the LAST definition of a function, so these win.
# ═══════════════════════════════════════════════════════════════════════════════

def _mv_css() -> str:
    """Minimal CSS — Tailwind handles everything via CDN."""
    return """
/* ShopWave-quality overrides — Tailwind handles layout */
.scrollbar-hide{-ms-overflow-style:none;scrollbar-width:none}
.scrollbar-hide::-webkit-scrollbar{display:none}
.line-clamp-2{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
"""


def _mv_base_html(site_name: str, font: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{% block title %}}{site_name}{{% endblock %}}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config={{theme:{{extend:{{colors:{{pink:{{500:'#e91e63',600:'#c2185b'}}}}}}}}}}</script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}"/>
  <style>body{{font-family:'Inter',sans-serif}}</style>
</head>
<body class="bg-gray-50 text-gray-900 antialiased">

{{%- with messages = get_flashed_messages(with_categories=true) %}}
{{%- if messages %}}
<div class="fixed top-4 right-4 z-50 space-y-2" x-data>
  {{%- for cat, msg in messages %}}
  <div x-data="{{{{show:true}}}}" x-show="show" x-transition
       class="flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium
              {{{{ 'bg-emerald-50 border border-emerald-200 text-emerald-800' if cat=='success' else
                  'bg-red-50 border border-red-200 text-red-800' if cat=='error' else
                  'bg-amber-50 border border-amber-200 text-amber-800' if cat=='warning' else
                  'bg-blue-50 border border-blue-200 text-blue-800' }}}}">
    <span>{{{{ msg }}}}</span>
    <button @click="show=false" class="ml-2 opacity-60 hover:opacity-100">✕</button>
  </div>
  {{%- endfor %}}
</div>
{{%- endif %}}
{{%- endwith %}}

<nav class="sticky top-0 z-40 bg-white border-b border-gray-100 shadow-sm" x-data="{{{{mobileOpen:false}}}}">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <div class="flex items-center gap-3 h-14">
      <a href="{{{{ url_for('index') }}}}" class="flex items-center gap-2 flex-shrink-0">
        <span class="w-8 h-8 rounded-lg bg-pink-500 flex items-center justify-center text-white text-sm">🛍️</span>
        <span class="font-black text-gray-900 text-lg tracking-tight hidden sm:inline">{site_name}</span>
      </a>
      {{%- if not session.role or session.role == 'customer' %}}
      <form action="{{{{ url_for('index') }}}}" method="get" class="flex-1 max-w-xl hidden sm:flex">
        <div class="flex w-full items-center bg-gray-50 border border-gray-200 rounded-full focus-within:border-pink-400 focus-within:ring-2 focus-within:ring-pink-100 overflow-hidden transition-all">
          <input type="search" name="q" value="{{{{ request.args.get('q','') }}}}"
                 placeholder="Search products…"
                 class="flex-1 px-4 py-2 text-sm bg-transparent outline-none"/>
          <button type="submit" class="px-4 py-2 text-gray-400 hover:text-pink-500">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/></svg>
          </button>
        </div>
      </form>
      {{%- endif %}}
      <div class="flex items-center gap-1 ml-auto">
        {{%- if not session.user_id %}}
          <a href="{{{{ url_for('login') }}}}" class="text-sm font-semibold text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-50">Login</a>
          <a href="{{{{ url_for('signup') }}}}" class="text-sm font-bold bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-full transition-colors">Sign Up</a>
        {{%- elif session.role == 'admin' %}}
          <a href="{{{{ url_for('admin_dashboard') }}}}" class="text-sm font-semibold text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-50">Dashboard</a>
          <a href="{{{{ url_for('admin_users') }}}}" class="text-sm font-semibold text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-50">Users</a>
          <a href="{{{{ url_for('admin_orders') }}}}" class="text-sm font-semibold text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-50">Orders</a>
          <a href="{{{{ url_for('logout') }}}}" class="text-sm font-semibold text-red-500 px-3 py-1.5 rounded-lg hover:bg-red-50">Logout</a>
        {{%- elif session.role == 'seller' %}}
          <a href="{{{{ url_for('seller_dashboard') }}}}" class="text-sm font-semibold text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-50">Dashboard</a>
          <a href="{{{{ url_for('seller_add_product') }}}}" class="text-sm font-bold bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-full transition-colors">+ Product</a>
          <a href="{{{{ url_for('logout') }}}}" class="text-sm font-semibold text-red-500 px-3 py-1.5 rounded-lg hover:bg-red-50">Logout</a>
        {{%- else %}}
          <a href="{{{{ url_for('cart') }}}}" class="relative flex items-center justify-center w-9 h-9 rounded-xl text-gray-500 hover:bg-gray-100">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
            {{%- if session.get('cart_count',0) > 0 %}}
            <span class="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[10px] font-bold min-w-[16px] h-4 px-0.5 rounded-full flex items-center justify-center">{{{{ session.get('cart_count',0) }}}}</span>
            {{%- endif %}}
          </a>
          <a href="{{{{ url_for('my_orders') }}}}" class="text-sm font-semibold text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-50 hidden sm:inline">Orders</a>
          <a href="{{{{ url_for('logout') }}}}" class="text-sm font-semibold text-red-500 px-3 py-1.5 rounded-lg hover:bg-red-50 hidden sm:inline">Logout</a>
        {{%- endif %}}
      </div>
    </div>
  </div>
</nav>

<main>{{%- block content %}}{{%- endblock %}}</main>

{{%- if session.role == 'customer' %}}
<nav class="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 flex md:hidden shadow-lg">
  <a href="{{{{ url_for('index') }}}}" class="flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-[10px] font-semibold text-gray-400 hover:text-pink-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
    Home
  </a>
  <a href="{{{{ url_for('cart') }}}}" class="flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-[10px] font-semibold text-gray-400 hover:text-pink-500 relative">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
    Cart
  </a>
  <a href="{{{{ url_for('my_orders') }}}}" class="flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-[10px] font-semibold text-gray-400 hover:text-pink-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
    Orders
  </a>
  <a href="{{{{ url_for('logout') }}}}" class="flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-[10px] font-semibold text-gray-400 hover:text-red-500">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
    Logout
  </a>
</nav>
<div class="h-16 md:hidden"></div>
{{%- endif %}}

<footer class="bg-gray-900 text-gray-400 mt-16">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-10">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
      <div class="col-span-2 md:col-span-1">
        <div class="flex items-center gap-2 mb-3">
          <span class="w-8 h-8 rounded-lg bg-pink-500 flex items-center justify-center text-white">🛍️</span>
          <span class="font-black text-white text-lg">{site_name}</span>
        </div>
        <p class="text-sm leading-relaxed">India's favourite multi-vendor marketplace. Shop smart, sell easy.</p>
      </div>
      <div>
        <h4 class="text-white font-semibold text-sm uppercase tracking-wider mb-3">Shop</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="{{{{ url_for('index') }}}}" class="hover:text-white transition-colors">All Products</a></li>
          <li><a href="{{{{ url_for('index', category='Fashion') }}}}" class="hover:text-white transition-colors">Fashion</a></li>
          <li><a href="{{{{ url_for('index', category='Electronics') }}}}" class="hover:text-white transition-colors">Electronics</a></li>
        </ul>
      </div>
      <div>
        <h4 class="text-white font-semibold text-sm uppercase tracking-wider mb-3">Sell</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="{{{{ url_for('signup') }}}}" class="hover:text-white transition-colors">Become a Seller</a></li>
          <li><a href="{{{{ url_for('seller_dashboard') }}}}" class="hover:text-white transition-colors">Seller Dashboard</a></li>
        </ul>
      </div>
      <div>
        <h4 class="text-white font-semibold text-sm uppercase tracking-wider mb-3">Trust</h4>
        <div class="space-y-1.5 text-xs">
          <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Free delivery above ₹499</div>
          <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> 7-day easy returns</div>
          <div class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Secure payments</div>
        </div>
      </div>
    </div>
  </div>
  <div class="border-t border-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex justify-between items-center text-xs text-gray-500">
      <span>&copy; 2025 {site_name}. All rights reserved.</span>
      <span>UPI · Cards · COD</span>
    </div>
  </div>
</footer>

<script src="{{{{ url_for('static', filename='js/script.js') }}}}"></script>
{{%- block scripts %}}{{%- endblock %}}
</body>
</html>"""


def _mv_storefront_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Shop — {{ request.host }}{%- endblock %}
{%- block content %}
<div x-data="{ loading: true }" x-init="setTimeout(()=>loading=false,400)" class="min-h-screen bg-gray-50">

  {# Hero #}
  <section class="bg-gradient-to-br from-pink-500 via-pink-600 to-violet-600 text-white text-center py-14 px-4">
    <p class="text-xs font-semibold tracking-widest uppercase opacity-80 mb-3">India's #1 Marketplace</p>
    <h1 class="text-3xl md:text-5xl font-black mb-3 leading-tight">Shop Smart, Sell Easy 🛍️</h1>
    <p class="text-sm md:text-base opacity-80 mb-6">10,000+ sellers · Millions of products · Free delivery above ₹499</p>
    <a href="#products" class="px-6 py-2.5 bg-white text-pink-600 font-bold rounded-full text-sm hover:bg-pink-50 transition-colors shadow-md">Shop Now</a>
  </section>

  {# Category pills #}
  <div class="bg-white border-b border-gray-100 sticky top-14 z-30">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3">
      <div class="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
        <a href="{{ url_for('index', q=q, sort=sort, min_price=min_price, max_price=max_price) }}"
           class="inline-flex items-center px-3.5 py-1.5 rounded-full text-[13px] font-medium whitespace-nowrap transition-all
                  {{ 'bg-pink-500 text-white' if not selected_cat else 'bg-gray-100 text-gray-600 hover:bg-gray-200' }}">All</a>
        {%- for cat in categories %}
        <a href="{{ url_for('index', category=cat, q=q, sort=sort) }}"
           class="inline-flex items-center px-3.5 py-1.5 rounded-full text-[13px] font-medium whitespace-nowrap transition-all
                  {{ 'bg-pink-500 text-white' if selected_cat==cat else 'bg-gray-100 text-gray-600 hover:bg-gray-200' }}">{{ cat }}</a>
        {%- endfor %}
      </div>
    </div>
  </div>

  {# Filter + sort bar #}
  <div class="bg-white border-b border-gray-100 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-2.5">
      <form method="get" action="{{ url_for('index') }}" class="flex items-center gap-3 flex-wrap">
        {%- if q %}<input type="hidden" name="q" value="{{ q }}"/>{%- endif %}
        {%- if selected_cat %}<input type="hidden" name="category" value="{{ selected_cat }}"/>{%- endif %}
        <span class="text-xs text-gray-400 font-medium">{{ products|length }} items</span>
        <div class="flex gap-2 ml-auto flex-wrap">
          {%- for val, label in [('newest','✨ Newest'),('price_asc','Price ↑'),('price_desc','Price ↓'),('rating','⭐ Top Rated')] %}
          <button type="submit" name="sort" value="{{ val }}"
                  class="px-3 py-1.5 rounded-full text-xs font-semibold transition-all
                         {{ 'bg-pink-50 text-pink-600 ring-1 ring-pink-300' if sort==val else 'bg-gray-100 text-gray-600 hover:bg-gray-200' }}">
            {{ label }}
          </button>
          {%- endfor %}
        </div>
      </form>
    </div>
  </div>

  {# Main layout #}
  <div class="max-w-7xl mx-auto px-3 sm:px-6 py-5 flex gap-6" id="products">

    {# Desktop sidebar #}
    <aside class="hidden lg:block w-52 flex-shrink-0">
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden sticky top-32">
        <div class="px-4 py-3 border-b border-gray-100">
          <h2 class="text-sm font-bold text-gray-900">Filters</h2>
        </div>
        <form method="get" action="{{ url_for('index') }}" class="p-4 space-y-4">
          {%- if q %}<input type="hidden" name="q" value="{{ q }}"/>{%- endif %}
          <div>
            <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Category</p>
            {%- for cat in categories %}
            <label class="flex items-center gap-2 py-1.5 cursor-pointer">
              <input type="radio" name="category" value="{{ cat }}" {{ 'checked' if selected_cat==cat else '' }} onchange="this.form.submit()" class="accent-pink-500"/>
              <span class="text-sm text-gray-700">{{ cat }}</span>
            </label>
            {%- endfor %}
          </div>
          <div>
            <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Price Range</p>
            <div class="grid grid-cols-2 gap-2">
              <input type="number" name="min_price" value="{{ min_price }}" placeholder="Min ₹"
                     class="w-full px-2 py-1.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-pink-400"/>
              <input type="number" name="max_price" value="{{ max_price }}" placeholder="Max ₹"
                     class="w-full px-2 py-1.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-pink-400"/>
            </div>
          </div>
          <button type="submit" class="w-full py-2 rounded-xl bg-pink-500 hover:bg-pink-600 text-white text-sm font-bold transition-colors">Apply</button>
          <a href="{{ url_for('index') }}" class="block text-center text-xs text-gray-400 hover:text-gray-600">Clear all</a>
        </form>
      </div>
    </aside>

    {# Product grid #}
    <div class="flex-1 min-w-0">
      {%- if products %}

      {# Skeleton #}
      <div x-show="loading" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {%- for _ in range(8) %}
        <div class="bg-white rounded-2xl p-3 shadow-sm animate-pulse">
          <div class="bg-gray-200 aspect-square rounded-xl mb-3"></div>
          <div class="bg-gray-200 h-3 rounded w-3/4 mb-2"></div>
          <div class="bg-gray-200 h-3 rounded w-1/2"></div>
        </div>
        {%- endfor %}
      </div>

      {# Real grid #}
      <div x-show="!loading" x-transition:enter="transition-opacity duration-300"
           x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100"
           class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {%- for p in products %}
        <div class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-0.5 cursor-pointer"
             onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
          <div class="relative aspect-square overflow-hidden bg-gray-50">
            <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
                 alt="{{ p.name }}"
                 class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                 loading="lazy"
                 onerror="this.src='https://placehold.co/400x400/fce4f3/e91e63?text=?'"/>
          </div>
          <div class="p-3">
            <h3 class="text-sm font-medium text-gray-800 line-clamp-2 leading-snug mb-1.5">{{ p.name }}</h3>
            <div class="flex items-baseline gap-1.5 mb-1.5">
              <span class="text-base font-bold text-gray-900">₹{{ '%.0f'|format(p.price) }}</span>
            </div>
            {%- if p.avg_rating > 0 %}
            <div class="flex items-center gap-1.5 mb-1.5">
              <div class="flex items-center gap-1 bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded text-xs font-semibold">
                <svg class="w-3 h-3 fill-amber-400" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                {{ '%.1f'|format(p.avg_rating) }}
              </div>
              <span class="text-xs text-gray-400">({{ p.review_count }})</span>
            </div>
            {%- endif %}
            <div class="flex items-center gap-1 text-[11px] text-gray-500 mb-2">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"/></svg>
              Free Delivery
            </div>
            {%- if not session.role or session.role == 'customer' %}
            <form method="POST" action="{{ url_for('add_to_cart', pid=p.id) }}" onclick="event.stopPropagation()">
              <input type="hidden" name="quantity" value="1"/>
              <button type="submit"
                      class="w-full flex items-center justify-center gap-1.5 bg-pink-500 hover:bg-pink-600 text-white font-semibold text-xs px-4 py-2 rounded-full transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                Add to Cart
              </button>
            </form>
            {%- endif %}
          </div>
        </div>
        {%- endfor %}
      </div>

      {%- else %}
      <div class="flex flex-col items-center justify-center py-16 text-center">
        <div class="w-24 h-24 rounded-full bg-pink-50 flex items-center justify-center mb-4">
          <svg class="w-12 h-12 text-pink-300" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/></svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 mb-2">No products found</h3>
        <p class="text-sm text-gray-500 mb-5">Try adjusting your filters or search term.</p>
        <a href="{{ url_for('index') }}" class="px-5 py-2.5 bg-pink-500 hover:bg-pink-600 text-white font-bold rounded-full text-sm transition-colors">Browse All</a>
      </div>
      {%- endif %}
    </div>
  </div>
</div>
{%- endblock %}"""


def _mv_product_detail_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}{{ product.name }}{%- endblock %}
{%- block content %}
<div x-data="{
  activeImg: '{{ url_for('static', filename='uploads/' + (product.image or 'default.png')) }}',
  qty: 1,
  adding: false,
  async addToCart() {
    this.adding = true;
    const res = await fetch('{{ url_for('add_to_cart', pid=product.id) }}', {
      method: 'POST',
      headers: {'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest'},
      body: 'quantity=' + this.qty
    });
    const data = await res.json().catch(()=>({}));
    this.adding = false;
    if (data.ok) {
      const t = document.createElement('div');
      t.className = 'fixed bottom-20 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-sm font-semibold px-4 py-2.5 rounded-full shadow-lg z-50 transition-all';
      t.textContent = '✓ Added to cart!';
      document.body.appendChild(t);
      setTimeout(()=>t.remove(), 2000);
    } else { window.location.href = '{{ url_for('add_to_cart', pid=product.id) }}'; }
  }
}" class="min-h-screen bg-gray-50 pb-24 md:pb-0">

  {# Breadcrumb #}
  <div class="bg-white border-b border-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-2.5">
      <nav class="flex items-center gap-2 text-xs text-gray-500">
        <a href="{{ url_for('index') }}" class="hover:text-pink-500">Home</a>
        <span>›</span>
        <a href="{{ url_for('index', category=product.category) }}" class="hover:text-pink-500">{{ product.category }}</a>
        <span>›</span>
        <span class="text-gray-900 font-medium truncate max-w-[200px]">{{ product.name }}</span>
      </nav>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-5">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">

      {# Image #}
      <div class="space-y-3">
        <div class="bg-white rounded-2xl overflow-hidden shadow-sm aspect-square">
          <img :src="activeImg" alt="{{ product.name }}"
               class="w-full h-full object-contain p-4"
               onerror="this.src='https://placehold.co/600x600/fce4f3/e91e63?text=?'"/>
        </div>
      </div>

      {# Info #}
      <div class="space-y-5">
        <div>
          <a href="{{ url_for('index', category=product.category) }}"
             class="inline-block text-xs font-semibold text-pink-500 bg-pink-50 px-2.5 py-1 rounded-full mb-2">{{ product.category }}</a>
          <h1 class="text-xl md:text-2xl font-bold text-gray-900 leading-snug">{{ product.name }}</h1>
        </div>

        {%- if product.avg_rating > 0 %}
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-emerald-500 text-white text-sm font-bold px-2.5 py-1 rounded-lg">
            <svg class="w-3.5 h-3.5 fill-white" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
            {{ product.avg_rating }}
          </div>
          <span class="text-sm text-gray-500">{{ product.review_count }} review{{ 's' if product.review_count != 1 }}</span>
          <span class="text-gray-300">|</span>
          {%- if product.stock > 0 %}
          <span class="text-sm font-semibold text-emerald-600">✓ In Stock</span>
          {%- else %}
          <span class="text-sm font-semibold text-red-500">Out of Stock</span>
          {%- endif %}
        </div>
        {%- endif %}

        <div class="bg-gray-50 rounded-2xl p-4">
          <div class="text-3xl font-black text-gray-900 mb-1">₹{{ '%.0f'|format(product.price) }}</div>
          <p class="text-xs text-gray-400">Inclusive of all taxes · Free delivery above ₹499</p>
        </div>

        {%- if product.description %}
        <div>
          <p class="text-sm font-bold text-gray-900 mb-2">Product Details</p>
          <p class="text-sm text-gray-600 leading-relaxed">{{ product.description }}</p>
        </div>
        {%- endif %}

        {# Delivery info #}
        <div class="bg-white rounded-2xl border border-gray-100 divide-y divide-gray-100 shadow-sm">
          <div class="flex items-center gap-3 px-4 py-3">
            <svg class="w-5 h-5 text-pink-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"/></svg>
            <div><p class="text-sm font-semibold text-gray-900">Free Delivery</p><p class="text-xs text-gray-500">On orders above ₹499 · 3–5 days</p></div>
          </div>
          <div class="flex items-center gap-3 px-4 py-3">
            <svg class="w-5 h-5 text-pink-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
            <div><p class="text-sm font-semibold text-gray-900">Secure Payments</p><p class="text-xs text-gray-500">UPI · Cards · COD</p></div>
          </div>
        </div>

        <p class="text-sm text-gray-500">Sold by <strong class="text-gray-900">{{ product.seller_name }}</strong></p>

        {# Qty + CTA (desktop) #}
        {%- if product.stock > 0 and (not session.role or session.role == 'customer') %}
        <div class="hidden md:flex items-center gap-3">
          <div class="flex items-center border border-gray-200 rounded-xl overflow-hidden">
            <button @click="qty=Math.max(1,qty-1)" type="button"
                    class="w-9 h-9 flex items-center justify-center text-gray-600 hover:bg-gray-50">−</button>
            <span x-text="qty" class="w-10 text-center text-sm font-bold"></span>
            <button @click="qty=Math.min({{ product.stock }},qty+1)" type="button"
                    class="w-9 h-9 flex items-center justify-center text-gray-600 hover:bg-gray-50">+</button>
          </div>
          <button @click="addToCart()" :disabled="adding"
                  class="flex-1 flex items-center justify-center gap-2 border border-pink-400 text-pink-500 hover:bg-pink-500 hover:text-white font-bold py-2.5 rounded-full transition-all">
            <span x-text="adding ? 'Adding…' : 'Add to Cart'"></span>
          </button>
          <a href="{{ url_for('checkout') }}"
             class="flex-1 flex items-center justify-center gap-2 bg-pink-500 hover:bg-pink-600 text-white font-bold py-2.5 rounded-full transition-colors">
            Buy Now
          </a>
        </div>
        {%- elif not session.user_id %}
        <a href="{{ url_for('login') }}" class="hidden md:flex items-center justify-center bg-pink-500 hover:bg-pink-600 text-white font-bold py-2.5 rounded-full transition-colors">Login to Buy</a>
        {%- endif %}
      </div>
    </div>

    {# Reviews #}
    <div id="reviews" class="mt-10">
      <h2 class="text-lg font-bold text-gray-900 mb-4">Customer Reviews</h2>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-white rounded-2xl p-5 shadow-sm">
          {%- if product.avg_rating > 0 %}
          <div class="text-5xl font-black text-gray-900 mb-1">{{ product.avg_rating }}</div>
          <div class="flex gap-0.5 mb-2">
            {%- for i in range(1,6) %}
            <svg class="w-4 h-4 {{ 'fill-amber-400' if i <= product.avg_rating|round else 'fill-gray-200' }}" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
            {%- endfor %}
          </div>
          <p class="text-xs text-gray-400">{{ product.review_count }} review{{ 's' if product.review_count != 1 }}</p>
          {%- else %}
          <p class="text-sm text-gray-400 mb-3">No reviews yet. Be the first!</p>
          {%- endif %}
          {%- if session.user_id and session.role == 'customer' %}
          <div x-data="{open:false, rating:{{ user_review.rating if user_review else 0 }}}">
            <button @click="open=!open" class="w-full mt-3 border border-pink-400 text-pink-500 hover:bg-pink-500 hover:text-white font-semibold text-sm py-2 rounded-full transition-all">
              {{ 'Edit Review' if user_review else 'Write a Review' }}
            </button>
            <div x-show="open" x-transition class="mt-4">
              <form method="POST" action="{{ url_for('submit_review', pid=product.id) }}" class="space-y-3">
                <div class="flex gap-1">
                  {%- for i in range(1,6) %}
                  <button type="button" @click="rating={{ i }}"
                          :class="rating >= {{ i }} ? 'text-amber-400' : 'text-gray-300'"
                          class="text-2xl transition-colors">★</button>
                  {%- endfor %}
                  <input type="hidden" name="rating" :value="rating"/>
                </div>
                <textarea name="comment" rows="3" placeholder="Share your experience…"
                          class="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-pink-400 resize-none">{{ user_review.comment if user_review else '' }}</textarea>
                <button type="submit" class="w-full bg-pink-500 hover:bg-pink-600 text-white font-bold text-sm py-2 rounded-full transition-colors">
                  {{ 'Update' if user_review else 'Submit' }} Review
                </button>
              </form>
            </div>
          </div>
          {%- endif %}
        </div>
        <div class="lg:col-span-2 space-y-3">
          {%- if reviews %}
          {%- for r in reviews %}
          <div class="bg-white rounded-2xl p-4 shadow-sm">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-pink-100 text-pink-600 font-bold text-sm flex items-center justify-center">{{ r.reviewer_name[0].upper() }}</div>
                <div>
                  <p class="text-sm font-semibold text-gray-900">{{ r.reviewer_name }}</p>
                  <p class="text-xs text-gray-400">{{ r.created_at[:10] }}</p>
                </div>
              </div>
              <div class="flex items-center gap-1 bg-emerald-500 text-white text-xs font-bold px-2 py-0.5 rounded-md">
                <svg class="w-3 h-3 fill-white" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                {{ r.rating }}
              </div>
            </div>
            {%- if r.comment %}<p class="text-sm text-gray-600">{{ r.comment }}</p>{%- endif %}
          </div>
          {%- endfor %}
          {%- else %}
          <div class="bg-white rounded-2xl p-8 text-center shadow-sm">
            <p class="text-3xl mb-2">💬</p>
            <p class="text-sm text-gray-500">No reviews yet</p>
          </div>
          {%- endif %}
        </div>
      </div>
    </div>

    {# Related #}
    {%- if related %}
    <section class="mt-10">
      <h2 class="text-lg font-bold text-gray-900 mb-4">Similar Products</h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {%- for p in related %}
        <div class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all cursor-pointer"
             onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
          <div class="aspect-square overflow-hidden bg-gray-50">
            <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
                 alt="{{ p.name }}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy"
                 onerror="this.src='https://placehold.co/400x400/fce4f3/e91e63?text=?'"/>
          </div>
          <div class="p-3">
            <p class="text-sm font-medium text-gray-800 line-clamp-2 mb-1">{{ p.name }}</p>
            <p class="text-base font-bold text-gray-900">₹{{ '%.0f'|format(p.price) }}</p>
          </div>
        </div>
        {%- endfor %}
      </div>
    </section>
    {%- endif %}
  </div>

  {# Mobile sticky bottom bar #}
  {%- if product.stock > 0 and (not session.role or session.role == 'customer') %}
  <div class="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 px-4 py-3 flex gap-3 md:hidden shadow-lg">
    <button @click="addToCart()" :disabled="adding"
            class="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl border-2 border-pink-500 text-pink-500 font-bold text-sm hover:bg-pink-50 transition-colors">
      <span x-text="adding ? 'Adding…' : 'Add to Cart'"></span>
    </button>
    <a href="{{ url_for('checkout') }}"
       class="flex-1 flex items-center justify-center py-3 rounded-2xl bg-pink-500 hover:bg-pink-600 text-white font-bold text-sm transition-colors">
      Buy Now
    </a>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


# ═══════════════════════════════════════════════════════════════════════════════
# FLASK GENERATOR OVERRIDES — Fix double navbar + separate pages
# ═══════════════════════════════════════════════════════════════════════════════

def _gen_flask(config: dict) -> dict:
    """Generate a multi-page Flask project — separate page per section."""
    site_name = _c(config, "site_name", "My App")
    primary   = _c(config, "primary_color", "#6c63ff")
    secondary = _c(config, "secondary_color", "#f50057")
    font      = _c(config, "font", "Poppins")
    has_auth  = config.get("has_auth", False)
    has_db    = config.get("has_db", False)
    sections  = config.get("sections", ["header", "hero", "about", "contact", "footer"])
    wtype     = _c(config, "website_type", "business")

    files = {}
    files["app.py"]               = _flask_mp_app_py(site_name, has_auth, has_db, sections)
    files["templates/base.html"]  = _flask_mp_base_html(site_name, has_auth, font, sections)
    files["static/css/style.css"] = _base_css(primary, secondary, font) + _flask_extra_css()
    files["static/js/script.js"]  = _base_js()
    files["requirements.txt"]     = "Flask==3.0.0\nWerkzeug==3.0.1\n"
    files["README.txt"]           = _readme_flask(site_name, has_auth)

    # Home page
    files["templates/index.html"] = _flask_mp_page(
        "home", site_name,
        f"""<section class="hero" id="home">
  <div class="hero-content">
    <h1>{site_name}</h1>
    <p>Welcome to {site_name} — your trusted partner.</p>
    <a href="/about" class="btn-primary">Learn More</a>
  </div>
</section>"""
    )

    # Separate page per section
    page_map = {
        "about": ("About Us", """<section class="about section">
  <div class="container">
    <h2 class="section-title">About Us</h2>
    <div class="about-grid">
      <div class="about-text">
        <p>We are passionate about delivering the best experience. Our team works hard to create innovative solutions that make a real difference.</p>
        <p>Founded with a vision to simplify complexity, we bring expertise and dedication to every project.</p>
      </div>
      <div class="about-stats">
        <div class="stat"><span class="stat-num">500+</span><span>Clients</span></div>
        <div class="stat"><span class="stat-num">10+</span><span>Years</span></div>
        <div class="stat"><span class="stat-num">99%</span><span>Satisfaction</span></div>
      </div>
    </div>
  </div>
</section>"""),
        "services": ("Services", """<section class="services section">
  <div class="container">
    <h2 class="section-title">Our Services</h2>
    <div class="cards-grid">
      <div class="card"><div class="card-icon">🚀</div><h3>Strategy</h3><p>Data-driven strategies tailored to your goals.</p></div>
      <div class="card"><div class="card-icon">🎨</div><h3>Design</h3><p>Beautiful, user-centric designs that convert.</p></div>
      <div class="card"><div class="card-icon">⚙️</div><h3>Development</h3><p>Robust, scalable solutions built with modern tech.</p></div>
      <div class="card"><div class="card-icon">📈</div><h3>Growth</h3><p>Continuous optimisation to keep you ahead.</p></div>
    </div>
  </div>
</section>"""),
        "portfolio": ("Portfolio", """<section class="portfolio section">
  <div class="container">
    <h2 class="section-title">Our Work</h2>
    <div class="portfolio-grid">
      <div class="portfolio-item"><img src="https://picsum.photos/seed/p1/400/250" alt="Project 1"/><div class="portfolio-overlay"><h3>Project One</h3><p>Web Design</p></div></div>
      <div class="portfolio-item"><img src="https://picsum.photos/seed/p2/400/250" alt="Project 2"/><div class="portfolio-overlay"><h3>Project Two</h3><p>Branding</p></div></div>
      <div class="portfolio-item"><img src="https://picsum.photos/seed/p3/400/250" alt="Project 3"/><div class="portfolio-overlay"><h3>Project Three</h3><p>Development</p></div></div>
    </div>
  </div>
</section>"""),
        "products": ("Products", """<section class="products section">
  <div class="container">
    <h2 class="section-title">Our Products</h2>
    <div class="cards-grid">
      <div class="product-card"><img src="https://picsum.photos/seed/pr1/300/200" alt="Product 1"/><div class="product-info"><h3>Product One</h3><p class="product-desc">High quality item with premium features.</p><div class="product-footer"><span class="price">$29.99</span><button class="btn-primary btn-sm">Buy Now</button></div></div></div>
      <div class="product-card"><img src="https://picsum.photos/seed/pr2/300/200" alt="Product 2"/><div class="product-info"><h3>Product Two</h3><p class="product-desc">Best seller with excellent reviews.</p><div class="product-footer"><span class="price">$49.99</span><button class="btn-primary btn-sm">Buy Now</button></div></div></div>
      <div class="product-card"><img src="https://picsum.photos/seed/pr3/300/200" alt="Product 3"/><div class="product-info"><h3>Product Three</h3><p class="product-desc">Limited edition, grab yours today.</p><div class="product-footer"><span class="price">$19.99</span><button class="btn-primary btn-sm">Buy Now</button></div></div></div>
    </div>
  </div>
</section>"""),
        "blog": ("Blog", """<section class="blog section">
  <div class="container">
    <h2 class="section-title">Latest Posts</h2>
    <div class="cards-grid">
      <div class="card"><img src="https://picsum.photos/seed/b1/400/200" alt="Post" style="width:100%;border-radius:8px;margin-bottom:1rem"/><span class="tag">Design</span><h3>The Future of Web Design</h3><p>Exploring trends that will shape the web in 2025 and beyond.</p><a href="#" class="read-more">Read more →</a></div>
      <div class="card"><img src="https://picsum.photos/seed/b2/400/200" alt="Post" style="width:100%;border-radius:8px;margin-bottom:1rem"/><span class="tag">Tech</span><h3>Building Scalable APIs</h3><p>Best practices for designing APIs that grow with your product.</p><a href="#" class="read-more">Read more →</a></div>
      <div class="card"><img src="https://picsum.photos/seed/b3/400/200" alt="Post" style="width:100%;border-radius:8px;margin-bottom:1rem"/><span class="tag">Business</span><h3>Growth Hacking in 2025</h3><p>Proven strategies to accelerate your startup's growth.</p><a href="#" class="read-more">Read more →</a></div>
    </div>
  </div>
</section>"""),
        "testimonials": ("Testimonials", """<section class="testimonials section">
  <div class="container">
    <h2 class="section-title">What Clients Say</h2>
    <div class="testimonials-grid">
      <div class="testimonial"><p>"Absolutely fantastic service. Exceeded all our expectations!"</p><div class="testimonial-author"><img src="https://i.pravatar.cc/50?img=1" alt="Client"/><div><strong>Alice Johnson</strong><span>CEO, TechCorp</span></div></div></div>
      <div class="testimonial"><p>"Professional, fast, and the results speak for themselves."</p><div class="testimonial-author"><img src="https://i.pravatar.cc/50?img=2" alt="Client"/><div><strong>Bob Smith</strong><span>Founder, StartupX</span></div></div></div>
      <div class="testimonial"><p>"I would recommend them to anyone looking for quality work."</p><div class="testimonial-author"><img src="https://i.pravatar.cc/50?img=3" alt="Client"/><div><strong>Carol White</strong><span>Designer, Studio Y</span></div></div></div>
    </div>
  </div>
</section>"""),
        "contact": ("Contact", """<section class="contact section">
  <div class="container">
    <h2 class="section-title">Contact Us</h2>
    <div class="contact-layout">
      <div class="contact-info">
        <div class="contact-item"><span>📧</span><p>hello@example.com</p></div>
        <div class="contact-item"><span>📞</span><p>+1 (555) 000-0000</p></div>
        <div class="contact-item"><span>📍</span><p>123 Main St, City, Country</p></div>
      </div>
      <form class="contact-form" method="POST" action="/contact">
        <input type="text" name="name" placeholder="Your Name" required/>
        <input type="email" name="email" placeholder="Your Email" required/>
        <input type="text" name="subject" placeholder="Subject"/>
        <textarea name="message" rows="5" placeholder="Your Message" required></textarea>
        <button type="submit" class="btn-primary">Send Message</button>
      </form>
    </div>
  </div>
</section>"""),
    }

    for section_key, (page_title, body_html) in page_map.items():
        if section_key in sections:
            files[f"templates/{section_key}.html"] = _flask_mp_page(section_key, page_title, body_html)

    if has_auth:
        files["templates/login.html"]  = _flask_login_html()
        files["templates/signup.html"] = _flask_signup_html()

    return files


def _flask_mp_app_py(site_name: str, has_auth: bool, has_db: bool, sections: list) -> str:
    """Multi-page Flask app.py with one route per page."""

    page_routes = ""
    page_names = ["about", "services", "portfolio", "products", "blog", "testimonials", "contact"]
    for page in page_names:
        if page in sections:
            page_routes += f"""
@app.route('/{page}')
def {page}():
    return render_template('{page}.html')
"""

    contact_save = """
    import sqlite3
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO contacts (name,email,message) VALUES (?,?,?)', (name, email, message))
    conn.commit(); conn.close()""" if has_db else ""

    auth_block = """
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        import sqlite3
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            flash('Welcome back, ' + username + '!', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        import sqlite3
        try:
            conn = sqlite3.connect('database.db')
            conn.execute('INSERT INTO users (username, password) VALUES (?,?)', (username, password))
            conn.commit(); conn.close()
            flash('Account created! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('Username already taken.', 'error')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
""" if has_auth else ""

    db_init = """
import sqlite3
def init_db():
    conn = sqlite3.connect('database.db')
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, message TEXT, sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    ''')
    conn.commit(); conn.close()
""" if has_db else ""

    return f'''"""
app.py — {site_name}
Generated by WebGen Platform — Multi-page Flask site
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production')
{db_init}
{auth_block}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact_submit():
    name    = request.form.get('name', '')
    email   = request.form.get('email', '')
    message = request.form.get('message', '')
    {contact_save}
    flash(f'Thanks {{name}}! We will get back to you soon.', 'success')
    return redirect(url_for('contact'))
{page_routes}
if __name__ == '__main__':
    {'init_db()' if has_db else '# No database needed'}
    app.run(debug=True)
'''


def _flask_mp_base_html(site_name: str, has_auth: bool, font: str, sections: list) -> str:
    """Clean base.html — ONE navbar, no duplicate."""

    # Build nav links for separate pages
    nav_items = [("Home", "/")]
    page_labels = {
        "about": "About", "services": "Services", "portfolio": "Portfolio",
        "products": "Products", "blog": "Blog", "testimonials": "Testimonials",
        "contact": "Contact",
    }
    for key, label in page_labels.items():
        if key in sections:
            nav_items.append((label, f"/{key}"))

    nav_links_html = "\n      ".join(
        f'<li><a href="{href}">{label}</a></li>' for label, href in nav_items
    )

    auth_html = ""
    if has_auth:
        auth_html = """
      {% if session.user %}
        <li><a href="/logout">Logout</a></li>
      {% else %}
        <li><a href="/login">Login</a></li>
        <li><a href="/signup" class="btn-nav">Sign Up</a></li>
      {% endif %}"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{% block title %}}{site_name}{{% endblock %}}</title>
  <link href="https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@300;400;600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}"/>
</head>
<body>

<header class="site-header">
  <nav class="navbar">
    <a href="/" class="logo">{site_name}</a>
    <ul class="nav-links" id="navLinks">
      {nav_links_html}
      {auth_html}
    </ul>
    <button class="hamburger" onclick="toggleNav()" aria-label="Toggle menu">&#9776;</button>
  </nav>
</header>

{{%- with messages = get_flashed_messages(with_categories=true) %}}
  {{%- if messages %}}
    {{%- for cat, msg in messages %}}
      <div class="flash flash-{{{{ cat }}}}">{{{{ msg }}}}</div>
    {{%- endfor %}}
  {{%- endif %}}
{{%- endwith %}}

{{%- block content %}}{{%- endblock %}}

<footer class="site-footer">
  <div class="footer-content">
    <div class="footer-brand">
      <div class="logo">{site_name}</div>
      <p>Building the future, one project at a time.</p>
    </div>
    <div class="footer-links">
      <h4>Quick Links</h4>
      <ul>
        {chr(10).join(f'<li><a href="{href}">{label}</a></li>' for label, href in nav_items)}
      </ul>
    </div>
  </div>
  <div class="footer-bottom"><p>&copy; 2025 {site_name}. All rights reserved.</p></div>
</footer>

<script src="{{{{ url_for('static', filename='js/script.js') }}}}"></script>
{{%- block scripts %}}{{%- endblock %}}
</body>
</html>"""


def _flask_mp_page(page_key: str, title: str, body_html: str) -> str:
    """Generate a single page template that extends base.html."""
    return f"""{{% extends 'base.html' %}}
{{% block title %}}{title}{{% endblock %}}
{{% block content %}}
{body_html}
{{% endblock %}}"""


