"""
ai_engine/designer.py — Smart AI UX Designer
Thinks like a designer: color psychology, font pairing, layout optimization,
CTA placement, UX best practices — all driven by industry/intent signals.
"""
import re
from utils.logger import get_logger

logger = get_logger("ai_engine.designer")

# ── Color psychology by industry ──────────────────────────────────────────────
INDUSTRY_COLORS = {
    # Finance / Fintech — trust, stability, professionalism
    "fintech":    {"primary": "#1565c0", "secondary": "#00897b", "accent": "#ffc107",
                   "rationale": "Blue builds trust; teal signals growth; gold = premium"},
    "finance":    {"primary": "#0d47a1", "secondary": "#1b5e20", "accent": "#f9a825",
                   "rationale": "Deep blue = authority; green = money/growth"},
    "banking":    {"primary": "#1a237e", "secondary": "#004d40", "accent": "#e65100",
                   "rationale": "Navy = stability; dark teal = security"},

    # Health / Medical — clean, calm, trustworthy
    "health":     {"primary": "#00695c", "secondary": "#1565c0", "accent": "#e8f5e9",
                   "rationale": "Teal/green = healing; blue = calm and clinical"},
    "medical":    {"primary": "#0277bd", "secondary": "#00695c", "accent": "#ffffff",
                   "rationale": "Medical blue = trust; white = cleanliness"},
    "wellness":   {"primary": "#2e7d32", "secondary": "#00838f", "accent": "#f3e5f5",
                   "rationale": "Green = nature/health; teal = calm"},

    # Tech / SaaS — modern, innovative, bold
    "tech":       {"primary": "#6c63ff", "secondary": "#f50057", "accent": "#00e5ff",
                   "rationale": "Purple = innovation; pink = energy; cyan = digital"},
    "saas":       {"primary": "#5c6bc0", "secondary": "#26c6da", "accent": "#ff7043",
                   "rationale": "Indigo = professional; cyan = modern SaaS"},
    "startup":    {"primary": "#7c4dff", "secondary": "#00bcd4", "accent": "#ff6e40",
                   "rationale": "Vibrant purple = disruption; cyan = fresh"},
    "ai":         {"primary": "#4a148c", "secondary": "#00bfa5", "accent": "#e040fb",
                   "rationale": "Deep purple = intelligence; teal = precision"},

    # E-commerce — action, urgency, trust
    "ecommerce":  {"primary": "#e91e63", "secondary": "#ff5722", "accent": "#ffc107",
                   "rationale": "Pink/red = action/urgency; orange = CTA; yellow = deals"},
    "fashion":    {"primary": "#212121", "secondary": "#f50057", "accent": "#ffd740",
                   "rationale": "Black = luxury/fashion; pink = feminine energy"},
    "food":       {"primary": "#e53935", "secondary": "#ff8f00", "accent": "#43a047",
                   "rationale": "Red stimulates appetite; orange = warmth; green = fresh"},

    # Education — approachable, trustworthy, energetic
    "education":  {"primary": "#1976d2", "secondary": "#f57c00", "accent": "#43a047",
                   "rationale": "Blue = knowledge; orange = enthusiasm; green = growth"},
    "edtech":     {"primary": "#3949ab", "secondary": "#00acc1", "accent": "#ffb300",
                   "rationale": "Indigo = academic; cyan = digital learning"},

    # Creative / Portfolio — expressive, unique
    "creative":   {"primary": "#6c63ff", "secondary": "#f50057", "accent": "#00e5ff",
                   "rationale": "Purple = creativity; pink = passion; cyan = digital art"},
    "design":     {"primary": "#212121", "secondary": "#6c63ff", "accent": "#ff6e40",
                   "rationale": "Dark = sophistication; purple = design thinking"},
    "photography":{"primary": "#212121", "secondary": "#bdbdbd", "accent": "#ff6e40",
                   "rationale": "Dark/mono = photography aesthetic; orange = warmth"},

    # Real estate — premium, trustworthy
    "realestate": {"primary": "#1a237e", "secondary": "#b8860b", "accent": "#f5f5f5",
                   "rationale": "Navy = trust; gold = premium/luxury"},
    "property":   {"primary": "#37474f", "secondary": "#b8860b", "accent": "#eceff1",
                   "rationale": "Slate = professional; gold = value"},

    # Fitness / Sports — energy, power
    "fitness":    {"primary": "#d32f2f", "secondary": "#212121", "accent": "#ffeb3b",
                   "rationale": "Red = energy/power; black = strength; yellow = motivation"},
    "gym":        {"primary": "#b71c1c", "secondary": "#212121", "accent": "#ff6f00",
                   "rationale": "Dark red = intensity; black = power; orange = fire"},
    "sports":     {"primary": "#1565c0", "secondary": "#e53935", "accent": "#ffd600",
                   "rationale": "Blue = team spirit; red = competition; yellow = victory"},

    # Default
    "default":    {"primary": "#6c63ff", "secondary": "#f50057", "accent": "#00e5ff",
                   "rationale": "Modern purple/pink — versatile and contemporary"},
}

