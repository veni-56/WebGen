"""
ai_engine/chat.py — Conversational AI Chat Builder
Users describe their website through a chat interface.
AI asks clarifying questions and builds the config progressively.
"""
import json
import re
from utils.logger import get_logger

logger = get_logger("ai_engine.chat")

# ── Conversation flow states ──────────────────────────────────────────────────
STATES = {
    "start":       "Collecting initial description",
    "type":        "Confirming website type",
    "features":    "Asking about features",
    "design":      "Collecting design preferences",
    "complete":    "Config complete — ready to generate",
}

# ── Clarifying questions per website type ─────────────────────────────────────
QUESTIONS = {
    "ecommerce": [
        {"key": "has_seller_dashboard", "q": "Do you need a seller dashboard to manage products?", "type": "bool"},
        {"key": "has_categories",       "q": "Should products be organized by categories?",         "type": "bool"},
        {"key": "has_cart",             "q": "Do you want a shopping cart system?",                 "type": "bool"},
    ],
    "portfolio": [
        {"key": "has_blog",      "q": "Would you like a blog section?",                    "type": "bool"},
        {"key": "has_animation", "q": "Do you want animated effects (typewriter, scroll)?", "type": "bool"},
        {"key": "dark_theme",    "q": "Prefer a dark theme or light theme?",               "type": "choice", "choices": ["dark", "light"]},
    ],
    "blog": [
        {"key": "has_comments",  "q": "Should readers be able to leave comments?",         "type": "bool"},
        {"key": "has_categories","q": "Do you want post categories?",                      "type": "bool"},
        {"key": "has_newsletter","q": "Would you like a newsletter signup?",               "type": "bool"},
    ],
    "business": [
        {"key": "has_pricing",   "q": "Do you need a pricing section?",                    "type": "bool"},
        {"key": "has_booking",   "q": "Would you like an appointment/booking form?",       "type": "bool"},
        {"key": "has_team",      "q": "Should there be a team/about section?",             "type": "bool"},
    ],
    "startup": [
        {"key": "has_waitlist",  "q": "Do you want a waitlist/email capture form?",        "type": "bool"},
        {"key": "has_pricing",   "q": "Should there be a pricing section?",                "type": "bool"},
        {"key": "has_demo",      "q": "Would you like a demo/video section?",              "type": "bool"},
    ],
}

# ── Intent detection from chat messages ───────────────────────────────────────
TYPE_SIGNALS = {
    "ecommerce":  ["shop", "store", "sell", "product", "ecommerce", "meesho", "shopify", "buy", "cart"],
    "portfolio":  ["portfolio", "showcase", "my work", "designer", "developer", "freelance", "cv"],
    "blog":       ["blog", "write", "articles", "posts", "cms", "content", "news"],
    "business":   ["business", "company", "agency", "service", "corporate", "startup"],
    "startup":    ["startup", "launch", "saas", "landing", "waitlist", "product launch"],
}

FEATURE_SIGNALS = {
    "has_auth":    ["login", "signup", "register", "account", "user", "member"],
    "has_db":      ["database", "store data", "save", "backend", "python", "flask"],
    "has_pricing": ["pricing", "plans", "subscription", "cost", "tiers"],
    "has_booking": ["booking", "appointment", "schedule", "calendar", "reserve"],
    "has_blog":    ["blog", "articles", "posts", "news"],
    "dark_theme":  ["dark", "dark theme", "dark mode", "night"],
}


