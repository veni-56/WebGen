"""
codegen.py — Advanced Structured Code Generation Engine
Implements the 3-step AI pipeline:
  Step 1: Intent Analysis  (planner.analyze_intent)
  Step 2: Auto Design      (planner.auto_design)
  Step 3: Architecture     (planner.build_architecture)
  Step 4: Code Generation  (generator.build_project)

Output format (strict):
  project_name, architecture_plan, folder_structure, files,
  database_schema, api_routes, run_instructions, deployment_guide
"""
import re
import json
from pathlib import Path

from nlp import parse_prompt
from generator import build_project, read_file, GENERATED_DIR
from planner import full_plan

# ── Run instructions ──────────────────────────────────────────────────────────
RUN_INSTRUCTIONS = {
    "static": [
        "No installation needed.",
        "Open <code>index.html</code> in any web browser.",
        "That's it — your website is live locally!",
    ],
    "flask": [
        "Install Python 3.8+ if not already installed.",
        "<code>pip install -r requirements.txt</code>",
        "<code>python app.py</code>",
        "Open <code>http://localhost:5000</code> in your browser.",
        "SQLite database is created automatically on first run.",
    ],
    "ecommerce": [
        "Install Python 3.8+ if not already installed.",
        "<code>pip install -r requirements.txt</code>",
        "<code>python app.py</code>",
        "Open <code>http://localhost:5000</code> — public marketplace storefront.",
        "<strong>Admin login:</strong> <code>admin@marketplace.com</code> / <code>admin123</code>",
        "Register as a <strong>Seller</strong> at <code>/signup</code> → manage products at <code>/seller/dashboard</code>.",
        "Register as a <strong>Customer</strong> at <code>/signup</code> → browse, cart, checkout.",
        "On checkout a <code>PAY-XXXXXXXX</code> reference is generated. 90% goes to seller, 10% platform commission.",
        "Admin panel at <code>/admin</code> — manage users, products, orders, earnings.",
        "Product images stored in <code>static/uploads/</code>.",
    ],
    "startup": [
        "Install Python 3.8+ if not already installed.",
        "<code>pip install -r requirements.txt</code>",
        "<code>python app.py</code>",
        "Open <code>http://localhost:5000</code> — landing page.",
        "Waitlist signups stored in <code>database.db</code>.",
        "View signups at <code>/admin</code>.",
    ],
    "blog": [
        "Install Python 3.8+ if not already installed.",
        "<code>pip install -r requirements.txt</code>",
        "<code>python app.py</code>",
        "Open <code>http://localhost:5000</code> — public blog.",
        "Create admin user (see README.txt for instructions).",
        "Login at <code>/login</code> → manage posts at <code>/admin</code>.",
    ],
    "portfolio_adv": [
        "No installation needed.",
        "Open <code>index.html</code> in any web browser.",
        "All animations work out of the box!",
        "Customize content directly in <code>index.html</code>.",
    ],
}

# ── Deployment guide ──────────────────────────────────────────────────────────
DEPLOYMENT_GUIDES = {
    "static": {
        "local": ["Open index.html directly in browser — no server needed."],
        "netlify": ["Drag & drop the project folder to netlify.com/drop", "Your site is live instantly with a free URL."],
        "github_pages": ["Push files to a GitHub repository.", "Go to Settings → Pages → select main branch.", "Site is live at https://username.github.io/repo"],
        "docker": None,
    },
    "portfolio_adv": {
        "local": ["Open index.html directly in browser — no server needed."],
        "netlify": ["Drag & drop the project folder to netlify.com/drop", "Your site is live instantly with a free URL."],
        "github_pages": ["Push files to a GitHub repository.", "Go to Settings → Pages → select main branch."],
        "docker": None,
    },
    "flask": {
        "local": ["pip install -r requirements.txt", "python app.py", "Visit http://localhost:5000"],
        "render": ["Push project to GitHub.", "Create new Web Service on render.com.", "Set Build Command: pip install -r requirements.txt", "Set Start Command: python app.py", "Deploy — free tier available."],
        "railway": ["Push project to GitHub.", "Connect repo on railway.app.", "Railway auto-detects Flask and deploys."],
        "docker": ["FROM python:3.11-slim", "WORKDIR /app", "COPY requirements.txt .", "RUN pip install -r requirements.txt", "COPY . .", "EXPOSE 5000", 'CMD ["python", "app.py"]'],
        "env_vars": ["SECRET_KEY=your-secret-key-here", "FLASK_ENV=production"],
    },
    "startup": {
        "local": ["pip install -r requirements.txt", "python app.py", "Visit http://localhost:5000"],
        "render": ["Push project to GitHub.", "Create new Web Service on render.com.", "Set Build Command: pip install -r requirements.txt", "Set Start Command: python app.py"],
        "docker": ["FROM python:3.11-slim", "WORKDIR /app", "COPY requirements.txt .", "RUN pip install -r requirements.txt", "COPY . .", "EXPOSE 5000", 'CMD ["python", "app.py"]'],
        "env_vars": ["SECRET_KEY=your-secret-key-here", "FLASK_ENV=production"],
    },
    "blog": {
        "local": ["pip install -r requirements.txt", "python app.py", "Visit http://localhost:5000", "Create admin user (see README.txt)"],
        "render": ["Push project to GitHub.", "Create new Web Service on render.com.", "Set Build Command: pip install -r requirements.txt", "Set Start Command: python app.py"],
        "docker": ["FROM python:3.11-slim", "WORKDIR /app", "COPY requirements.txt .", "RUN pip install -r requirements.txt", "COPY . .", "EXPOSE 5000", 'CMD ["python", "app.py"]'],
        "env_vars": ["SECRET_KEY=your-secret-key-here", "FLASK_ENV=production"],
    },
    "ecommerce": {
        "local": ["pip install -r requirements.txt", "python app.py", "Visit http://localhost:5000"],
        "render": ["Push project to GitHub.", "Create new Web Service on render.com.", "Set Build Command: pip install -r requirements.txt", "Set Start Command: python app.py", "Add environment variable: SECRET_KEY=<random-string>"],
        "docker": ["FROM python:3.11-slim", "WORKDIR /app", "COPY requirements.txt .", "RUN pip install -r requirements.txt", "COPY . .", "RUN mkdir -p static/uploads", "EXPOSE 5000", 'CMD ["python", "app.py"]'],
        "env_vars": ["SECRET_KEY=your-secret-key-here", "FLASK_ENV=production"],
    },
}


