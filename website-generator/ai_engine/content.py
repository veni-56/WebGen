"""
ai_engine/content.py — AI Content Generator
Generates realistic, SEO-optimized website copy for every section.
Works in two modes:
  1. Template mode (default) — industry-specific copy templates
  2. OpenAI mode — GPT-generated unique copy (when OPENAI_API_KEY is set)
Supports multi-language output.
"""
import os
import re
from utils.logger import get_logger

logger = get_logger("ai_engine.content")

# ── Multi-language support ────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "hi": "Hindi",
    "ar": "Arabic",
    "pt": "Portuguese",
    "zh": "Chinese",
    "ja": "Japanese",
    "ur": "Urdu",
}

# ── Industry content templates ────────────────────────────────────────────────
CONTENT_TEMPLATES = {
    "fintech": {
        "hero": {
            "heading":    "The Future of Finance, Today",
            "subheading": "Secure, fast, and intelligent financial solutions for modern businesses.",
            "cta":        "Start Free Trial",
            "cta_secondary": "See How It Works",
        },
        "about": {
            "heading":    "Built for the Modern Economy",
            "body":       "We combine cutting-edge technology with deep financial expertise to deliver solutions that scale with your business. Our platform processes millions of transactions daily with 99.99% uptime.",
            "stats":      [("$2B+", "Processed"), ("50K+", "Businesses"), ("99.99%", "Uptime")],
        },
        "features": [
            {"icon": "🔒", "title": "Bank-Grade Security", "desc": "256-bit encryption and multi-factor authentication protect every transaction."},
            {"icon": "⚡", "title": "Instant Transfers", "desc": "Move money in seconds, not days. Real-time settlement across 150+ countries."},
            {"icon": "📊", "title": "Smart Analytics", "desc": "AI-powered insights help you understand your cash flow and optimize spending."},
            {"icon": "🌍", "title": "Global Reach", "desc": "Accept payments in 135+ currencies with automatic conversion."},
        ],
        "testimonials": [
            {"name": "Sarah Chen", "role": "CFO, TechCorp", "text": "Reduced our payment processing costs by 40% in the first month."},
            {"name": "Marcus Johnson", "role": "Founder, StartupX", "text": "The best fintech platform we've used. Setup took 10 minutes."},
        ],
        "seo": {
            "title":       "Fintech Platform — Secure Payments & Financial Tools",
            "description": "Modern financial platform with instant transfers, smart analytics, and bank-grade security. Start free today.",
            "keywords":    "fintech, payment processing, financial platform, secure payments, money transfer",
        },
    },
    "ecommerce": {
        "hero": {
            "heading":    "Shop Smarter, Live Better",
            "subheading": "Discover thousands of products at unbeatable prices. Free shipping on orders over $50.",
            "cta":        "Shop Now",
            "cta_secondary": "View Deals",
        },
        "about": {
            "heading":    "Your Trusted Shopping Destination",
            "body":       "We curate the best products from verified sellers worldwide. Every purchase is protected by our buyer guarantee — if it's not right, we'll make it right.",
            "stats":      [("10K+", "Products"), ("500K+", "Happy Customers"), ("4.8★", "Rating")],
        },
        "features": [
            {"icon": "🚚", "title": "Fast Delivery", "desc": "Same-day delivery available in 50+ cities. Track your order in real-time."},
            {"icon": "🔄", "title": "Easy Returns", "desc": "30-day hassle-free returns. No questions asked."},
            {"icon": "🛡️", "title": "Buyer Protection", "desc": "Every purchase is covered by our 100% satisfaction guarantee."},
            {"icon": "💳", "title": "Secure Checkout", "desc": "Pay with card, UPI, wallet, or cash on delivery."},
        ],
        "seo": {
            "title":       "Online Shopping — Best Deals on Electronics, Fashion & More",
            "description": "Shop thousands of products at the best prices. Free shipping, easy returns, and secure checkout.",
            "keywords":    "online shopping, best deals, free shipping, electronics, fashion, home goods",
        },
    },
    "saas": {
        "hero": {
            "heading":    "Build Faster. Scale Smarter.",
            "subheading": "The all-in-one platform that helps teams ship products 10x faster with AI-powered automation.",
            "cta":        "Start Free — No Credit Card",
            "cta_secondary": "Watch Demo",
        },
        "about": {
            "heading":    "Trusted by 10,000+ Teams Worldwide",
            "body":       "From early-stage startups to Fortune 500 companies, teams choose us to streamline their workflow, reduce costs, and ship faster. Our platform integrates with 200+ tools you already use.",
            "stats":      [("10K+", "Teams"), ("200+", "Integrations"), ("40%", "Faster Shipping")],
        },
        "features": [
            {"icon": "🤖", "title": "AI Automation", "desc": "Automate repetitive tasks and let your team focus on what matters."},
            {"icon": "📈", "title": "Real-time Analytics", "desc": "Track every metric that matters with beautiful, actionable dashboards."},
            {"icon": "🔗", "title": "200+ Integrations", "desc": "Connect with Slack, GitHub, Jira, and 200+ tools in one click."},
            {"icon": "🔒", "title": "Enterprise Security", "desc": "SOC 2 Type II certified. Your data is always safe and private."},
        ],
        "seo": {
            "title":       "SaaS Platform — AI-Powered Workflow Automation",
            "description": "Streamline your team's workflow with AI automation, real-time analytics, and 200+ integrations. Start free today.",
            "keywords":    "saas platform, workflow automation, team productivity, project management, ai tools",
        },
    },
    "portfolio": {
        "hero": {
            "heading":    "I Design Experiences That Matter",
            "subheading": "Full-stack developer & UI/UX designer crafting digital products that users love.",
            "cta":        "View My Work",
            "cta_secondary": "Hire Me",
        },
        "about": {
            "heading":    "Passionate About Craft",
            "body":       "With 5+ years of experience building digital products, I specialize in creating clean, performant, and accessible web applications. I believe great design is invisible — it just works.",
            "stats":      [("50+", "Projects"), ("30+", "Clients"), ("5+", "Years")],
        },
        "seo": {
            "title":       "Portfolio — Full-Stack Developer & UI/UX Designer",
            "description": "Experienced developer and designer creating beautiful, functional web applications. Available for freelance projects.",
            "keywords":    "portfolio, web developer, ui ux designer, freelance, full stack developer",
        },
    },
    "health": {
        "hero": {
            "heading":    "Your Health, Our Priority",
            "subheading": "Compassionate, evidence-based care delivered by experienced professionals.",
            "cta":        "Book Appointment",
            "cta_secondary": "Learn More",
        },
        "about": {
            "heading":    "Trusted Healthcare Since 2010",
            "body":       "Our team of board-certified physicians and specialists provides comprehensive healthcare services. We combine the latest medical technology with a patient-first approach to deliver exceptional outcomes.",
            "stats":      [("15K+", "Patients"), ("25+", "Specialists"), ("98%", "Satisfaction")],
        },
        "seo": {
            "title":       "Healthcare Clinic — Compassionate, Expert Medical Care",
            "description": "Board-certified physicians providing comprehensive healthcare. Book your appointment online today.",
            "keywords":    "healthcare, medical clinic, doctor, appointment, health services",
        },
    },
    "default": {
        "hero": {
            "heading":    "Welcome to the Future",
            "subheading": "We help businesses grow with innovative solutions and exceptional service.",
            "cta":        "Get Started",
            "cta_secondary": "Learn More",
        },
        "about": {
            "heading":    "About Us",
            "body":       "We are a passionate team dedicated to delivering exceptional results. Our expertise, combined with a client-first approach, has helped hundreds of businesses achieve their goals.",
            "stats":      [("500+", "Clients"), ("10+", "Years"), ("99%", "Satisfaction")],
        },
        "features": [
            {"icon": "⚡", "title": "Fast & Reliable", "desc": "Built for performance and reliability at any scale."},
            {"icon": "🎯", "title": "Results Driven", "desc": "Every decision is backed by data and focused on your goals."},
            {"icon": "🤝", "title": "Expert Support", "desc": "Our team is available 24/7 to help you succeed."},
            {"icon": "🔒", "title": "Secure & Private", "desc": "Your data is protected with enterprise-grade security."},
        ],
        "seo": {
            "title":       "Professional Services — Quality You Can Trust",
            "description": "Delivering exceptional results with expertise and dedication. Contact us today.",
            "keywords":    "professional services, business solutions, quality, expertise",
        },
    },
}

