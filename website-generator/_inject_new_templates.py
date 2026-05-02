"""
Inject new _mv_* template functions into generator.py.
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

with open("_new_mv_templates.py", encoding="utf-8") as f:
    t1 = f.read()
with open("_new_mv_templates2.py", encoding="utf-8") as f:
    t2 = f.read()
with open("_new_mv_templates3.py", encoding="utf-8") as f:
    t3 = f.read()

new_funcs = t1 + "\n\n" + t2 + "\n\n" + t3 + "\n\n"
content = content[:idx] + new_funcs + content[idx:]

with open("generator.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done — injected new template functions.")