def slugify(name: str) -> str:
    """Convert a site name to a safe folder name."""
    name = name.lower().strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_-]+", "_", name)
    return name or "my_website"


def generate_structured(prompt: str, project_id: str) -> dict:
    """
    Main entry point — full 4-step pipeline.

    Returns strict output format:
      project_name, architecture_plan, folder_structure, files,
      database_schema, api_routes, run_instructions, deployment_guide,
      intent, design, summary, config, type, total_files, total_lines
    """
    # ── Step 1 & 2: Parse NLP config ─────────────────────────────────────────
    config = parse_prompt(prompt)
    ptype  = config["project_type"]

    # ── Step 2 & 3: Full planner (intent + design + architecture) ────────────
    plan = full_plan(prompt, config)
    intent = plan["intent"]
    design = plan["design"]
    arch   = plan["arch"]

    # ── Step 4: Generate all files ────────────────────────────────────────────
    result = build_project(project_id, config)

    # ── Read all generated file contents ─────────────────────────────────────
    files_out = []
    for filepath in result["files"]:
        content = read_file(project_id, filepath)
        if content is None or (len(content.strip()) == 0 and filepath.endswith(".gitkeep")):
            continue
        files_out.append({
            "path":     filepath,
            "code":     content,
            "language": _detect_language(filepath),
            "lines":    content.count("\n") + 1,
        })

    # ── Build project name ────────────────────────────────────────────────────
    project_name = slugify(config.get("site_name", "my_website"))

    # ── Folder tree ───────────────────────────────────────────────────────────
    folder_tree = _build_folder_tree(result["files"], project_name)

    # ── Architecture plan (human-readable) ───────────────────────────────────
    architecture_plan = _build_architecture_plan(config, intent, design, arch)

    # ── DB schema (formatted) ─────────────────────────────────────────────────
    db_schema = _format_db_schema(arch.get("db_schema"))

    # ── API routes ────────────────────────────────────────────────────────────
    api_routes = arch.get("api_routes", [])

    # ── Run instructions ──────────────────────────────────────────────────────
    run_instructions = RUN_INSTRUCTIONS.get(ptype, RUN_INSTRUCTIONS["static"])

    # ── Deployment guide ──────────────────────────────────────────────────────
    deployment_guide = DEPLOYMENT_GUIDES.get(ptype, DEPLOYMENT_GUIDES["static"])

    # ── Summary ───────────────────────────────────────────────────────────────
    summary = _build_summary(config, intent, design)

    return {
        # Core identifiers
        "project_id":        project_id,
        "project_name":      project_name,
        "site_name":         config.get("site_name", "My Website"),
        "type":              ptype,
        "website_type":      config.get("website_type", "business"),
        "theme":             config.get("theme", "modern"),

        # Step 1: Intent
        "intent":            intent,

        # Step 2: Design
        "design":            design,

        # Step 3: Architecture
        "architecture_plan": architecture_plan,
        "db_schema":         db_schema,
        "api_routes":        api_routes,
        "deployment_guide":  deployment_guide,

        # Step 4: Generated files
        "folder_tree":       folder_tree,
        "files":             files_out,
        "run_instructions":  run_instructions,

        # Meta
        "config":            config,
        "summary":           summary,
        "total_files":       len(files_out),
        "total_lines":       sum(f["lines"] for f in files_out),
    }


# ── Private helpers ───────────────────────────────────────────────────────────