# ── Font pairing system ───────────────────────────────────────────────────────
FONT_PAIRS = {
    "fintech":    {"heading": "Inter",       "body": "Inter",      "mono": "JetBrains Mono"},
    "finance":    {"heading": "Playfair Display", "body": "Inter", "mono": "Courier New"},
    "health":     {"heading": "Nunito",      "body": "Nunito",     "mono": "Courier New"},
    "medical":    {"heading": "Roboto",      "body": "Roboto",     "mono": "Courier New"},
    "tech":       {"heading": "Poppins",     "body": "Inter",      "mono": "JetBrains Mono"},
    "saas":       {"heading": "Inter",       "body": "Inter",      "mono": "Fira Code"},
    "startup":    {"heading": "Poppins",     "body": "Poppins",    "mono": "Courier New"},
    "ai":         {"heading": "Inter",       "body": "Inter",      "mono": "JetBrains Mono"},
    "ecommerce":  {"heading": "Poppins",     "body": "Lato",       "mono": "Courier New"},
    "fashion":    {"heading": "Raleway",     "body": "Lato",       "mono": "Courier New"},
    "food":       {"heading": "Nunito",      "body": "Nunito",     "mono": "Courier New"},
    "education":  {"heading": "Nunito",      "body": "Roboto",     "mono": "Courier New"},
    "creative":   {"heading": "Montserrat",  "body": "Lato",       "mono": "Courier New"},
    "design":     {"heading": "Raleway",     "body": "Inter",      "mono": "Courier New"},
    "fitness":    {"heading": "Montserrat",  "body": "Roboto",     "mono": "Courier New"},
    "realestate": {"heading": "Raleway",     "body": "Lato",       "mono": "Courier New"},
    "default":    {"heading": "Poppins",     "body": "Inter",      "mono": "Courier New"},
}

# ── Layout optimization by type ───────────────────────────────────────────────
LAYOUT_DECISIONS = {
    "fintech": {
        "hero_style":    "split-screen",
        "cta_position":  "above-fold",
        "nav_style":     "sticky-transparent",
        "trust_signals": ["security badges", "client logos", "stats counter"],
        "sections_order":["header","hero","stats","features","testimonials","pricing","contact","footer"],
        "ux_notes":      ["Use data visualizations", "Show security certifications",
                          "Add social proof early", "Keep forms minimal"],
    },
    "ecommerce": {
        "hero_style":    "full-width-banner",
        "cta_position":  "product-cards",
        "nav_style":     "sticky-with-cart",
        "trust_signals": ["reviews", "secure checkout", "free shipping badge"],
        "sections_order":["header","hero","products","testimonials","contact","footer"],
        "ux_notes":      ["Show prices prominently", "Add urgency (limited stock)",
                          "Use high-quality product images", "Streamline checkout"],
    },
    "saas": {
        "hero_style":    "centered-gradient",
        "cta_position":  "hero-primary",
        "nav_style":     "sticky-with-cta",
        "trust_signals": ["user count", "company logos", "G2/Capterra badges"],
        "sections_order":["header","hero","features","how-it-works","pricing","testimonials","faq","footer"],
        "ux_notes":      ["Lead with value proposition", "Show product screenshot",
                          "Use comparison table", "Add free trial CTA"],
    },
    "portfolio": {
        "hero_style":    "full-screen-dark",
        "cta_position":  "hero-secondary",
        "nav_style":     "minimal-overlay",
        "trust_signals": ["client logos", "project count", "years experience"],
        "sections_order":["header","hero","about","skills","portfolio","testimonials","contact","footer"],
        "ux_notes":      ["Let work speak first", "Use large imagery",
                          "Keep navigation minimal", "Add personality"],
    },
    "health": {
        "hero_style":    "calm-centered",
        "cta_position":  "above-fold",
        "nav_style":     "clean-white",
        "trust_signals": ["certifications", "doctor photos", "patient count"],
        "sections_order":["header","hero","services","about","testimonials","contact","footer"],
        "ux_notes":      ["Use calming imagery", "Show credentials prominently",
                          "Make contact easy", "Use accessible colors"],
    },
    "default": {
        "hero_style":    "centered",
        "cta_position":  "hero-primary",
        "nav_style":     "sticky",
        "trust_signals": ["testimonials", "stats"],
        "sections_order":["header","hero","about","services","contact","footer"],
        "ux_notes":      ["Clear value proposition", "Single primary CTA"],
    },
}

