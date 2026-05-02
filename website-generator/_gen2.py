import pathlib

B = pathlib.Path("static-site")
WG = pathlib.Path("website-generator")

def read(f):
    return (WG / f).read_text(encoding="utf-8")

HEAD_TMPL = """<!DOCTYPE html>
<html lang="en" x-data="{ dark: localStorage.getItem('dark')==='true', mobileOpen: false }" :class="dark ? 'dark' : ''" class="scroll-smooth">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>NovaTech &mdash; PAGE_TITLE</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: { extend: { colors: { primary: { 50:'#f5f3ff', 500:'#6c63ff', 600:'#5a52d5' }, secondary: { 500:'#f50057' } }, fontFamily: { sans: ['Inter','system-ui','sans-serif'] } } }
    }
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <link rel="stylesheet" href="style.css"/>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white font-sans antialiased">
"""

def pg(title, body_file):
    head = HEAD_TMPL.replace("PAGE_TITLE", title)
    nav = read("_nav.html")
    body = read(body_file)
    foot = read("_foot.html")
    return head + nav + body + foot

pages = {
    "services.html":     ("Services",     "_services_body.html"),
    "portfolio.html":    ("Portfolio",    "_portfolio_body.html"),
    "blog.html":         ("Blog",         "_blog_body.html"),
    "contact.html":      ("Contact",      "_contact_body.html"),
    "pricing.html":      ("Pricing",      "_pricing_body.html"),
    "team.html":         ("Team",         "_team_body.html"),
    "faq.html":          ("FAQ",          "_faq_body.html"),
    "testimonials.html": ("Testimonials", "_testimonials_body.html"),
}

for filename, (title, body_file) in pages.items():
    content = pg(title, body_file)
    (B / filename).write_text(content, encoding="utf-8")
    print(f"wrote {filename} ({len(content)} bytes)")

print("All pages written!")