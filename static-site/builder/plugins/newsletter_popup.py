"""
Plugin: Newsletter Popup
Shows a modal popup after a configurable delay.

Config:
  plugins.newsletter_popup.enabled: true
  plugins.newsletter_popup.delay_seconds: 5
  plugins.newsletter_popup.title: "Get Exclusive Updates"
  plugins.newsletter_popup.subtitle: "Join 10,000+ teams. No spam, ever."
"""

PLUGIN_ID = "newsletter_popup"


def inject(cfg: dict) -> dict:
    plugin_cfg = cfg.get("plugins", {}).get(PLUGIN_ID, {})
    if not plugin_cfg.get("enabled", False):
        return {}

    delay    = int(plugin_cfg.get("delay_seconds", 5)) * 1000
    title    = plugin_cfg.get("title",    "Get Exclusive Updates")
    subtitle = plugin_cfg.get("subtitle", "Join 10,000+ teams. No spam, ever.")

    body_html = f"""<!-- Newsletter Popup (injected by plugin) -->
<div id="nlPopup" x-data="{{show:false}}" x-init="setTimeout(()=>show=true,{delay})"
     x-show="show" x-transition x-cloak
     class="fixed inset-0 z-[9998] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
     @click.self="show=false" role="dialog" aria-modal="true" aria-labelledby="nlTitle">
  <div class="bg-white dark:bg-gray-900 rounded-2xl p-8 max-w-md w-full shadow-2xl border border-gray-100 dark:border-gray-800 relative">
    <button @click="show=false"
            class="absolute top-4 right-4 w-8 h-8 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close popup">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
    </button>
    <div class="text-center mb-6">
      <div class="text-4xl mb-3" aria-hidden="true">📬</div>
      <h3 id="nlTitle" class="text-xl font-black dark:text-white mb-2">{title}</h3>
      <p class="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
    </div>
    <form onsubmit="event.preventDefault();document.getElementById('nlPopup').__x.$data.show=false;showToast('Subscribed! 🎉')" class="space-y-3">
      <input type="email" required placeholder="your@email.com"
             class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 transition-all dark:text-white"
             aria-label="Email address"/>
      <button type="submit"
              class="w-full btn-gradient py-3 rounded-full font-bold text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-offset-2">
        Subscribe Free
      </button>
    </form>
    <p class="text-xs text-gray-400 text-center mt-3">No spam. Unsubscribe anytime.</p>
  </div>
</div>"""

    return {"head": "", "body": body_html, "scripts": ""}
