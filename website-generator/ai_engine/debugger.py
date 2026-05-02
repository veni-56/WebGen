"""
ai_engine/debugger.py — AI Code Debugger & Fixer
Detects issues in generated code and fixes them automatically.
Works without OpenAI (rule-based) + enhanced with OpenAI when available.
"""
import re
import os
from utils.logger import get_logger

logger = get_logger("ai_engine.debugger")

# ── Rule-based issue detectors ────────────────────────────────────────────────
HTML_CHECKS = [
    (r"<img(?![^>]*alt=)[^>]*>",          "Missing alt attribute on img tag",          "accessibility"),
    (r"<a(?![^>]*href=)[^>]*>",           "Anchor tag missing href attribute",          "html"),
    (r"<form(?![^>]*method=)[^>]*>",      "Form missing method attribute",              "html"),
    (r"<input(?![^>]*type=)[^>]*>",       "Input missing type attribute",               "html"),
    (r"style=['\"][^'\"]*!important",     "Avoid !important in inline styles",          "css"),
    (r"onclick=['\"][^'\"]*javascript:",  "Avoid javascript: in onclick handlers",      "security"),
    (r"<script[^>]*src=['\"]http://",     "HTTP script source — use HTTPS",             "security"),
]

CSS_CHECKS = [
    (r"color:\s*#fff\s*;[^}]*background:\s*#fff",  "White text on white background",   "accessibility"),
    (r"font-size:\s*[0-9]+px",                      "Use rem/em instead of px for font sizes", "performance"),
    (r"position:\s*fixed.*z-index:\s*[0-9]{4,}",   "Very high z-index value",          "css"),
]

PYTHON_CHECKS = [
    (r"debug\s*=\s*True",                "Debug mode enabled — disable in production",  "security"),
    (r"secret_key\s*=\s*['\"][^'\"]{1,20}['\"]", "Weak secret key",                   "security"),
    (r"SELECT \* FROM",                  "Avoid SELECT * — specify columns",            "performance"),
    (r"except\s*:",                      "Bare except clause — catch specific exceptions", "python"),
    (r"print\(",                         "Remove print() statements in production",     "debug"),
    (r"password\s*=\s*['\"][^'\"]+['\"]","Hardcoded password detected",                "security"),
]

# ── Auto-fixers ───────────────────────────────────────────────────────────────
AUTO_FIXES = {
    # Add alt="" to img tags missing alt
    r"<img(?![^>]*alt=)([^>]*)>": r'<img alt=""\1>',
    # Fix HTTP script sources
    r'<script([^>]*)src=[\'"]http://': r'<script\1src="https://',
    # Fix debug mode
    r"debug\s*=\s*True": "debug=False",
}

PERFORMANCE_IMPROVEMENTS = [
    "Add loading='lazy' to images below the fold",
    "Minify CSS and JavaScript before deployment",
    "Use CSS variables for repeated color values",
    "Add will-change: transform to animated elements",
    "Use font-display: swap for Google Fonts",
    "Compress images to WebP format",
    "Add a service worker for caching",
]


class AIDebugger:
    """Detects and fixes issues in generated website code."""

    def __init__(self):
        self._openai = bool(os.environ.get("OPENAI_API_KEY"))

    def analyze(self, files: list[dict]) -> dict:
        """
        Analyze all project files for issues.
        files: [{"path": str, "code": str, "language": str}]
        Returns: {"issues": [...], "score": int, "suggestions": [...]}
        """
        issues      = []
        suggestions = list(PERFORMANCE_IMPROVEMENTS[:3])

        for f in files:
            path = f["path"]
            code = f["code"]
            lang = f.get("language", "")

            if lang == "html" or path.endswith(".html"):
                for pattern, message, category in HTML_CHECKS:
                    matches = re.findall(pattern, code, re.IGNORECASE)
                    if matches:
                        issues.append({
                            "file":     path,
                            "message":  message,
                            "category": category,
                            "severity": "warning" if category != "security" else "error",
                            "count":    len(matches),
                        })

            elif lang == "css" or path.endswith(".css"):
                for pattern, message, category in CSS_CHECKS:
                    if re.search(pattern, code, re.IGNORECASE):
                        issues.append({
                            "file":     path,
                            "message":  message,
                            "category": category,
                            "severity": "warning",
                            "count":    1,
                        })

            elif lang == "python" or path.endswith(".py"):
                for pattern, message, category in PYTHON_CHECKS:
                    matches = re.findall(pattern, code, re.IGNORECASE)
                    if matches:
                        issues.append({
                            "file":     path,
                            "message":  message,
                            "category": category,
                            "severity": "error" if category == "security" else "warning",
                            "count":    len(matches),
                        })

        # Calculate health score (100 - deductions)
        errors   = sum(1 for i in issues if i["severity"] == "error")
        warnings = sum(1 for i in issues if i["severity"] == "warning")
        score    = max(0, 100 - (errors * 15) - (warnings * 5))

        logger.info("Analyzed %d files: %d issues, score=%d", len(files), len(issues), score)
        return {
            "issues":      issues,
            "score":       score,
            "grade":       self._score_to_grade(score),
            "suggestions": suggestions,
            "errors":      errors,
            "warnings":    warnings,
        }

    def fix(self, files: list[dict]) -> list[dict]:
        """
        Auto-fix detected issues in all files.
        Returns the fixed files list.
        """
        fixed_files = []
        total_fixes = 0

        for f in files:
            code = f["code"]
            original = code

            # Apply auto-fixes
            for pattern, replacement in AUTO_FIXES.items():
                code, n = re.subn(pattern, replacement, code, flags=re.IGNORECASE)
                total_fixes += n

            fixed_files.append({**f, "code": code, "lines": code.count("\n") + 1})

        logger.info("Auto-fixed %d issues across %d files", total_fixes, len(files))
        return fixed_files

    def fix_with_ai(self, file_path: str, code: str, issue: str) -> str:
        """
        Use OpenAI to fix a specific issue in a file.
        Falls back to rule-based fix if OpenAI unavailable.
        """
        if not self._openai:
            # Apply rule-based fixes
            fixed = code
            for pattern, replacement in AUTO_FIXES.items():
                fixed = re.sub(pattern, replacement, fixed, flags=re.IGNORECASE)
            return fixed

        try:
            import openai
            client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            ext = file_path.rsplit(".", 1)[-1] if "." in file_path else "txt"
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{
                    "role": "user",
                    "content": (
                        f"Fix this {ext} code. Issue: {issue}\n\n"
                        f"Return ONLY the fixed code, no explanation:\n\n{code[:3000]}"
                    )
                }],
                temperature=0.1,
                max_tokens=2000,
            )
            fixed = response.choices[0].message.content.strip()
            # Strip markdown code blocks
            fixed = re.sub(r"^```\w*\n?", "", fixed)
            fixed = re.sub(r"\n?```$", "", fixed)
            return fixed
        except Exception as e:
            logger.warning("OpenAI fix failed: %s", e)
            return code

    def _score_to_grade(self, score: int) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"
