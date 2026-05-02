"""
ai_engine/seo.py — SEO + Performance Engine
Automatically injects SEO optimization into every generated site:
- Meta tags, OpenGraph, Twitter Cards
- sitemap.xml, robots.txt
- Structured data (JSON-LD)
- Performance: lazy loading, preconnect hints, critical CSS
- Lighthouse score optimization hints
"""
from utils.logger import get_logger

logger = get_logger("ai_engine.seo")


def inject_seo(html: str, seo: dict, site_url: str = "https://example.com") -> str:
    """
    Inject SEO meta tags into an HTML string.
    Replaces </head> with meta tags + </head>.
    """
    title       = seo.get("title", "My Website")
    description = seo.get("description", "")
    keywords    = seo.get("keywords", "")
    image       = seo.get("og_image", f"{site_url}/static/og-image.png")
    canonical   = seo.get("canonical", site_url)

    meta_block = f"""
  <!-- SEO Meta Tags -->
  <meta name="description" content="{description}"/>
  <meta name="keywords" content="{keywords}"/>
  <meta name="robots" content="index, follow"/>
  <link rel="canonical" href="{canonical}"/>

  <!-- Open Graph -->
  <meta property="og:type" content="website"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{description}"/>
  <meta property="og:image" content="{image}"/>
  <meta property="og:url" content="{canonical}"/>
  <meta property="og:site_name" content="{title}"/>

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:title" content="{title}"/>
  <meta name="twitter:description" content="{description}"/>
  <meta name="twitter:image" content="{image}"/>

  <!-- Performance hints -->
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link rel="dns-prefetch" href="https://fonts.googleapis.com"/>
"""
    return html.replace("</head>", meta_block + "</head>", 1)


def inject_structured_data(html: str, schema: dict) -> str:
    """Inject JSON-LD structured data before </body>."""
    import json
    script = f'\n<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>\n'
    return html.replace("</body>", script + "</body>", 1)


def inject_lazy_loading(html: str) -> str:
    """Add loading="lazy" to all img tags that don't already have it."""
    import re
    # Add lazy loading to images
    html = re.sub(
        r'<img(?![^>]*loading=)([^>]*)>',
        r'<img loading="lazy"\1>',
        html
    )
    return html


def generate_sitemap(site_name: str, site_url: str, pages: list) -> str:
    """Generate a sitemap.xml for a website."""
    from datetime import date
    today = date.today().isoformat()

    urls = "\n".join([
        f"""  <url>
    <loc>{site_url}{page}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{"1.0" if page == "/" else "0.8"}</priority>
  </url>"""
        for page in pages
    ])

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""


def generate_robots_txt(site_url: str, disallow: list = None) -> str:
    """Generate robots.txt."""
    disallow_lines = "\n".join(
        f"Disallow: {path}" for path in (disallow or ["/admin", "/api/"])
    )
    return f"""User-agent: *
Allow: /
{disallow_lines}

Sitemap: {site_url}/sitemap.xml
"""


def get_schema_org(schema_type: str, data: dict) -> dict:
    """Generate Schema.org structured data."""
    schemas = {
        "organization": {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": data.get("name", ""),
            "url": data.get("url", ""),
            "description": data.get("description", ""),
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "customer service",
                "email": data.get("email", ""),
            },
        },
        "website": {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": data.get("name", ""),
            "url": data.get("url", ""),
            "description": data.get("description", ""),
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{data.get('url', '')}/search?q={{search_term_string}}",
                "query-input": "required name=search_term_string",
            },
        },
        "product": {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "offers": {
                "@type": "Offer",
                "price": data.get("price", "0"),
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
            },
        },
        "blog": {
            "@context": "https://schema.org",
            "@type": "Blog",
            "name": data.get("name", ""),
            "url": data.get("url", ""),
            "description": data.get("description", ""),
        },
    }
    return schemas.get(schema_type, schemas["website"])


def get_performance_css() -> str:
    """Critical CSS additions for performance."""
    return """
/* Performance: reduce layout shift */
img, video { max-width: 100%; height: auto; }
img[loading="lazy"] { opacity: 0; transition: opacity .3s; }
img[loading="lazy"].loaded { opacity: 1; }

/* Smooth font loading */
@font-face { font-display: swap; }

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    transition-duration: .01ms !important;
  }
}
"""


def get_performance_js() -> str:
    """Performance JavaScript additions."""
    return """
// Lazy image loading polyfill
if ('IntersectionObserver' in window) {
  const imgObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const img = e.target;
        img.src = img.dataset.src || img.src;
        img.classList.add('loaded');
        imgObserver.unobserve(img);
      }
    });
  });
  document.querySelectorAll('img[loading="lazy"]').forEach(img => imgObserver.observe(img));
}
"""


def get_lighthouse_hints(project_type: str) -> list:
    """Return Lighthouse optimization hints for a project type."""
    common = [
        "Add width and height attributes to all <img> tags to prevent layout shift",
        "Minify CSS and JavaScript files before deployment",
        "Enable gzip compression on your web server",
        "Use a CDN for static assets",
        "Add a service worker for offline support",
    ]
    specific = {
        "ecommerce": [
            "Optimize product images (use WebP format)",
            "Implement infinite scroll or pagination for product lists",
            "Add structured data for products (Schema.org/Product)",
        ],
        "blog": [
            "Add article structured data (Schema.org/Article)",
            "Implement reading time estimate",
            "Add social sharing buttons",
        ],
        "static": [
            "Consider deploying to a CDN (Netlify, Vercel)",
            "Add a manifest.json for PWA support",
        ],
    }
    return common + specific.get(project_type, [])


def enhance_project_files(files: dict, config: dict,
                           site_url: str = "https://example.com") -> dict:
    """
    Enhance a generated project's files with SEO and performance optimizations.
    Modifies index.html and adds sitemap.xml, robots.txt.
    """
    site_name   = config.get("site_name", "My Website")
    ptype       = config.get("project_type", "static")
    website_type = config.get("website_type", "business")

    # Build SEO data
    seo = {
        "title":       f"{site_name} — {website_type.title()} Website",
        "description": config.get("tagline", f"Welcome to {site_name}"),
        "keywords":    f"{site_name}, {website_type}, {', '.join(config.get('sections', [])[:5])}",
        "canonical":   site_url,
    }

    # Inject into index.html
    if "index.html" in files:
        html = files["index.html"]
        html = inject_seo(html, seo, site_url)
        html = inject_lazy_loading(html)

        # Add structured data
        schema = get_schema_org("website", {
            "name": site_name,
            "url":  site_url,
            "description": seo["description"],
        })
        html = inject_structured_data(html, schema)
        files["index.html"] = html

    # Add sitemap.xml
    pages = ["/"]
    for section in config.get("sections", []):
        if section not in ("header", "footer", "hero"):
            pages.append(f"/#{section}")
    files["sitemap.xml"] = generate_sitemap(site_name, site_url, pages)

    # Add robots.txt
    disallow = ["/admin", "/api/"] if ptype != "static" else []
    files["robots.txt"] = generate_robots_txt(site_url, disallow)

    # Add performance CSS to style.css
    if "style.css" in files:
        files["style.css"] += "\n" + get_performance_css()

    # Add performance JS to script.js
    if "script.js" in files:
        files["script.js"] += "\n" + get_performance_js()

    logger.info("SEO enhanced: %s (%s)", site_name, ptype)
    return files
