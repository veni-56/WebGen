"""
nlp.py — Natural Language Intent Parser for WebGen Platform.
Converts free-text prompts into structured website configs.
No external AI API required — uses keyword matching + heuristics.
"""
import re

# ── Theme presets ─────────────────────────────────────────────────────────────
THEMES = {
    "modern":   {"primary": "#6c63ff", "secondary": "#f50057", "font": "Poppins"},
    "minimal":  {"primary": "#212121", "secondary": "#ff9800", "font": "Inter"},
    "business": {"primary": "#1565c0", "secondary": "#e91e63", "font": "Roboto"},
    "nature":   {"primary": "#2e7d32", "secondary": "#ffc107", "font": "Nunito"},
    "dark":     {"primary": "#bb86fc", "secondary": "#03dac6", "font": "Inter"},
    "warm":     {"primary": "#e91e63", "secondary": "#ff5722", "font": "Montserrat"},
    "ocean":    {"primary": "#00897b", "secondary": "#ff6f00", "font": "Lato"},
    "luxury":   {"primary": "#b8860b", "secondary": "#8b0000", "font": "Raleway"},
}

# ── Keyword maps ──────────────────────────────────────────────────────────────
TYPE_KEYWORDS = {
    "portfolio":  ["portfolio", "showcase", "personal", "resume", "cv", "work", "projects",
                   "designer", "developer", "freelance", "creative", "artist", "photographer"],
    "ecommerce":  ["ecommerce", "e-commerce", "shop", "store", "sell", "seller", "product",
                   "meesho", "amazon", "shopify", "flipkart", "marketplace", "buy", "cart",
                   "order", "inventory", "catalog", "reseller"],
    "blog":       ["blog", "article", "post", "write", "news", "magazine", "journal",
                   "content", "cms", "editorial", "publication"],
    "business":   ["business", "company", "agency", "corporate", "service", "startup",
                   "saas", "landing", "professional", "launch", "product launch",
                   "ai tool", "app", "platform", "waitlist"],
}

SECTION_KEYWORDS = {
    "hero":         ["hero", "banner", "landing", "welcome", "intro", "above the fold"],
    "about":        ["about", "story", "team", "who we are", "mission", "vision"],
    "services":     ["service", "offer", "what we do", "solution", "feature", "capability"],
    "portfolio":    ["portfolio", "work", "project", "case study", "gallery", "showcase"],
    "products":     ["product", "shop", "catalog", "item", "listing", "inventory"],
    "blog":         ["blog", "article", "post", "news", "latest"],
    "testimonials": ["testimonial", "review", "client", "feedback", "rating", "social proof"],
    "contact":      ["contact", "form", "reach", "email", "touch", "message", "get in touch"],
    "pricing":      ["pricing", "plan", "subscription", "cost", "tier", "package", "price"],
    "faq":          ["faq", "question", "answer", "help", "frequently asked"],
    "footer":       ["footer"],
    "header":       ["header", "nav", "navbar", "navigation", "menu"],
    "features":     ["feature", "benefit", "why", "how it works", "capability"],
    "stats":        ["stat", "number", "metric", "achievement", "milestone"],
    "cta":          ["cta", "call to action", "sign up", "get started", "waitlist", "join"],
}

FEATURE_KEYWORDS = {
    "has_auth": ["login", "signup", "auth", "register", "account", "user", "member", "password"],
    "has_db":   ["database", "db", "store", "save", "sqlite", "mysql", "data", "backend"],
}

STACK_KEYWORDS = {
    "ecommerce": ["ecommerce", "e-commerce", "shop", "store", "seller", "meesho", "product", "order"],
    "flask":     ["flask", "python", "backend", "full-stack", "fullstack", "server", "api", "database", "db"],
    "static":    ["html", "css", "js", "javascript", "static", "simple", "basic", "frontend"],
}

THEME_KEYWORDS = {
    "dark":     ["dark", "night", "black", "dark theme", "dark mode"],
    "minimal":  ["minimal", "clean", "simple", "white", "light", "minimalist"],
    "business": ["corporate", "professional", "business", "formal", "enterprise"],
    "nature":   ["green", "nature", "eco", "organic", "environment"],
    "warm":     ["warm", "red", "pink", "vibrant", "bold", "colorful"],
    "ocean":    ["blue", "ocean", "teal", "sea", "water", "cool"],
    "luxury":   ["luxury", "premium", "gold", "elegant", "high-end"],
    "modern":   ["modern", "trendy", "fresh", "new", "contemporary"],
}

COLOR_PATTERNS = [
    (r"#[0-9a-fA-F]{6}", "hex"),
    (r"\b(red|blue|green|purple|pink|orange|yellow|teal|black|white|gray|grey)\b", "name"),
]

COLOR_MAP = {
    "red": "#e53935", "blue": "#1565c0", "green": "#2e7d32",
    "purple": "#6c63ff", "pink": "#e91e63", "orange": "#ff5722",
    "yellow": "#ffc107", "teal": "#00897b", "black": "#212121",
    "white": "#f5f5f5", "gray": "#616161", "grey": "#616161",
}


