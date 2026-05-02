"""
ai_engine/plugins.py — Plugin / Extension System
Users can add plugins to their generated websites:
chatbot, analytics, payment gateway, newsletter, cookie consent, etc.
"""
from utils.logger import get_logger

logger = get_logger("ai_engine.plugins")

# ── Plugin registry ───────────────────────────────────────────────────────────
PLUGINS = {
    "chatbot": {
        "name":        "Live Chat",
        "description": "Add a live chat widget (Tawk.to — free)",
        "icon":        "💬",
        "category":    "support",
        "config_fields": [
            {"key": "property_id", "label": "Tawk.to Property ID", "type": "text",
             "placeholder": "Get from tawk.to dashboard"},
        ],
        "inject_head": "",
        "inject_body": lambda cfg: f"""
<!-- Tawk.to Live Chat -->
<script type="text/javascript">
var Tawk_API=Tawk_API||{{}}, Tawk_LoadStart=new Date();
(function(){{
  var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
  s1.async=true;
  s1.src='https://embed.tawk.to/{cfg.get("property_id","YOUR_PROPERTY_ID")}/default';
  s1.charset='UTF-8';
  s1.setAttribute('crossorigin','*');
  s0.parentNode.insertBefore(s1,s0);
}})();
</script>""",
    },
    "analytics_ga": {
        "name":        "Google Analytics",
        "description": "Track visitors with Google Analytics 4",
        "icon":        "📊",
        "category":    "analytics",
        "config_fields": [
            {"key": "measurement_id", "label": "GA4 Measurement ID", "type": "text",
             "placeholder": "G-XXXXXXXXXX"},
        ],
        "inject_head": lambda cfg: f"""
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={cfg.get('measurement_id','G-XXXXXXXXXX')}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{cfg.get("measurement_id","G-XXXXXXXXXX")}');
</script>""",
        "inject_body": "",
    },
    "stripe_payment": {
        "name":        "Stripe Payments",
        "description": "Accept payments with Stripe Checkout",
        "icon":        "💳",
        "category":    "payment",
        "config_fields": [
            {"key": "publishable_key", "label": "Stripe Publishable Key", "type": "text",
             "placeholder": "pk_live_..."},
            {"key": "price_id", "label": "Stripe Price ID", "type": "text",
             "placeholder": "price_..."},
        ],
        "inject_head": lambda cfg: '<script src="https://js.stripe.com/v3/"></script>',
        "inject_body": lambda cfg: f"""
<script>
const stripe = Stripe('{cfg.get("publishable_key","pk_test_...")}');
document.querySelectorAll('.stripe-checkout-btn').forEach(btn => {{
  btn.addEventListener('click', async () => {{
    const {{error}} = await stripe.redirectToCheckout({{
      lineItems: [{{price: '{cfg.get("price_id","price_...")}', quantity: 1}}],
      mode: 'payment',
      successUrl: window.location.origin + '/success',
      cancelUrl: window.location.origin + '/cancel',
    }});
    if (error) console.error(error);
  }});
}});
</script>""",
    },
    "newsletter": {
        "name":        "Newsletter Signup",
        "description": "Collect emails with Mailchimp",
        "icon":        "📧",
        "category":    "marketing",
        "config_fields": [
            {"key": "form_action", "label": "Mailchimp Form Action URL", "type": "text",
             "placeholder": "https://xxx.list-manage.com/subscribe/post?..."},
        ],
        "inject_head": "",
        "inject_body": lambda cfg: f"""
<!-- Newsletter Signup Widget -->
<div id="newsletter-widget" style="position:fixed;bottom:20px;right:20px;background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 4px 24px rgba(0,0,0,.15);max-width:300px;z-index:999;display:none">
  <button onclick="this.parentElement.style.display='none'" style="position:absolute;top:.5rem;right:.75rem;background:none;border:none;font-size:1.2rem;cursor:pointer">✕</button>
  <h4 style="margin-bottom:.75rem">📧 Stay Updated</h4>
  <form action="{cfg.get('form_action','#')}" method="POST" target="_blank">
    <input type="email" name="EMAIL" placeholder="Your email" required style="width:100%;padding:.6rem;border:1px solid #ddd;border-radius:6px;margin-bottom:.5rem"/>
    <button type="submit" style="width:100%;padding:.6rem;background:#6c63ff;color:#fff;border:none;border-radius:6px;cursor:pointer">Subscribe</button>
  </form>
</div>
<script>setTimeout(()=>{{document.getElementById('newsletter-widget').style.display='block'}},5000)</script>""",
    },
    "cookie_consent": {
        "name":        "Cookie Consent",
        "description": "GDPR-compliant cookie consent banner",
        "icon":        "🍪",
        "category":    "legal",
        "config_fields": [],
        "inject_head": "",
        "inject_body": lambda cfg: """
<!-- Cookie Consent -->
<div id="cookie-banner" style="position:fixed;bottom:0;left:0;right:0;background:#1a1a2e;color:#fff;padding:1rem 1.5rem;display:flex;align-items:center;justify-content:space-between;z-index:9999;flex-wrap:wrap;gap:.75rem">
  <span style="font-size:.9rem">🍪 We use cookies to improve your experience. <a href="/privacy" style="color:#6c63ff">Learn more</a></span>
  <div style="display:flex;gap:.5rem">
    <button onclick="document.getElementById('cookie-banner').style.display='none';localStorage.setItem('cookies','accepted')" style="background:#6c63ff;color:#fff;border:none;padding:.5rem 1.25rem;border-radius:6px;cursor:pointer">Accept</button>
    <button onclick="document.getElementById('cookie-banner').style.display='none'" style="background:transparent;color:#aaa;border:1px solid #444;padding:.5rem 1.25rem;border-radius:6px;cursor:pointer">Decline</button>
  </div>
</div>
<script>if(localStorage.getItem('cookies'))document.getElementById('cookie-banner').style.display='none'</script>""",
    },
    "whatsapp": {
        "name":        "WhatsApp Button",
        "description": "Floating WhatsApp contact button",
        "icon":        "📱",
        "category":    "support",
        "config_fields": [
            {"key": "phone", "label": "WhatsApp Number (with country code)", "type": "text",
             "placeholder": "+1234567890"},
            {"key": "message", "label": "Pre-filled message", "type": "text",
             "placeholder": "Hello! I'd like to know more..."},
        ],
        "inject_head": "",
        "inject_body": lambda cfg: f"""
<!-- WhatsApp Float Button -->
<a href="https://wa.me/{cfg.get('phone','').replace('+','').replace(' ','')}?text={cfg.get('message','Hello').replace(' ','%20')}"
   target="_blank" rel="noopener"
   style="position:fixed;bottom:20px;left:20px;background:#25d366;color:#fff;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.6rem;box-shadow:0 4px 16px rgba(37,211,102,.4);z-index:999;text-decoration:none"
   title="Chat on WhatsApp">💬</a>""",
    },
}


