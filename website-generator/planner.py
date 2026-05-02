"""
planner.py — AI Design & Architecture Planner
Step 1: Intent Analysis  — extract type, features, UI style, complexity
Step 2: Auto Design      — decide colors, layout, components, UX flow
Step 3: Architecture     — frontend/backend structure, DB schema, API routes

This module sits between nlp.parse_prompt() and generator.build_project().
It enriches the config with a full architecture plan before code generation.
"""
import re

# ── Complexity signals ────────────────────────────────────────────────────────
COMPLEXITY_ADVANCED = [
    "meesho", "shopify", "amazon", "flipkart", "admin panel", "dashboard",
    "analytics", "cms", "blog system", "full stack", "fullstack", "saas",
    "platform", "marketplace", "multi-user", "role", "permission",
    "animation", "gsap", "parallax", "3d", "interactive",
]
COMPLEXITY_MEDIUM = [
    "login", "signup", "auth", "database", "backend", "flask", "python",
    "portfolio", "contact form", "gallery", "blog", "pricing",
]

# ── UI style signals ──────────────────────────────────────────────────────────
UI_STYLES = {
    "glassmorphism": ["glass", "glassmorphism", "frosted", "blur"],
    "neumorphism":   ["neumorphism", "soft ui", "neomorphism"],
    "brutalist":     ["brutalist", "bold", "raw", "stark"],
    "gradient":      ["gradient", "colorful", "vibrant", "neon"],
    "minimal":       ["minimal", "clean", "white space", "simple", "flat"],
    "dark":          ["dark", "night", "black", "dark mode"],
    "saas":          ["saas", "startup", "landing", "product", "app"],
    "corporate":     ["corporate", "enterprise", "professional", "business"],
    "creative":      ["creative", "animation", "animated", "portfolio", "artistic"],
}

# ── Special platform signals ──────────────────────────────────────────────────
PLATFORM_SIGNALS = {
    "meesho":    ["meesho", "seller dashboard", "reseller", "social commerce"],
    "shopify":   ["shopify", "ecommerce platform", "online store", "product catalog"],
    "wordpress": ["wordpress", "cms", "blog system", "content management"],
    "airbnb":    ["airbnb", "booking", "rental", "listing"],
    "twitter":   ["twitter", "social", "feed", "timeline", "post"],
    "notion":    ["notion", "notes", "workspace", "productivity"],
    "startup":   ["startup", "landing page", "saas", "product launch", "waitlist"],
}