# ── Language translations for UI strings ──────────────────────────────────────
UI_TRANSLATIONS = {
    "en": {"get_started": "Get Started", "learn_more": "Learn More",
           "contact_us": "Contact Us", "about": "About", "services": "Services"},
    "es": {"get_started": "Comenzar", "learn_more": "Saber Más",
           "contact_us": "Contáctenos", "about": "Nosotros", "services": "Servicios"},
    "fr": {"get_started": "Commencer", "learn_more": "En Savoir Plus",
           "contact_us": "Contactez-nous", "about": "À Propos", "services": "Services"},
    "de": {"get_started": "Loslegen", "learn_more": "Mehr Erfahren",
           "contact_us": "Kontakt", "about": "Über Uns", "services": "Leistungen"},
    "hi": {"get_started": "शुरू करें", "learn_more": "और जानें",
           "contact_us": "संपर्क करें", "about": "हमारे बारे में", "services": "सेवाएं"},
    "ur": {"get_started": "شروع کریں", "learn_more": "مزید جانیں",
           "contact_us": "رابطہ کریں", "about": "ہمارے بارے میں", "services": "خدمات"},
    "ar": {"get_started": "ابدأ الآن", "learn_more": "اعرف المزيد",
           "contact_us": "اتصل بنا", "about": "من نحن", "services": "خدماتنا"},
    "pt": {"get_started": "Começar", "learn_more": "Saiba Mais",
           "contact_us": "Contate-nos", "about": "Sobre Nós", "services": "Serviços"},
}


