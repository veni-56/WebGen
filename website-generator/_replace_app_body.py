"""
Replace the broken _MV_APP_PY_BODY in generator.py with the complete
ShopWave multi-vendor marketplace app.py body.
Run from website-generator/ directory.
"""
import re

START_MARKER = "_MV_APP_PY_BODY = '''\"\"\""
END_MARKER   = "\nif __name__ == '__main__':\n    init_db()\n    app.run(debug=True)\n'''"

with open("generator.py", encoding="utf-8") as f:
    content = f.read()

si = content.find(START_MARKER)
ei = content.find(END_MARKER, si)
if si == -1 or ei == -1:
    print(f"ERROR: markers not found. si={si} ei={ei}")
    exit(1)

ei += len(END_MARKER)
print(f"Replacing chars {si}..{ei} ({ei-si} chars)")

with open("_new_app_body.py", encoding="utf-8") as f:
    new_body = f.read()

content = content[:si] + new_body + content[ei:]
with open("generator.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done.")
