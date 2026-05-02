"""
Plugin loader — discovers and runs all enabled plugins.
Each plugin module must expose: inject(cfg) -> dict with keys: head, body, scripts
"""
import importlib
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent
KNOWN_PLUGINS = ["google_analytics", "whatsapp", "newsletter_popup"]


def run_all(cfg: dict) -> dict:
    """
    Run all enabled plugins and merge their injections.
    Returns: { "head": str, "body": str, "scripts": str }
    """
    result = {"head": "", "body": "", "scripts": ""}

    for plugin_id in KNOWN_PLUGINS:
        plugin_cfg = cfg.get("plugins", {}).get(plugin_id, {})
        if not plugin_cfg.get("enabled", False):
            continue
        try:
            mod = importlib.import_module(f"plugins.{plugin_id}")
            out = mod.inject(cfg)
            result["head"]    += out.get("head",    "")
            result["body"]    += out.get("body",    "")
            result["scripts"] += out.get("scripts", "")
            print(f"  🔌 Plugin '{plugin_id}' injected")
        except Exception as e:
            print(f"  ⚠  Plugin '{plugin_id}' failed: {e}")

    return result
