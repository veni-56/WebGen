"""
_do_upgrade.py — Replace old Bootstrap _mv_base_html with Tailwind version.
Run: python _do_upgrade.py
"""
import re

with open("generator.py", encoding="utf-8") as f:
    src = f.read()

print(f"File: {len(src):,} chars, {src.count('def _mv_base_html(')} copies of _mv_base_html")

# ── New Tailwind base_html ────────────────────────────────────────────────────
# Uses {site_name} f-string interpolation (outer f-string in generator.py)
# Jinja2 tags use {{%  %}} and {{{{  }}}} to survive the f-string

NEW_BASE_FUNC = r'''def _mv_base_html(site_name: str, font: str) -> str:
    sn = site_name
    return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <