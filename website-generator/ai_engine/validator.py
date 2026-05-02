"""
ai_engine/validator.py — Response Validator
Ensures generated code output is valid and complete before delivery.
"""
import re
from utils.logger import get_logger

logger = get_logger("ai_engine.validator")


class ValidationError(Exception):
    pass


class ResponseValidator:
    """
    Validates generated project files for completeness and correctness.
    """

    # Minimum line counts per file type
    MIN_LINES = {
        "html":       20,
        "css":        30,
        "js":         10,
        "py":         20,
        "txt":         3,
    }

    # Required patterns per project type
    REQUIRED_PATTERNS = {
        "static": {
            "index.html": [r"<!DOCTYPE html>", r"<html", r"</html>"],
            "style.css":  [r":root\s*\{", r"body\s*\{"],
            "script.js":  [r"function\s+\w+|addEventListener|document\."],
        },
        "flask": {
            "app.py": [r"from flask import", r"@app\.route", r"if __name__"],
            "templates/base.html": [r"<!DOCTYPE html>", r"block content"],
        },
        "ecommerce": {
            "app.py": [r"from flask import", r"@app\.route.*dashboard",
                       r"@app\.route.*product"],
        },
        "blog": {
            "app.py": [r"from flask import", r"@app\.route.*admin",
                       r"@app\.route.*post"],
        },
        "startup": {
            "app.py": [r"from flask import", r"waitlist"],
        },
    }

    def validate(self, files: list[dict], project_type: str) -> dict:
        """
        Validate a list of generated files.
        files: [{"path": str, "code": str, "language": str, "lines": int}]
        Returns {"valid": bool, "errors": [...], "warnings": [...]}
        """
        errors   = []
        warnings = []

        if not files:
            errors.append("No files were generated.")
            return {"valid": False, "errors": errors, "warnings": warnings}

        file_map = {f["path"]: f for f in files}

        # Check minimum line counts
        for f in files:
            ext = f["path"].rsplit(".", 1)[-1].lower() if "." in f["path"] else ""
            min_lines = self.MIN_LINES.get(ext, 0)
            if f["lines"] < min_lines:
                warnings.append(
                    f"{f['path']}: only {f['lines']} lines (expected ≥{min_lines})"
                )

        # Check required patterns
        patterns = self.REQUIRED_PATTERNS.get(project_type, {})
        for filepath, required in patterns.items():
            if filepath not in file_map:
                warnings.append(f"Expected file missing: {filepath}")
                continue
            code = file_map[filepath]["code"]
            for pattern in required:
                if not re.search(pattern, code, re.IGNORECASE):
                    warnings.append(
                        f"{filepath}: missing expected pattern '{pattern}'"
                    )

        # Check for placeholder text
        placeholder_patterns = [
            r"\[YOUR_\w+\]",
            r"TODO:",
            r"FIXME:",
            r"placeholder_\w+",
        ]
        for f in files:
            for pat in placeholder_patterns:
                if re.search(pat, f["code"]):
                    warnings.append(f"{f['path']}: contains placeholder text")
                    break

        # Check HTML files have proper structure
        for f in files:
            if f["path"].endswith(".html") and "base.html" not in f["path"]:
                code = f["code"]
                if "<!DOCTYPE" not in code and "extends" not in code:
                    warnings.append(f"{f['path']}: missing DOCTYPE declaration")

        valid = len(errors) == 0
        if not valid:
            logger.error("Validation failed: %s", errors)
        elif warnings:
            logger.warning("Validation warnings for %s: %s", project_type, warnings)
        else:
            logger.info("Validation passed for %s (%d files)", project_type, len(files))

        return {"valid": valid, "errors": errors, "warnings": warnings}

    def validate_config(self, config: dict) -> tuple[bool, str]:
        """
        Validate a generation config dict.
        Returns (valid: bool, error_message: str)
        """
        required = ["project_type", "website_type"]
        for field in required:
            if not config.get(field):
                return False, f"Missing required config field: {field}"

        valid_types = {"static", "flask", "ecommerce", "startup", "blog", "portfolio_adv"}
        if config["project_type"] not in valid_types:
            return False, f"Invalid project_type: {config['project_type']}"

        valid_wtypes = {"portfolio", "business", "ecommerce", "blog"}
        if config["website_type"] not in valid_wtypes:
            return False, f"Invalid website_type: {config['website_type']}"

        # Validate color format
        for color_field in ("primary_color", "secondary_color"):
            color = config.get(color_field, "")
            if color and not re.match(r"^#[0-9a-fA-F]{6}$", color):
                return False, f"Invalid color format for {color_field}: {color}"

        return True, ""