# ── DB schema templates ───────────────────────────────────────────────────────
DB_SCHEMAS = {
    "ecommerce": {
        "tables": [
            {
                "name": "sellers",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "username TEXT UNIQUE NOT NULL",
                    "password TEXT NOT NULL",
                    "shop_name TEXT",
                    "email TEXT",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
            {
                "name": "products",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "seller_id INTEGER NOT NULL REFERENCES sellers(id)",
                    "name TEXT NOT NULL",
                    "description TEXT",
                    "price REAL NOT NULL",
                    "stock INTEGER DEFAULT 0",
                    "category TEXT",
                    "image TEXT",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
            {
                "name": "orders",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "product_id INTEGER NOT NULL REFERENCES products(id)",
                    "buyer_name TEXT NOT NULL",
                    "buyer_email TEXT NOT NULL",
                    "quantity INTEGER DEFAULT 1",
                    "total_price REAL",
                    "status TEXT DEFAULT 'pending'",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
        ]
    },
    "blog": {
        "tables": [
            {
                "name": "users",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "username TEXT UNIQUE NOT NULL",
                    "password TEXT NOT NULL",
                    "role TEXT DEFAULT 'author'",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
            {
                "name": "posts",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "author_id INTEGER NOT NULL REFERENCES users(id)",
                    "title TEXT NOT NULL",
                    "slug TEXT UNIQUE NOT NULL",
                    "content TEXT NOT NULL",
                    "excerpt TEXT",
                    "category TEXT",
                    "tags TEXT",
                    "status TEXT DEFAULT 'draft'",
                    "published_at TIMESTAMP",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
            {
                "name": "comments",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "post_id INTEGER NOT NULL REFERENCES posts(id)",
                    "author_name TEXT NOT NULL",
                    "author_email TEXT NOT NULL",
                    "content TEXT NOT NULL",
                    "approved INTEGER DEFAULT 0",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
        ]
    },
    "portfolio": {
        "tables": [
            {
                "name": "projects",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "title TEXT NOT NULL",
                    "description TEXT",
                    "category TEXT",
                    "image TEXT",
                    "url TEXT",
                    "tags TEXT",
                    "featured INTEGER DEFAULT 0",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
            {
                "name": "contacts",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "name TEXT NOT NULL",
                    "email TEXT NOT NULL",
                    "subject TEXT",
                    "message TEXT NOT NULL",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
        ]
    },
    "business": {
        "tables": [
            {
                "name": "contacts",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "name TEXT NOT NULL",
                    "email TEXT NOT NULL",
                    "phone TEXT",
                    "subject TEXT",
                    "message TEXT NOT NULL",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
            {
                "name": "newsletter",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "email TEXT UNIQUE NOT NULL",
                    "subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
        ]
    },
    "startup": {
        "tables": [
            {
                "name": "waitlist",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "email TEXT UNIQUE NOT NULL",
                    "name TEXT",
                    "source TEXT",
                    "joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
            {
                "name": "contacts",
                "columns": [
                    "id INTEGER PRIMARY KEY AUTOINCREMENT",
                    "name TEXT NOT NULL",
                    "email TEXT NOT NULL",
                    "message TEXT NOT NULL",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ],
            },
        ]
    },
}

# ── API route templates ───────────────────────────────────────────────────────
API_ROUTES = {
    "ecommerce": [
        {"method": "GET",  "path": "/",                      "desc": "Public storefront — browse products"},
        {"method": "GET",  "path": "/products",              "desc": "Product listing with category filter"},
        {"method": "POST", "path": "/buy/<pid>",             "desc": "Place an order for a product"},
        {"method": "GET",  "path": "/login",                 "desc": "Seller login page"},
        {"method": "POST", "path": "/login",                 "desc": "Authenticate seller"},
        {"method": "GET",  "path": "/signup",                "desc": "Seller registration page"},
        {"method": "POST", "path": "/signup",                "desc": "Create seller account"},
        {"method": "GET",  "path": "/logout",                "desc": "Clear session"},
        {"method": "GET",  "path": "/dashboard",             "desc": "Seller dashboard — stats + products"},
        {"method": "GET",  "path": "/product/add",           "desc": "Add product form"},
        {"method": "POST", "path": "/product/add",           "desc": "Save new product"},
        {"method": "GET",  "path": "/product/edit/<pid>",    "desc": "Edit product form"},
        {"method": "POST", "path": "/product/edit/<pid>",    "desc": "Update product"},
        {"method": "POST", "path": "/product/delete/<pid>",  "desc": "Delete product"},
        {"method": "GET",  "path": "/orders",                "desc": "All orders for seller"},
        {"method": "POST", "path": "/order/update/<oid>",    "desc": "Update order status"},
    ],
    "blog": [
        {"method": "GET",  "path": "/",                      "desc": "Blog homepage — latest posts"},
        {"method": "GET",  "path": "/post/<slug>",           "desc": "Single post view"},
        {"method": "GET",  "path": "/category/<cat>",        "desc": "Posts by category"},
        {"method": "POST", "path": "/post/<id>/comment",     "desc": "Submit a comment"},
        {"method": "GET",  "path": "/login",                 "desc": "Admin login"},
        {"method": "POST", "path": "/login",                 "desc": "Authenticate admin"},
        {"method": "GET",  "path": "/admin",                 "desc": "Admin dashboard"},
        {"method": "GET",  "path": "/admin/post/new",        "desc": "New post editor"},
        {"method": "POST", "path": "/admin/post/new",        "desc": "Save new post"},
        {"method": "GET",  "path": "/admin/post/edit/<id>",  "desc": "Edit post"},
        {"method": "POST", "path": "/admin/post/edit/<id>",  "desc": "Update post"},
        {"method": "POST", "path": "/admin/post/delete/<id>","desc": "Delete post"},
    ],
    "flask": [
        {"method": "GET",  "path": "/",                      "desc": "Homepage"},
        {"method": "POST", "path": "/contact",               "desc": "Submit contact form"},
        {"method": "GET",  "path": "/login",                 "desc": "Login page"},
        {"method": "POST", "path": "/login",                 "desc": "Authenticate user"},
        {"method": "GET",  "path": "/signup",                "desc": "Registration page"},
        {"method": "POST", "path": "/signup",                "desc": "Create account"},
        {"method": "GET",  "path": "/logout",                "desc": "Logout"},
    ],
    "static": [
        {"method": "—", "path": "index.html",  "desc": "Main page (static file)"},
        {"method": "—", "path": "style.css",   "desc": "Stylesheet"},
        {"method": "—", "path": "script.js",   "desc": "JavaScript"},
    ],
    "startup": [
        {"method": "GET",  "path": "/",                      "desc": "Landing page"},
        {"method": "POST", "path": "/waitlist",              "desc": "Join waitlist (email capture)"},
        {"method": "POST", "path": "/contact",               "desc": "Contact form submission"},
        {"method": "GET",  "path": "/admin",                 "desc": "Admin — view waitlist"},
    ],
    "blog": [
        {"method": "GET",  "path": "/",                      "desc": "Blog homepage — latest posts"},
        {"method": "GET",  "path": "/post/<slug>",           "desc": "Single post view"},
        {"method": "GET",  "path": "/?category=<cat>",       "desc": "Posts by category"},
        {"method": "POST", "path": "/post/<id>/comment",     "desc": "Submit a comment"},
        {"method": "GET",  "path": "/login",                 "desc": "Admin login"},
        {"method": "POST", "path": "/login",                 "desc": "Authenticate admin"},
        {"method": "GET",  "path": "/logout",                "desc": "Logout"},
        {"method": "GET",  "path": "/admin",                 "desc": "Admin dashboard"},
        {"method": "GET",  "path": "/admin/post/new",        "desc": "New post editor"},
        {"method": "POST", "path": "/admin/post/new",        "desc": "Save new post"},
        {"method": "GET",  "path": "/admin/post/edit/<id>",  "desc": "Edit post"},
        {"method": "POST", "path": "/admin/post/edit/<id>",  "desc": "Update post"},
        {"method": "POST", "path": "/admin/post/delete/<id>","desc": "Delete post"},
        {"method": "POST", "path": "/admin/comment/approve/<id>","desc": "Approve comment"},
        {"method": "POST", "path": "/admin/comment/delete/<id>","desc": "Delete comment"},
    ],
    "portfolio_adv": [
        {"method": "—", "path": "index.html",  "desc": "Animated portfolio (static)"},
        {"method": "—", "path": "style.css",   "desc": "Dark theme + animations"},
        {"method": "—", "path": "script.js",   "desc": "Typewriter, scroll reveal, counters"},
    ],
}

# ── Component lists ───────────────────────────────────────────────────────────
COMPONENT_LISTS = {
    "ecommerce": [
        "Sticky navbar with cart icon",
        "Hero banner with CTA",
        "Category filter bar",
        "Product grid with cards",
        "Product image + buy modal",
        "Seller dashboard sidebar",
        "Stats cards (revenue, orders, products)",
        "Product CRUD forms",
        "Orders table with status badges",
        "Flash message system",
        "Responsive mobile layout",
    ],
    "blog": [
        "Navigation with search",
        "Hero with featured post",
        "Post card grid",
        "Single post view with typography",
        "Comment section",
        "Category sidebar",
        "Admin post editor (textarea)",
        "Admin dashboard",
        "Pagination",
        "Tag cloud",
    ],
    "portfolio": [
        "Animated hero with typewriter effect",
        "About section with skills",
        "Portfolio grid with hover overlay",
        "Project modal/detail view",
        "Testimonials carousel",
        "Contact form",
        "Scroll reveal animations",
        "Sticky nav with active state",
        "Social links",
        "Back-to-top button",
    ],
    "startup": [
        "Hero with gradient + CTA",
        "Social proof / logos bar",
        "Features grid (3-col)",
        "How it works (steps)",
        "Pricing cards (3 tiers)",
        "Testimonials",
        "FAQ accordion",
        "Email waitlist form",
        "Footer with links",
        "Sticky nav with CTA button",
    ],
    "business": [
        "Sticky navbar",
        "Hero section",
        "Services grid",
        "About section with stats",
        "Testimonials",
        "Contact form",
        "Footer",
    ],
}

# ── UX flow templates ─────────────────────────────────────────────────────────
UX_FLOWS = {
    "ecommerce": [
        "Visitor lands on storefront → browses products",
        "Filters by category → views product detail",
        "Clicks Buy Now → fills order form → order confirmed",
        "Seller visits /login → authenticates",
        "Seller goes to /dashboard → sees stats + products",
        "Seller adds/edits/deletes products",
        "Seller views and updates order statuses",
    ],
    "blog": [
        "Reader lands on homepage → sees latest posts",
        "Clicks post → reads full article",
        "Leaves a comment → awaits moderation",
        "Admin logs in → goes to /admin",
        "Admin creates/edits/publishes posts",
        "Admin moderates comments",
    ],
    "portfolio": [
        "Visitor lands → animated hero grabs attention",
        "Scrolls to portfolio → views projects",
        "Clicks project → sees detail/modal",
        "Scrolls to contact → sends message",
    ],
    "startup": [
        "Visitor lands → hero with value proposition",
        "Scrolls features → understands product",
        "Views pricing → selects plan",
        "Joins waitlist → email captured",
        "Reads FAQ → objections handled",
    ],
    "business": [
        "Visitor lands → hero with CTA",
        "Views services → understands offering",
        "Reads testimonials → builds trust",
        "Fills contact form → lead captured",
    ],
}


def analyze_intent(prompt: str) -> dict:
    """
    Step 1: Deep intent analysis.
    Returns enriched intent dict beyond basic nlp.parse_prompt().
    """
    text = prompt.lower().strip()

    # Detect complexity
    complexity = "simple"
    if any(k in text for k in COMPLEXITY_ADVANCED):
        complexity = "advanced"
    elif any(k in text for k in COMPLEXITY_MEDIUM):
        complexity = "medium"

    # Detect UI style
    ui_style = "saas"
    for style, keywords in UI_STYLES.items():
        if any(k in text for k in keywords):
            ui_style = style
            break

    # Detect platform reference
    platform_ref = None
    for platform, keywords in PLATFORM_SIGNALS.items():
        if any(k in text for k in keywords):
            platform_ref = platform
            break

    # Detect special modes
    is_startup   = any(k in text for k in PLATFORM_SIGNALS["startup"])
    has_animation = any(k in text for k in ["animation", "animated", "animate", "gsap",
                                             "parallax", "scroll effect", "typewriter",
                                             "fade", "slide", "motion"])
    has_pricing  = any(k in text for k in ["pricing", "plan", "subscription", "tier", "cost"])
    has_admin    = any(k in text for k in ["admin", "admin panel", "cms", "manage", "dashboard"])
    has_waitlist = any(k in text for k in ["waitlist", "wait list", "early access", "coming soon", "launch"])

    return {
        "complexity":    complexity,
        "ui_style":      ui_style,
        "platform_ref":  platform_ref,
        "is_startup":    is_startup,
        "has_animation": has_animation,
        "has_pricing":   has_pricing,
        "has_admin":     has_admin,
        "has_waitlist":  has_waitlist,
    }


def auto_design(config: dict, intent: dict) -> dict:
    """
    Step 2: Auto design decisions.
    Returns design config: colors, layout, components, UX flow.
    """
    wtype    = config.get("website_type", "business")
    ptype    = config.get("project_type", "static")
    ui_style = intent.get("ui_style", "saas")

    # Resolve effective type for components/UX
    eff_type = wtype
    if intent.get("is_startup"):
        eff_type = "startup"
    elif ptype == "ecommerce":
        eff_type = "ecommerce"

    # Component list
    components = COMPONENT_LISTS.get(eff_type, COMPONENT_LISTS["business"])
    if intent.get("has_pricing") and "Pricing cards (3 tiers)" not in components:
        components = components + ["Pricing cards (3 tiers)"]
    if intent.get("has_animation") and "Scroll reveal animations" not in components:
        components = components + ["Scroll reveal animations", "CSS keyframe animations"]
    if intent.get("has_admin") and "Admin dashboard" not in components:
        components = components + ["Admin dashboard", "Admin CRUD interface"]

    # UX flow
    ux_flow = UX_FLOWS.get(eff_type, UX_FLOWS["business"])

    # Layout decision
    layout = _decide_layout(wtype, ui_style, intent)

    return {
        "effective_type": eff_type,
        "ui_style":       ui_style,
        "layout":         layout,
        "components":     components,
        "ux_flow":        ux_flow,
    }


def build_architecture(config: dict, intent: dict, design: dict) -> dict:
    """
    Step 3: Full architecture plan.
    Returns frontend_structure, backend_structure, db_schema, api_routes.
    """
    ptype    = config.get("project_type", "static")
    wtype    = config.get("website_type", "business")
    eff_type = design.get("effective_type", wtype)

    # Frontend structure
    frontend = _frontend_structure(ptype, eff_type, config)

    # Backend structure
    backend = _backend_structure(ptype, eff_type, config, intent)

    # DB schema
    schema_key = eff_type if eff_type in DB_SCHEMAS else (
        "ecommerce" if ptype == "ecommerce" else
        "blog"      if wtype == "blog" else
        "portfolio" if wtype == "portfolio" else
        "startup"   if intent.get("is_startup") else
        "business"
    )
    db_schema = DB_SCHEMAS.get(schema_key, DB_SCHEMAS["business"]) if ptype != "static" else None

    # API routes
    route_key = ptype if ptype in API_ROUTES else "flask"
    if eff_type == "startup":
        route_key = "startup"
    elif eff_type in API_ROUTES:
        route_key = eff_type
    api_routes = API_ROUTES.get(route_key, API_ROUTES["static"])

    return {
        "frontend":   frontend,
        "backend":    backend,
        "db_schema":  db_schema,
        "api_routes": api_routes,
    }


def full_plan(prompt: str, config: dict) -> dict:
    """
    Run all 3 planning steps and return the complete plan.
    """
    intent  = analyze_intent(prompt)
    design  = auto_design(config, intent)
    arch    = build_architecture(config, intent, design)

    return {
        "intent":  intent,
        "design":  design,
        "arch":    arch,
    }


# ── Private helpers ───────────────────────────────────────────────────────────

def _decide_layout(wtype: str, ui_style: str, intent: dict) -> dict:
    """Decide layout structure based on type and style."""
    layouts = {
        "ecommerce": {"type": "sidebar-main", "nav": "sticky-top", "grid": "product-grid"},
        "blog":      {"type": "content-sidebar", "nav": "sticky-top", "grid": "post-list"},
        "portfolio": {"type": "full-width", "nav": "transparent-overlay", "grid": "masonry"},
        "startup":   {"type": "full-width-sections", "nav": "sticky-cta", "grid": "feature-grid"},
        "business":  {"type": "full-width-sections", "nav": "sticky-top", "grid": "card-grid"},
    }
    base = layouts.get(wtype, layouts["business"])
    if ui_style == "dark":
        base["color_mode"] = "dark"
    elif ui_style == "minimal":
        base["color_mode"] = "light-minimal"
    else:
        base["color_mode"] = "light"
    return base


def _frontend_structure(ptype: str, eff_type: str, config: dict) -> dict:
    if ptype == "static":
        return {
            "type":      "Static HTML/CSS/JS",
            "files":     ["index.html", "style.css", "script.js"],
            "framework": "Vanilla (no framework)",
            "responsive": "CSS Grid + Flexbox, mobile-first",
            "fonts":     f"Google Fonts — {config.get('font', 'Poppins')}",
        }
    templates = ["base.html", "index.html"]
    if eff_type == "ecommerce":
        templates += ["dashboard.html", "add_product.html", "edit_product.html",
                      "orders.html", "login.html"]
    elif eff_type == "blog":
        templates += ["post.html", "admin.html", "admin_post.html", "login.html"]
    elif config.get("has_auth"):
        templates += ["login.html", "signup.html"]

    return {
        "type":       "Jinja2 Templates (Flask)",
        "templates":  templates,
        "static":     ["static/css/style.css", "static/js/script.js"],
        "responsive": "CSS Grid + Flexbox, mobile-first",
        "fonts":      f"Google Fonts — {config.get('font', 'Poppins')}",
    }


def _backend_structure(ptype: str, eff_type: str, config: dict, intent: dict) -> dict:
    if ptype == "static":
        return {"type": "None (static site)", "server": "—", "database": "—"}

    routes_count = len(API_ROUTES.get(eff_type, API_ROUTES.get(ptype, API_ROUTES["flask"])))
    features = ["Flask application factory", "Jinja2 template rendering",
                "SQLite via sqlite3", "Session management"]
    if config.get("has_auth") or eff_type in ("ecommerce", "blog"):
        features += ["Werkzeug password hashing", "Login/logout routes",
                     "login_required decorator"]
    if eff_type == "ecommerce":
        features += ["File upload (Werkzeug)", "Product CRUD", "Order management"]
    if intent.get("has_admin"):
        features += ["Admin panel routes", "Role-based access"]

    return {
        "type":       "Python Flask",
        "server":     "Flask dev server (python app.py)",
        "database":   "SQLite (database.db, auto-created)",
        "routes":     routes_count,
        "features":   features,
    }