# ── Industry detection ────────────────────────────────────────────────────────
INDUSTRY_KEYWORDS = {
    "fintech":    ["fintech", "finance app", "payment", "crypto", "blockchain", "trading", "investment app"],
    "finance":    ["finance", "financial", "accounting", "tax", "insurance", "wealth"],
    "banking":    ["bank", "banking", "loan", "mortgage", "credit"],
    "health":     ["health", "wellness", "clinic", "hospital", "doctor", "medical", "therapy"],
    "medical":    ["medical", "healthcare", "pharma", "dental", "surgery"],
    "tech":       ["tech", "software", "app", "platform", "developer", "coding"],
    "saas":       ["saas", "software as a service", "subscription", "dashboard", "tool"],
    "startup":    ["startup", "launch", "mvp", "product launch", "waitlist"],
    "ai":         ["ai", "artificial intelligence", "machine learning", "chatbot", "automation"],
    "ecommerce":  ["ecommerce", "shop", "store", "sell", "product", "meesho", "shopify"],
    "fashion":    ["fashion", "clothing", "apparel", "boutique", "style"],
    "food":       ["food", "restaurant", "cafe", "recipe", "delivery", "catering"],
    "education":  ["education", "school", "course", "learning", "tutorial", "training"],
    "edtech":     ["edtech", "online learning", "lms", "e-learning"],
    "creative":   ["creative", "artist", "designer", "portfolio", "agency"],
    "design":     ["design", "ui/ux", "graphic", "branding", "visual"],
    "photography":["photography", "photographer", "photo", "studio"],
    "realestate": ["real estate", "property", "realty", "housing", "apartment"],
    "fitness":    ["fitness", "workout", "gym", "personal trainer", "yoga"],
    "gym":        ["gym", "bodybuilding", "crossfit", "weight"],
    "sports":     ["sports", "team", "athlete", "coaching"],
}


def detect_industry(prompt: str) -> str:
    """Detect industry from prompt text."""
    text = prompt.lower()
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        if any(k in text for k in keywords):
            logger.debug("Detected industry: %s", industry)
            return industry
    return "default"


def get_design_decision(prompt: str, website_type: str = "business") -> dict:
    """
    Main entry point — returns complete design decisions for a prompt.
    Includes colors, fonts, layout, UX notes, and rationale.
    """
    industry = detect_industry(prompt)

    colors  = INDUSTRY_COLORS.get(industry, INDUSTRY_COLORS["default"])
    fonts   = FONT_PAIRS.get(industry, FONT_PAIRS["default"])
    layout  = LAYOUT_DECISIONS.get(industry, LAYOUT_DECISIONS["default"])

    decision = {
        "industry":       industry,
        "colors":         colors,
        "fonts":          fonts,
        "layout":         layout,
        "primary_color":  colors["primary"],
        "secondary_color":colors["secondary"],
        "accent_color":   colors["accent"],
        "font":           fonts["heading"],
        "color_rationale":colors["rationale"],
        "ux_notes":       layout["ux_notes"],
        "sections_order": layout["sections_order"],
        "trust_signals":  layout["trust_signals"],
        "hero_style":     layout["hero_style"],
        "cta_position":   layout["cta_position"],
    }

    logger.info("Design decision for '%s': industry=%s, primary=%s",
                prompt[:50], industry, colors["primary"])
    return decision


def apply_design_to_config(config: dict, prompt: str) -> dict:
    """
    Enrich a generation config with smart design decisions.
    Only overrides colors/font if user hasn't explicitly specified them.
    """
    decision = get_design_decision(prompt, config.get("website_type", "business"))

    # Only apply if user didn't specify custom colors
    if config.get("primary_color") in ("#6c63ff", None, ""):
        config["primary_color"]   = decision["primary_color"]
        config["secondary_color"] = decision["secondary_color"]
        config["font"]            = decision["font"]

    # Always add design metadata
    config["_design"] = decision
    config["_industry"] = decision["industry"]

    return config
