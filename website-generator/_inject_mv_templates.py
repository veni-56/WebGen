"""
Inject all _mv_* template helper functions into generator.py.
Run from website-generator/ directory.
"""
MARKER = (
    "# ─────────────────────────────────────────────────────────────────────────────\n"
    "# 4. SHARED CSS / JS\n"
    "# ─────────────────────────────────────────────────────────────────────────────"
)

with open("generator.py", encoding="utf-8") as f:
    content = f.read()

idx = content.find(MARKER)
if idx == -1:
    print("ERROR: marker not found"); exit(1)

# Read the new functions from the companion data file
with open("_mv_template_functions.py", encoding="utf-8") as f:
    new_funcs = f.read()

content = content[:idx] + new_funcs + "\n\n" + content[idx:]
with open("generator.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done — injected _mv_* template functions into generator.py")