def get_all_plugins() -> dict:
    """Return all available plugins (without lambda functions for JSON serialization)."""
    result = {}
    for key, plugin in PLUGINS.items():
        result[key] = {
            "name":          plugin["name"],
            "description":   plugin["description"],
            "icon":          plugin["icon"],
            "category":      plugin["category"],
            "config_fields": plugin["config_fields"],
        }
    return result


def inject_plugin(html: str, plugin_type: str, config: dict) -> str:
    """Inject a plugin's code into an HTML string."""
    plugin = PLUGINS.get(plugin_type)
    if not plugin:
        return html

    # Inject head code
    head_code = plugin.get("inject_head", "")
    if callable(head_code):
        head_code = head_code(config)
    if head_code:
        html = html.replace("</head>", head_code + "\n</head>", 1)

    # Inject body code
    body_code = plugin.get("inject_body", "")
    if callable(body_code):
        body_code = body_code(config)
    if body_code:
        html = html.replace("</body>", body_code + "\n</body>", 1)

    logger.info("Injected plugin: %s", plugin_type)
    return html


def inject_all_plugins(html: str, plugins: list) -> str:
    """Inject multiple plugins into HTML."""
    for p in plugins:
        if p.get("enabled", True):
            html = inject_plugin(html, p["plugin_type"], p.get("config", {}))
    return html
