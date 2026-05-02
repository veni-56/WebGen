"""
sections.py — Reusable HTML section generators.
Each function takes cfg dict and returns an HTML string.
"""


def _r(cfg): return "reveal" if cfg["features"].get("animations") else ""
def _rl(cfg): return "reveal-left" if cfg["features"].get("animations") else ""
def _rr(cfg): return "reveal-right" if cfg["features"].get("animations") else ""
def _ch(cfg): return "card-hover" if cfg["features"].get("animations") else ""


def section_hero(cfg: dict) -> str:
    r = _r(cfg)
    return f"""<section class="relative overflow-hidden py-24 md:py-36 px-4" aria-labelledby="hero-heading">
  <div class="absolute inset-0 bg-gradient-to-br from-