def _detect_language(filepath: str) -> str:
    ext = filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""
    return {
        "py": "python", "html": "html", "css": "css",
        "js": "javascript", "txt": "text", "md": "markdown",
        "json": "json", "sql": "sql",
    }.get(ext, "text")


def _build_folder_tree(files: list, project_name: str) -> list:
    """Build a visual ├── / └── folder tree from a flat file list."""
    tree = {}
    for f in sorted(files):
        parts = Path(f).parts
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part + "/", {})
        node[parts[-1]] = None

    lines = [f"{project_name}/"]
    _render_tree(tree, lines, prefix="")
    return lines


def _render_tree(node: dict, lines: list, prefix: str) -> None:
    items = list(node.items())
    for i, (name, children) in enumerate(items):
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + name)
        if children is not None:
            extension = "    " if is_last else "│   "
            _render_tree(children, lines, prefix + extension)


def _build_architecture_plan(config: dict, intent: dict, design: dict, arch: dict) -> dict:
    """Build a structured, human-readable architecture plan."""
    ptype    = config.get("project_type", "static")
    wtype    = config.get("website_type", "business")
    eff_type = design.get("effective_type", wtype)

    frontend = arch.get("frontend", {})
    backend  = arch.get("backend", {})

    return {
        "complexity":   intent.get("complexity", "simple"),
        "ui_style":     intent.get("ui_style", "saas"),
        "platform_ref": intent.get("platform_ref"),

        "frontend": {
            "type":       frontend.get("type", "Static HTML/CSS/JS"),
            "templates":  frontend.get("templates", ["index.html"]),
            "static":     frontend.get("static", ["style.css", "script.js"]),
            "responsive": frontend.get("responsive", "CSS Grid + Flexbox, mobile-first"),
            "fonts":      frontend.get("fonts", f"Google Fonts — {config.get('font','Poppins')}"),
        },

        "backend": {
            "type":     backend.get("type", "None (static site)"),
            "server":   backend.get("server", "—"),
            "database": backend.get("database", "—"),
            "routes":   backend.get("routes", 0),
            "features": backend.get("features", []),
        },

        "components":  design.get("components", []),
        "ux_flow":     design.get("ux_flow", []),
        "layout":      design.get("layout", {}),

        "special_features": {
            "has_animation": intent.get("has_animation", False),
            "has_pricing":   intent.get("has_pricing", False),
            "has_admin":     intent.get("has_admin", False),
            "has_waitlist":  intent.get("has_waitlist", False),
            "has_auth":      config.get("has_auth", False),
            "has_db":        config.get("has_db", False),
        },
    }


def _format_db_schema(schema: dict | None) -> list | None:
    """Format DB schema dict into list of SQL CREATE TABLE strings."""
    if not schema:
        return None
    tables = []
    for table in schema.get("tables", []):
        cols = ",\n    ".join(table["columns"])
        sql = f"CREATE TABLE IF NOT EXISTS {table['name']} (\n    {cols}\n);"
        tables.append({"name": table["name"], "sql": sql, "columns": table["columns"]})
    return tables


def _build_summary(config: dict, intent: dict, design: dict) -> dict:
    """Human-readable summary of what was generated."""
    ptype    = config.get("project_type", "static")
    wtype    = config.get("website_type", "business")
    eff_type = design.get("effective_type", wtype)

    features = []
    if ptype == "ecommerce":
        features = [
            "Multi-vendor marketplace (Meesho-style)",
            "3 roles: Admin / Seller / Customer",
            "Seller dashboard + product CRUD",
            "Image upload support",
            "Customer storefront with search & filters",
            "Cart & checkout system",
            "Payment split: 90% seller / 10% platform",
            "SellerEarnings + PlatformEarnings tracking",
            "Order status flow (paid → confirmed → shipped → delivered)",
            "Admin panel: users, products, orders, earnings",
            "SQLite database (7 tables)",
        ]
    elif ptype == "flask":
        features = ["Flask routes", "Jinja2 templates", "Contact form", "SQLite DB"]
        if config.get("has_auth"):
            features += ["Login / Signup", "Session management", "Password hashing"]
    else:
        features = ["Responsive HTML", "Custom CSS theme", "JavaScript interactions",
                    "Smooth scroll", "Mobile navigation", "Scroll reveal animations"]

    if intent.get("has_pricing"):
        features.append("Pricing section")
    if intent.get("has_animation"):
        features.append("CSS animations")
    if intent.get("has_admin"):
        features.append("Admin panel")
    if intent.get("has_waitlist"):
        features.append("Waitlist / email capture")

    return {
        "stack":      ptype,
        "type":       wtype,
        "eff_type":   eff_type,
        "complexity": intent.get("complexity", "simple"),
        "ui_style":   intent.get("ui_style", "saas"),
        "theme":      config.get("theme", "modern"),
        "font":       config.get("font", "Poppins"),
        "sections":   config.get("sections", []),
        "features":   features,
        "has_auth":   config.get("has_auth", False),
        "has_db":     config.get("has_db", False),
    }
