"""
cache.py — AI Cost Optimization Engine
- Prompt caching (hash-based)
- Template reuse detection
- Minor-edit detection (avoid full regeneration)
- Smart prompt normalization
"""
import hashlib
import json
import re
import db as database


# ── Prompt normalization ──────────────────────────────────────────────────────

def normalize_prompt(prompt: str) -> str:
    """
    Normalize a prompt for cache key generation.
    Strips extra whitespace, lowercases, removes punctuation noise.
    """
    text = prompt.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[!?.]+$", "", text)
    return text


def prompt_hash(prompt: str) -> str:
    """Generate a stable hash for a normalized prompt."""
    normalized = normalize_prompt(prompt)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def config_hash(config: dict) -> str:
    """Generate a hash for a config dict (for editor change detection)."""
    # Only hash the fields that affect code generation
    key_fields = {
        k: config.get(k) for k in [
            "project_type", "website_type", "primary_color", "secondary_color",
            "font", "sections", "has_auth", "has_db", "site_name"
        ]
    }
    return hashlib.md5(json.dumps(key_fields, sort_keys=True).encode()).hexdigest()[:12]


# ── Cache operations ──────────────────────────────────────────────────────────

def get_cached(prompt: str) -> dict | None:
    """
    Try to get a cached generation result for a prompt.
    Returns the cached result dict or None.
    """
    h   = prompt_hash(prompt)
    row = database.get_cached_prompt(h)
    if row:
        try:
            return json.loads(row["result_json"])
        except Exception:
            return None
    return None


def save_to_cache(prompt: str, config: dict, result: dict) -> None:
    """Save a generation result to cache."""
    h = prompt_hash(prompt)
    database.save_prompt_cache(
        prompt_hash=h,
        config_json=json.dumps(config),
        result_json=json.dumps(result, default=str),
    )


# ── Minor edit detection ──────────────────────────────────────────────────────

# Fields that are "cosmetic" — changing them doesn't require full regeneration
COSMETIC_FIELDS = {"primary_color", "secondary_color", "font", "site_name", "tagline"}

# Fields that require full regeneration
STRUCTURAL_FIELDS = {"project_type", "website_type", "sections", "has_auth", "has_db"}


def is_minor_edit(old_config: dict, new_config: dict) -> bool:
    """
    Detect if the change between two configs is minor (cosmetic only).
    If True, we can skip full regeneration and just patch CSS/content.
    """
    for field in STRUCTURAL_FIELDS:
        if old_config.get(field) != new_config.get(field):
            return False
    return True


def get_changed_fields(old_config: dict, new_config: dict) -> list[str]:
    """Return list of fields that changed between two configs."""
    all_fields = set(old_config.keys()) | set(new_config.keys())
    return [f for f in all_fields if old_config.get(f) != new_config.get(f)]


# ── Prompt compression ────────────────────────────────────────────────────────

# Verbose phrases → compact equivalents
COMPRESSIONS = [
    (r"i want (to |you to )?", ""),
    (r"please (create|make|build|generate) (me |a |an )?", "create "),
    (r"can you (create|make|build|generate) (me |a |an )?", "create "),
    (r"i need (a |an )?", "create "),
    (r"help me (create|make|build) (a |an )?", "create "),
    (r"with (a |the )?", "with "),
    (r"that (has|includes|contains) ", "with "),
    (r"and (also )?", "and "),
]


def compress_prompt(prompt: str) -> str:
    """
    Compress a verbose prompt to its essential intent.
    Reduces token usage if OpenAI integration is added.
    """
    text = prompt.lower().strip()
    for pattern, replacement in COMPRESSIONS:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── Cache stats ───────────────────────────────────────────────────────────────

def get_stats() -> dict:
    return database.get_cache_stats()
