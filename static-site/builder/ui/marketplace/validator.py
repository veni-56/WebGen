"""
marketplace/validator.py — Plugin manifest validation.

Validates plugin manifests against the required schema.
Also verifies plugin signatures (HMAC-SHA256).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any

# Manifest schema
MANIFEST_SCHEMA = {
    "id":          {"type": str,  "required": True,  "pattern": r"^[a-z][a-z0-9_-]{1,60}$"},
    "name":        {"type": str,  "required": True,  "max_len": 120},
    "version":     {"type": str,  "required": True,  "pattern": r"^\d+\.\d+\.\d+$"},
    "author":      {"type": str,  "required": False, "max_len": 120},
    "description": {"type": str,  "required": False, "max_len": 500},
    "permissions": {"type": list, "required": False},
    "dependencies":{"type": list, "required": False},
    "hooks":       {"type": list, "required": False},
    "settings":    {"type": dict, "required": False},
    "entry":       {"type": str,  "required": False},
}

ALLOWED_PERMISSIONS = {
    "read:config", "write:config",
    "read:pages",  "write:pages",
    "read:uploads","write:uploads",
    "inject:head", "inject:body",
    "network:outbound",
}

ALLOWED_HOOKS = {
    "beforeBuild", "afterBuild",
    "beforeRender", "afterRender",
    "beforePublish", "afterPublish",
    "beforeSave", "afterSave",
    "onError",
}

# HMAC secret — override via env in production
_SIGN_SECRET = b"wbs-plugin-signing-secret"


def validate_manifest(manifest: Any) -> list[str]:
    """
    Validate a plugin manifest dict.
    Returns list of error strings (empty = valid).
    """
    errors: list[str] = []

    if not isinstance(manifest, dict):
        return ["Manifest must be a JSON object"]

    for field, rules in MANIFEST_SCHEMA.items():
        value = manifest.get(field)
        if rules["required"] and (value is None or value == ""):
            errors.append(f'"{field}" is required')
            continue
        if value is None:
            continue
        if not isinstance(value, rules["type"]):
            errors.append(f'"{field}" must be {rules["type"].__name__}')
            continue
        if "pattern" in rules and isinstance(value, str):
            if not re.match(rules["pattern"], value):
                errors.append(f'"{field}" does not match pattern {rules["pattern"]}')
        if "max_len" in rules and isinstance(value, str):
            if len(value) > rules["max_len"]:
                errors.append(f'"{field}" exceeds max length {rules["max_len"]}')

    # Validate permissions
    for perm in manifest.get("permissions", []):
        if perm not in ALLOWED_PERMISSIONS:
            errors.append(f'Unknown permission: "{perm}". Allowed: {sorted(ALLOWED_PERMISSIONS)}')

    # Validate hooks
    for hook in manifest.get("hooks", []):
        if hook not in ALLOWED_HOOKS:
            errors.append(f'Unknown hook: "{hook}". Allowed: {sorted(ALLOWED_HOOKS)}')

    # Validate dependencies format
    for dep in manifest.get("dependencies", []):
        if isinstance(dep, str):
            if not re.match(r"^[a-z][a-z0-9_-]{1,60}$", dep):
                errors.append(f'Invalid dependency id: "{dep}"')
        elif isinstance(dep, dict):
            if "id" not in dep:
                errors.append('Dependency object must have "id"')
        else:
            errors.append(f"Dependency must be string or object, got {type(dep).__name__}")

    return errors


def sign_manifest(manifest: dict) -> str:
    """Generate an HMAC-SHA256 signature for a manifest."""
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return hmac.new(_SIGN_SECRET, canonical.encode(), hashlib.sha256).hexdigest()


def verify_signature(manifest: dict, signature: str) -> bool:
    """Verify a manifest signature. Returns True if valid."""
    expected = sign_manifest(manifest)
    return hmac.compare_digest(expected, signature)