class ChatBuilder:
    """
    Manages a conversational website building session.
    Each user has a session_state dict stored in Flask session.
    """

    def process_message(self, message: str, state: dict) -> dict:
        """
        Process a user message and return the next response.
        state: current conversation state (stored in session)
        Returns: {"reply": str, "state": dict, "ready": bool, "config": dict|None}
        """
        text = message.lower().strip()

        # Initialize state if new conversation
        if not state:
            state = {"step": "start", "config": {}, "questions_asked": [], "answers": {}}

        step = state.get("step", "start")

        if step == "start":
            return self._handle_start(message, text, state)
        elif step == "clarify":
            return self._handle_clarify(message, text, state)
        elif step == "design":
            return self._handle_design(message, text, state)
        else:
            return self._handle_start(message, text, state)

    def _handle_start(self, message: str, text: str, state: dict) -> dict:
        """Handle initial message — detect type and start clarifying."""
        config = state.get("config", {})

        # Detect website type
        website_type = "business"
        for wtype, signals in TYPE_SIGNALS.items():
            if any(s in text for s in signals):
                website_type = wtype
                break

        # Detect features from initial message
        for feature, signals in FEATURE_SIGNALS.items():
            if any(s in text for s in signals):
                config[feature] = True

        # Detect dark theme
        if "dark" in text:
            config["primary_color"] = "#bb86fc"
            config["secondary_color"] = "#03dac6"

        config["website_type"] = website_type
        config["prompt"] = message

        # Get clarifying questions for this type
        questions = QUESTIONS.get(website_type, QUESTIONS["business"])
        remaining = [q for q in questions if q["key"] not in state.get("answers", {})]

        if remaining:
            next_q = remaining[0]
            state["step"] = "clarify"
            state["config"] = config
            state["current_question"] = next_q
            state["remaining_questions"] = remaining[1:]

            reply = self._format_question(website_type, next_q, is_first=True)
            return {"reply": reply, "state": state, "ready": False, "config": None}

        # No questions needed — go to design
        return self._ask_design(state, config)

    def _handle_clarify(self, message: str, text: str, state: dict) -> dict:
        """Handle answer to a clarifying question."""
        current_q = state.get("current_question", {})
        answers   = state.get("answers", {})
        config    = state.get("config", {})

        # Parse answer
        if current_q.get("type") == "bool":
            answer = any(w in text for w in ["yes", "yeah", "sure", "ok", "yep", "please", "want", "need"])
            answers[current_q["key"]] = answer
            if answer:
                config[current_q["key"]] = True
        elif current_q.get("type") == "choice":
            choices = current_q.get("choices", [])
            for choice in choices:
                if choice in text:
                    answers[current_q["key"]] = choice
                    config[current_q["key"]] = choice
                    break

        state["answers"] = answers
        state["config"]  = config

        # Next question?
        remaining = state.get("remaining_questions", [])
        if remaining:
            next_q = remaining[0]
            state["current_question"] = next_q
            state["remaining_questions"] = remaining[1:]
            reply = self._format_question(config.get("website_type", "business"), next_q)
            return {"reply": reply, "state": state, "ready": False, "config": None}

        # All questions answered — ask about design
        return self._ask_design(state, config)

    def _ask_design(self, state: dict, config: dict) -> dict:
        """Ask about design preferences."""
        state["step"] = "design"
        state["config"] = config
        wtype = config.get("website_type", "business")

        reply = (
            f"Great! I have everything I need for your {wtype} website. "
            f"One last thing — any color preference? "
            f"(e.g. 'blue and white', 'dark theme', 'green') "
            f"Or just say 'surprise me' and I'll choose the best colors for your industry! 🎨"
        )
        return {"reply": reply, "state": state, "ready": False, "config": None}

    def _handle_design(self, message: str, text: str, state: dict) -> dict:
        """Handle design preferences and finalize config."""
        config = state.get("config", {})

        # Apply design choices
        if "surprise" in text or "auto" in text or "you choose" in text:
            from ai_engine.designer import apply_design_to_config
            config = apply_design_to_config(config, config.get("prompt", ""))
        else:
            # Parse color mentions
            color_map = {
                "blue": "#1565c0", "red": "#e53935", "green": "#2e7d32",
                "purple": "#6c63ff", "pink": "#e91e63", "orange": "#ff5722",
                "teal": "#00897b", "dark": "#bb86fc", "black": "#212121",
            }
            for color, hex_val in color_map.items():
                if color in text:
                    config["primary_color"] = hex_val
                    break

        # Finalize config
        config.setdefault("primary_color",   "#6c63ff")
        config.setdefault("secondary_color", "#f50057")
        config.setdefault("font",            "Poppins")
        config.setdefault("sections",        self._default_sections(config))
        config.setdefault("has_auth",        False)
        config.setdefault("has_db",          config.get("project_type", "static") != "static")
        config["project_type"] = self._resolve_project_type(config)

        state["step"] = "complete"
        state["config"] = config

        wtype  = config.get("website_type", "business")
        ptype  = config.get("project_type", "static")
        color  = config.get("primary_color", "#6c63ff")
        features = []
        if config.get("has_auth"):    features.append("login/signup")
        if config.get("has_pricing"): features.append("pricing section")
        if config.get("has_blog"):    features.append("blog")
        if config.get("has_booking"): features.append("booking form")

        feat_str = f" with {', '.join(features)}" if features else ""
        reply = (
            f"✅ Perfect! I'm ready to build your **{wtype} website**{feat_str}.\n\n"
            f"🎨 Color: `{color}` | Stack: `{ptype}` | Font: `{config['font']}`\n\n"
            f"Click **Generate** to create your complete website! 🚀"
        )
        return {"reply": reply, "state": state, "ready": True, "config": config}

    def _format_question(self, wtype: str, question: dict, is_first: bool = False) -> str:
        prefix = ""
        if is_first:
            type_labels = {
                "ecommerce": "e-commerce store", "portfolio": "portfolio",
                "blog": "blog", "business": "business site", "startup": "startup landing page",
            }
            label = type_labels.get(wtype, "website")
            prefix = f"Got it! I'll build you a {label}. Let me ask a few quick questions.\n\n"

        q = question["q"]
        if question["type"] == "bool":
            return f"{prefix}👉 {q} (yes/no)"
        elif question["type"] == "choice":
            choices = " / ".join(question.get("choices", []))
            return f"{prefix}👉 {q} ({choices})"
        return f"{prefix}👉 {q}"

    def _default_sections(self, config: dict) -> list:
        wtype = config.get("website_type", "business")
        base = {
            "ecommerce": ["header", "hero", "products", "contact", "footer"],
            "portfolio":  ["header", "hero", "about", "portfolio", "contact", "footer"],
            "blog":       ["header", "hero", "blog", "about", "contact", "footer"],
            "business":   ["header", "hero", "about", "services", "contact", "footer"],
            "startup":    ["header", "hero", "features", "pricing", "testimonials", "faq", "footer"],
        }
        sections = list(base.get(wtype, base["business"]))
        if config.get("has_pricing") and "pricing" not in sections:
            sections.insert(-1, "pricing")
        if config.get("has_blog") and "blog" not in sections:
            sections.insert(-1, "blog")
        return sections

    def _resolve_project_type(self, config: dict) -> str:
        wtype = config.get("website_type", "business")
        if wtype == "ecommerce":
            return "ecommerce"
        if wtype == "startup":
            return "startup"
        if wtype == "blog":
            return "blog"
        if config.get("has_auth") or config.get("has_db"):
            return "flask"
        if config.get("dark_theme") == "dark" and wtype == "portfolio":
            return "portfolio_adv"
        return "static"
