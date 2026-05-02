"""
_static_pro.py — Modern multi-page static site generator
Tailwind CSS + Alpine.js + Dark Mode + Scroll animations
"""


def _sp_head(name: str, page_title: str, primary: str, font: str) -> str:
    font_url = font.replace(' ', '+')
    return f"""<!DOCTYPE html>
<html lang="en" x-data="app()" :class="dark ? 'dark' : ''" class="scroll-smooth">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{page_title} — {name}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            primary: {{
              50:'#f5f3ff',100:'#ede9fe',200:'#ddd6fe',300:'#c4b5fd',
              400:'#a78bfa',500:'{primary}',600:'#7c3aed',700:'#6d28d9',
              800:'#5b21b6',900:'#4c1d95'
            }}
          }},
          fontFamily: {{ sans: ['{font}','system-ui','sans-serif'] }}
        }}
      }}
    }}
  </script>
  <link href="https://fonts.googleapis.com/css2?family={font_url}:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <style>
    [x-cloak]{{display:none!important}}
    .reveal{{opacity:0;transform:translateY(20px);transition:opacity .6s ease,transform .6s ease}}
    .reveal.visible{{opacity:1;transform:none}}
    .nav-link{{position:relative}}
    .nav-link::after{{content:'';position:absolute;bottom:-2px;left:0;width:0;height:2px;background:currentColor;transition:width .2s}}
    .nav-link:hover::after,.nav-link.active-link::after{{width:100%}}
  </style>
</head>"""
