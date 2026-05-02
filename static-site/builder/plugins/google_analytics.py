"""
Plugin: Google Analytics
Injects GA4 tracking script into <head>.

Config:
  plugins.google_analytics.enabled: true
  plugins.google_analytics.tracking_id: "G-XXXXXXXXXX"
"""

PLUGIN_ID = "google_analytics"


def inject(cfg: dict) -> dict:
    """Return dict with head/body/scripts HTML to inject."""
    plugin_cfg = cfg.get("plugins", {}).get(PLUGIN_ID, {})
    if not plugin_cfg.get("enabled", False):
        return {}

    tid = plugin_cfg.get("tracking_id", "")
    if not tid:
        return {}

    head_html = f"""<!-- Google Analytics (injected by plugin) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={tid}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{tid}');
</script>"""

    return {"head": head_html, "body": "", "scripts": ""}