class ContentGenerator:
    """Generates website copy for all sections."""

    def __init__(self):
        self._openai = bool(os.environ.get("OPENAI_API_KEY"))

    def generate(self, site_name: str, industry: str, website_type: str,
                 language: str = "en") -> dict:
        """
        Generate complete content for a website.
        Returns dict with content for each section.
        """
        if self._openai:
            try:
                return self._openai_generate(site_name, industry, website_type, language)
            except Exception as e:
                logger.warning("OpenAI content failed, using templates: %s", e)

        return self._template_generate(site_name, industry, website_type, language)

    def _template_generate(self, site_name: str, industry: str,
                            website_type: str, language: str) -> dict:
        """Generate content from industry templates."""
        # Find best matching template
        template_key = industry if industry in CONTENT_TEMPLATES else "default"
        template = CONTENT_TEMPLATES[template_key]

        # Personalize with site name
        content = {}
        for section, data in template.items():
            if isinstance(data, dict):
                content[section] = {
                    k: v.replace("We ", f"{site_name} ").replace("Our ", f"{site_name}'s ")
                    if isinstance(v, str) else v
                    for k, v in data.items()
                }
            else:
                content[section] = data

        # Add UI translations
        content["ui"] = UI_TRANSLATIONS.get(language, UI_TRANSLATIONS["en"])
        content["language"] = language
        content["site_name"] = site_name

        logger.info("Content generated for %s (%s, %s)", site_name, industry, language)
        return content

    def _openai_generate(self, site_name: str, industry: str,
                         website_type: str, language: str) -> dict:
        """Generate unique content via OpenAI."""
        import openai, json
        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        lang_name = SUPPORTED_LANGUAGES.get(language, "English")
        prompt = f"""Generate website content for "{site_name}", a {industry} {website_type} website.
Language: {lang_name}

Return JSON with:
{{
  "hero": {{"heading": "", "subheading": "", "cta": "", "cta_secondary": ""}},
  "about": {{"heading": "", "body": "", "stats": [["value", "label"]]}},
  "features": [{{"icon": "emoji", "title": "", "desc": ""}}],
  "testimonials": [{{"name": "", "role": "", "text": ""}}],
  "seo": {{"title": "", "description": "", "keywords": ""}}
}}

Make it professional, compelling, and SEO-optimized for the {industry} industry."""

        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )
        content = json.loads(response.choices[0].message.content)
        content["ui"] = UI_TRANSLATIONS.get(language, UI_TRANSLATIONS["en"])
        content["language"] = language
        content["site_name"] = site_name
        logger.info("OpenAI content generated for %s", site_name)
        return content

    def rewrite_text(self, text: str, tone: str = "professional",
                     instruction: str = "") -> str:
        """
        Rewrite a piece of text with a given tone/instruction.
        Used by the inline AI editor.
        """
        if not self._openai:
            return self._template_rewrite(text, tone)

        try:
            import openai
            client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            system = f"You are a professional copywriter. Rewrite text to be {tone}."
            user_msg = instruction or f"Rewrite this to be more {tone}: {text}"
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user_msg},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning("OpenAI rewrite failed: %s", e)
            return self._template_rewrite(text, tone)

    def _template_rewrite(self, text: str, tone: str) -> str:
        """Simple template-based rewrite (no API)."""
        rewrites = {
            "professional": f"{text} Our team of experts ensures the highest quality standards.",
            "marketing":    f"🚀 {text} — Don't miss out! Join thousands of satisfied customers today.",
            "casual":       f"Hey! {text} We'd love to help you out.",
            "formal":       f"We are pleased to inform you that {text.lower()}",
        }
        return rewrites.get(tone, text)

    def generate_blog_post(self, topic: str, industry: str = "default") -> dict:
        """Generate a complete blog post."""
        if self._openai:
            try:
                return self._openai_blog_post(topic, industry)
            except Exception as e:
                logger.warning("OpenAI blog post failed: %s", e)

        return {
            "title":   f"The Complete Guide to {topic.title()}",
            "excerpt": f"Everything you need to know about {topic} in {industry}.",
            "content": f"""# The Complete Guide to {topic.title()}

## Introduction

{topic.title()} is one of the most important topics in {industry} today. 
In this comprehensive guide, we'll cover everything you need to know.

## Key Points

1. **Understanding the basics** — Start with the fundamentals before diving deep.
2. **Best practices** — Learn from industry leaders and apply proven strategies.
3. **Common mistakes** — Avoid the pitfalls that trip up most beginners.
4. **Advanced techniques** — Take your knowledge to the next level.

## Conclusion

Mastering {topic} takes time and practice, but the results are worth it.
Start implementing these strategies today and see the difference.
""",
            "tags":    [topic, industry, "guide", "tips"],
            "seo_title": f"{topic.title()} Guide — Everything You Need to Know",
            "seo_desc":  f"Complete guide to {topic} for {industry} professionals. Tips, best practices, and expert advice.",
        }

    def _openai_blog_post(self, topic: str, industry: str) -> dict:
        import openai, json
        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content":
                f"Write a 400-word SEO-optimized blog post about '{topic}' for the {industry} industry. "
                f"Return JSON: {{title, excerpt, content (markdown), tags (array), seo_title, seo_desc}}"}],
            temperature=0.7, max_tokens=800,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
