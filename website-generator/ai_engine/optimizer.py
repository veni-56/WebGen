"""
ai_engine/optimizer.py — Prompt Optimizer
Transforms raw user prompts into structured, optimized generation configs.
Works in two modes:
  1. Keyword mode (default, no API cost)
  2. OpenAI mode (when OPENAI_API_KEY is set)
"""
import re
import os
import json
from utils.logger import get_logger

logger = get_logger("ai_engine.optimizer")

# ── Verbose phrase compressions ───────────────────────────────────────────────
_COMPRESSIONS = [
    (r"i want (to |you to )?",                    ""),
    (r"please (create|make|build|generate) (me |a |an )?", "create "),
    (r"can you (create|make|build|generate) (me |a |an )?", "create "),
    (r"i need (a |an )?",                          "create "),
    (r"help me (create|make|build) (a |an )?",     "create "),
    (r"i would like (a |an )?",                    "create "),
    (r"could you (make|build|create) (me |a |an )?", "create "),
    (r"\bplease\b",                                ""),
    (r"\bkindly\b",                                ""),
    (r"\bthanks?\b",                               ""),
]

# ── Intent enrichment rules ───────────────────────────────────────────────────
_ENRICHMENTS = {
    "meesho":    "ecommerce seller dashboard with product management and orders",
    "shopify":   "ecommerce platform with product catalog and seller dashboard",
    "wordpress": "blog CMS with admin panel and post management",
    "airbnb":    "booking platform with listing management",
    "notion":    "productivity workspace with notes and tasks",
    "netflix":   "streaming platform with content catalog",
    "twitter":   "social media platform with feed and posts",
    "amazon":    "ecommerce marketplace with product listings and orders",
    "flipkart":  "ecommerce marketplace with seller dashboard",
}

# ── System prompt for OpenAI mode ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a website configuration extractor. 
Given a user's website description, extract a structured JSON config.

Return ONLY valid JSON with these fields:
{
  "site_name": "string",
  "tagline": "string", 
  "website_type": "portfolio|business|ecommerce|blog",
  "project_type": "static|flask|ecommerce|startup|blog|portfolio_adv",
  "primary_color": "#hexcode",
  "secondary_color": "#hexcode",
  "font": "Poppins|Inter|Roboto|Montserrat|Lato|Nunito|Raleway",
  "sections": ["header","hero","about","services","contact","footer"],
  "has_auth": true|false,
  "has_db": true|false,
  "theme": "modern|minimal|business|nature|dark|warm|ocean|luxury"
}

Rules:
- website_type must be one of the 4 options
- project_type: use "ecommerce" for shops, "startup" for landing pages, "blog" for CMS, "portfolio_adv" for animated portfolios, "flask" for backend apps, "static" for simple sites
- sections: only include relevant ones
- has_auth: true if login/signup mentioned
- has_db: true if backend/database mentioned or project_type is not static"""


class PromptOptimizer:
    """
    Optimizes and enriches user prompts before generation.
    """

    def __init__(self):
        self._openai_available = bool(os.environ.get("OPENAI_API_KEY"))
        if self._openai_available:
            logger.info("PromptOptimizer: OpenAI mode enabled")
        else:
            logger.info("PromptOptimizer: Keyword mode (no OpenAI key)")

    def optimize(self, prompt: str) -> str:
        """
        Clean and compress a prompt for efficient processing.
        Returns the optimized prompt string.
        """
        text = prompt.lower().strip()

        # Apply compressions
        for pattern, replacement in _COMPRESSIONS:
            text = re.sub(pattern, replacement, text)

        # Expand platform references
        for platform, expansion in _ENRICHMENTS.items():
            if platform in text:
                text = text.replace(platform, expansion)
                logger.debug("Expanded platform reference: %s", platform)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        logger.debug("Optimized prompt: %s → %s", prompt[:50], text[:50])
        return text

    def extract_config(self, prompt: str) -> dict:
        """
        Extract a structured config from a prompt.
        Uses OpenAI if available, falls back to keyword parsing.
        """
        optimized = self.optimize(prompt)

        if self._openai_available:
            try:
                config = self._openai_extract(optimized)
                config["prompt"] = prompt
                logger.info("Config extracted via OpenAI for: %s", prompt[:60])
                return config
            except Exception as e:
                logger.warning("OpenAI extraction failed, falling back to NLP: %s", e)

        # Fallback to keyword-based NLP
        from nlp import parse_prompt
        config = parse_prompt(prompt)
        logger.debug("Config extracted via NLP keywords")
        return config

    def _openai_extract(self, prompt: str) -> dict:
        """Call OpenAI API to extract structured config."""
        import openai
        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        config = json.loads(raw)

        # Validate and fill defaults
        config.setdefault("site_name",      "My Website")
        config.setdefault("tagline",        "")
        config.setdefault("website_type",   "business")
        config.setdefault("project_type",   "static")
        config.setdefault("primary_color",  "#6c63ff")
        config.setdefault("secondary_color","#f50057")
        config.setdefault("font",           "Poppins")
        config.setdefault("sections",       ["header","hero","about","contact","footer"])
        config.setdefault("has_auth",       False)
        config.setdefault("has_db",         False)
        config.setdefault("theme",          "modern")

        return config

    def estimate_complexity(self, prompt: str) -> str:
        """Estimate generation complexity: simple | medium | advanced"""
        text = prompt.lower()
        advanced_signals = ["meesho", "shopify", "dashboard", "admin", "analytics",
                            "cms", "saas", "platform", "marketplace", "animation"]
        medium_signals   = ["login", "auth", "database", "backend", "flask",
                            "portfolio", "pricing", "contact form"]
        if any(s in text for s in advanced_signals):
            return "advanced"
        if any(s in text for s in medium_signals):
            return "medium"
        return "simple"
