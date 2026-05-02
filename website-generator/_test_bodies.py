import pathlib, sys

WG = pathlib.Path("website-generator")

def read_body(f):
    return (WG / f).read_text(encoding="utf-8")

def _darken(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    r = max(0, int(r * 0.85))
    g = max(0, int(g * 0.85))
    b = max(0, int(b * 0.85))
    return f"#{r:02x}{g:02x}{b:02x}"

# Read all body files
bodies = {
    "index":        read_body("_index_body.html") if (WG / "_index_body.html").exists() else "",
    "about":        read_body("_about_body.html") if (WG / "_about_body.html").exists() else "",
    "services":     read_body("_services_body.html"),
    "portfolio":    read_body("_portfolio_body.html"),
    "blog":         read_body("_blog_body.html"),
    "contact":      read_body("_contact_body.html"),
    "pricing":      read_body("_pricing_body.html"),
    "team":         read_body("_team_body.html"),
    "faq":          read_body("_faq_body.html"),
    "testimonials": read_body("_testimonials_body.html"),
}

print("Bodies loaded:")
for k, v in bodies.items():
    print(f"  {k}: {len(v)} bytes")