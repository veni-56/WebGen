"""
ai_engine/openai_gen.py — OpenAI Integration Layer
Optional enhancement: uses GPT to improve generated code quality.
Falls back gracefully when OPENAI_API_KEY is not set.
"""
import os
import json
from utils.logger import get_logger

logger = get_logger("ai_engine.openai")

_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))


class OpenAIGenerator:
    """
    Optional OpenAI-powered code enhancement.
    When enabled, can improve generated code quality.
    When disabled, passes through unchanged.
    """

    def __init__(self):
        self.enabled = _AVAILABLE
        if self.enabled:
            logger.info("OpenAI generator enabled (model: %s)",
                        os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))

    def enhance_css(self, css: str, theme: str, primary: str) -> str:
        """
        Optionally enhance generated CSS with OpenAI.
        Returns original CSS if OpenAI not available.
        """
        if not self.enabled:
            return css
        try:
            import openai
            client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            prompt = (
                f"Improve this CSS for a {theme} theme website with primary color {primary}. "
                f"Make it more polished and modern. Return only the CSS, no explanation.\n\n{css[:3000]}"
            )
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )
            enhanced = response.choices[0].message.content.strip()
            # Strip markdown code blocks if present
            enhanced = enhanced.replace("```css", "").replace("```", "").strip()
            logger.info("CSS enhanced via OpenAI")
            return enhanced
        except Exception as e:
            logger.warning("OpenAI CSS enhancement failed: %s", e)
            return css

    def generate_content(self, site_name: str, section: str,
                         website_type: str) -> dict:
        """
        Generate realistic content for a website section.
        Returns dict with content fields, or empty dict if unavailable.
        """
        if not self.enabled:
            return {}
        try:
            import openai
            client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            prompt = (
                f"Generate realistic content for the '{section}' section of a "
                f"{website_type} website called '{site_name}'. "
                f"Return JSON with relevant text fields (heading, subheading, body, cta_text, etc.)."
            )
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            content = json.loads(response.choices[0].message.content)
            logger.debug("Content generated for %s/%s", site_name, section)
            return content
        except Exception as e:
            logger.warning("OpenAI content generation failed: %s", e)
            return {}

    def is_available(self) -> bool:
        return self.enabled
