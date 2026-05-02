"""
ai_engine/memory.py — User Memory & Personalization Engine
Remembers user preferences, past projects, and industry to make
AI suggestions smarter over time.
"""
import json
from utils.logger import get_logger
import db as database

logger = get_logger("ai_engine.memory")


def save_preference(user_id: int, key: str, value) -> None:
    """Save a user preference to the database."""
    conn = database.get_db()
    existing = conn.execute(
        "SELECT * FROM user_settings WHERE user_id=?", (user_id,)
    ).fetchone()

    if existing:
        try:
            existing_dict = dict(existing)
            prefs = json.loads(existing_dict.get("preferences", "{}") or "{}")
        except Exception:
            prefs = {}
        prefs[key] = value
        conn.execute(
            "UPDATE user_settings SET preferences=? WHERE user_id=?",
            (json.dumps(prefs), user_id)
        )
    else:
        conn.execute(
            "INSERT INTO user_settings (user_id, preferences) VALUES (?,?)",
            (user_id, json.dumps({key: value}))
        )
    conn.commit()
    conn.close()


def get_preferences(user_id: int) -> dict:
    """Get all stored preferences for a user."""
    conn = database.get_db()
    row = conn.execute(
        "SELECT * FROM user_settings WHERE user_id=?", (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {}
    try:
        row_dict = dict(row)
        return json.loads(row_dict.get("preferences", "{}") or "{}")
    except Exception:
        return {}


def learn_from_generation(user_id: int, config: dict) -> None:
    """
    Learn from a generation event — update user preferences.
    Called after every successful generation.
    """
    prefs = get_preferences(user_id)

    # Track preferred colors
    primary = config.get("primary_color", "")
    if primary:
        color_history = prefs.get("color_history", [])
        if primary not in color_history:
            color_history.insert(0, primary)
        prefs["color_history"] = color_history[:5]  # keep last 5

    # Track preferred font
    font = config.get("font", "")
    if font:
        font_counts = prefs.get("font_counts", {})
        font_counts[font] = font_counts.get(font, 0) + 1
        prefs["font_counts"] = font_counts
        # Set preferred font to most used
        prefs["preferred_font"] = max(font_counts, key=font_counts.get)

    # Track preferred project types
    ptype = config.get("project_type", "")
    if ptype:
        type_counts = prefs.get("type_counts", {})
        type_counts[ptype] = type_counts.get(ptype, 0) + 1
        prefs["type_counts"] = type_counts

    # Track industry
    industry = config.get("_industry", "")
    if industry:
        industry_history = prefs.get("industry_history", [])
        if industry not in industry_history:
            industry_history.insert(0, industry)
        prefs["industry_history"] = industry_history[:3]
        prefs["primary_industry"] = industry_history[0]

    # Save updated preferences
    conn = database.get_db()
    existing = conn.execute(
        "SELECT user_id FROM user_settings WHERE user_id=?", (user_id,)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE user_settings SET preferences=? WHERE user_id=?",
            (json.dumps(prefs), user_id)
        )
    else:
        conn.execute(
            "INSERT INTO user_settings (user_id, preferences) VALUES (?,?)",
            (user_id, json.dumps(prefs))
        )
    conn.commit()
    conn.close()


def get_personalized_defaults(user_id: int) -> dict:
    """
    Return personalized defaults for a new generation based on user history.
    """
    prefs = get_preferences(user_id)
    defaults = {}

    if prefs.get("preferred_font"):
        defaults["font"] = prefs["preferred_font"]

    if prefs.get("color_history"):
        defaults["suggested_colors"] = prefs["color_history"][:3]

    if prefs.get("primary_industry"):
        defaults["suggested_industry"] = prefs["primary_industry"]

    if prefs.get("type_counts"):
        defaults["preferred_type"] = max(
            prefs["type_counts"], key=prefs["type_counts"].get
        )

    return defaults


def get_suggestions(user_id: int, projects: list) -> list:
    """
    Generate AI suggestions based on user's project history.
    Returns list of actionable suggestion strings.
    """
    suggestions = []
    prefs = get_preferences(user_id)

    if not projects:
        suggestions.append("🚀 Create your first project — try the AI Generator!")
        return suggestions

    # Analyze project types
    types = [p["project_type"] for p in projects]
    if types.count("static") > 2:
        suggestions.append("💡 You've built several static sites — try a Flask backend for more features!")

    # Check for missing SEO
    suggestions.append("📈 Add SEO optimization to your projects for better search rankings")

    # Check for ecommerce opportunity
    if "ecommerce" not in types and len(projects) >= 2:
        suggestions.append("🛍️ Try building an e-commerce site — it's one of our most popular project types")

    # Personalized based on industry
    industry = prefs.get("primary_industry", "")
    if industry == "fintech":
        suggestions.append("🔒 Consider adding a security badge section to build user trust")
    elif industry == "ecommerce":
        suggestions.append("⭐ Add customer testimonials to increase conversion rates by up to 34%")
    elif industry == "saas":
        suggestions.append("📊 A pricing comparison table can increase plan upgrades by 20%")

    return suggestions[:4]
    logger.debug("Learned from generation for user %s", user_id)
