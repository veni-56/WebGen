"""
_upgrade_to_tailwind.py
Replaces ALL copies of _mv_base_html in generator.py with a
ShopWave-quality Tailwind + Alpine.js version.
Run: python _upgrade_to_tailwind.py
"""
import re

GENERATOR = "generator.py"

with open(GENERATOR, "r", encoding="utf-8") as f:
    src = f.read()

print(f"File size: {len(src):,} chars")
print(f"_mv_base_html occurrences: {src.count('def _mv_base_html(')}")