def parse_prompt(prompt: str) -> dict:
    """
    Parse a natural language prompt and return a structured config dict.
    This config is compatible with generator.build_project().
    """
    text = prompt.lower().strip()

    # ── Detect website type ───────────────────────────────────────────────────
    website_type = _detect_type(text)

    # ── Detect stack ──────────────────────────────────────────────────────────
    project_type = _detect_stack(text, website_type)

    # ── Detect theme ──────────────────────────────────────────────────────────
    theme_name = _detect_theme(text)
    theme = THEMES.get(theme_name, THEMES["modern"])

    # ── Detect colors from prompt ─────────────────────────────────────────────
    primary, secondary = _detect_colors(text, theme)

    # ── Detect font ───────────────────────────────────────────────────────────
    font = _detect_font(text, theme)

    # ── Detect sections ───────────────────────────────────────────────────────
    sections = _detect_sections(text, website_type)

    # ── Detect features ───────────────────────────────────────────────────────
    has_auth = any(k in text for k in FEATURE_KEYWORDS["has_auth"])
    has_db   = any(k in text for k in FEATURE_KEYWORDS["has_db"]) or project_type != "static"

    # ── Extract site name from prompt ─────────────────────────────────────────
    site_name = _extract_site_name(prompt)

    # ── Extract tagline ───────────────────────────────────────────────────────
    tagline = _extract_tagline(prompt, website_type)

    return {
        "site_name":      site_name,
        "tagline":        tagline,
        "website_type":   website_type,
        "project_type":   project_type,
        "primary_color":  primary,
        "secondary_color": secondary,
        "font":           font,
        "sections":       sections,
        "has_auth":       has_auth,
        "has_db":         has_db,
        "theme":          theme_name,
        "prompt":         prompt,
    }


def _detect_type(text: str) -> str:
    scores = {t: 0 for t in TYPE_KEYWORDS}
    for t, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[t] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "business"


def _detect_stack(text: str, website_type: str) -> str:
    if website_type == "ecommerce":
        return "ecommerce"
    # Blog always gets its own CMS generator
    if website_type == "blog":
        return "blog"
    # Portfolio with animation keywords gets advanced generator
    if website_type == "portfolio" and any(k in text for k in ["animation", "animated", "animate", "dark", "creative", "advanced"]):
        return "portfolio_adv"
    # Check for startup signals
    if any(k in text for k in ["startup", "saas", "landing page", "waitlist", "launch", "ai tool"]):
        return "startup"
    scores = {s: 0 for s in STACK_KEYWORDS}
    for s, keywords in STACK_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[s] += 1
    if scores["flask"] > 0 or scores["ecommerce"] > 0:
        return "flask"
    return "static"


def _detect_theme(text: str) -> str:
    for theme, keywords in THEME_KEYWORDS.items():
        if any(k in text for k in keywords):
            return theme
    return "modern"


def _detect_colors(text: str, theme: dict) -> tuple:
    """Extract hex colors or named colors from prompt."""
    # Try hex first
    hexes = re.findall(r"#[0-9a-fA-F]{6}", text)
    if len(hexes) >= 2:
        return hexes[0], hexes[1]
    if len(hexes) == 1:
        return hexes[0], theme["secondary"]

    # Try named colors
    named = []
    for name, hex_val in COLOR_MAP.items():
        if name in text:
            named.append(hex_val)
    if len(named) >= 2:
        return named[0], named[1]
    if len(named) == 1:
        return named[0], theme["secondary"]

    return theme["primary"], theme["secondary"]


def _detect_font(text: str, theme: dict) -> str:
    font_map = {
        "poppins": "Poppins", "inter": "Inter", "roboto": "Roboto",
        "montserrat": "Montserrat", "lato": "Lato", "nunito": "Nunito",
        "raleway": "Raleway",
    }
    for key, val in font_map.items():
        if key in text:
            return val
    return theme.get("font", "Poppins")


def _detect_sections(text: str, website_type: str) -> list:
    """Detect which sections to include, with type-based defaults."""
    # Always include these
    base = ["header", "hero", "footer"]

    # Type-specific defaults
    type_defaults = {
        "portfolio":  ["about", "portfolio", "contact"],
        "business":   ["about", "services", "testimonials", "contact"],
        "ecommerce":  ["products", "contact"],
        "blog":       ["blog", "about", "contact"],
    }
    sections = base + type_defaults.get(website_type, ["about", "contact"])

    # Startup/SaaS gets richer defaults
    if any(k in text for k in ["startup", "saas", "landing page", "ai tool", "launch", "waitlist"]):
        for s in ["services", "pricing", "testimonials", "faq", "contact"]:
            if s not in sections:
                sections.append(s)

    # Add any explicitly mentioned sections
    for section, keywords in SECTION_KEYWORDS.items():
        if section not in sections:
            if any(k in text for k in keywords):
                sections.append(section)

    # Deduplicate while preserving order
    seen = set()
    result = []
    for s in sections:
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result


def _extract_site_name(prompt: str) -> str:
    """Try to extract a site/company name from the prompt."""
    # Patterns like "called X", "named X", "for X", "website for X"
    patterns = [
        r"(?:called|named|for|brand)\s+['\"]?([A-Z][a-zA-Z0-9\s]{1,30})['\"]?",
        r"([A-Z][a-zA-Z]{2,}(?:\s[A-Z][a-zA-Z]{2,})?)\s+(?:website|site|app|platform|store|shop|blog)",
    ]
    for pat in patterns:
        m = re.search(pat, prompt)
        if m:
            name = m.group(1).strip()
            if len(name) > 2:
                return name
    return "My Website"


def _extract_tagline(prompt: str, website_type: str) -> str:
    """Generate a contextual tagline based on website type."""
    defaults = {
        "portfolio":  "Showcasing my work and passion",
        "business":   "Professional solutions for modern challenges",
        "ecommerce":  "Discover amazing products at great prices",
        "blog":       "Thoughts, ideas, and stories worth sharing",
    }
    return defaults.get(website_type, "Welcome to our website")


def get_theme(name: str) -> dict:
    """Return a theme config by name."""
    return THEMES.get(name, THEMES["modern"])


def list_themes() -> dict:
    """Return all available themes."""
    return THEMES
