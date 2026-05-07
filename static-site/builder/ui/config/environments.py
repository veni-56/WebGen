"""
config/environments.py — Environment profiles (dev, staging, production).

Each environment has its own config overrides.
The active environment is set via the ENV environment variable.
"""
from __future__ import annotations

import os
from typing import Any


PROFILES: dict[str, dict[str, Any]] = {
    "development": {
        "FLASK_DEBUG":   "1",
        "LOG_LEVEL":     "debug",
        "WORKER_COUNT":  "1",
        "FLAG_ANALYTICS": False,
        "FLAG_WEBHOOKS":  False,
    },
    "staging": {
        "FLASK_DEBUG":   "0",
        "LOG_LEVEL":     "info",
        "WORKER_COUNT":  "2",
        "FLAG_ANALYTICS": True,
        "FLAG_WEBHOOKS":  True,
    },
    "production": {
        "FLASK_DEBUG":   "0",
        "LOG_LEVEL":     "warning",
        "WORKER_COUNT":  "4",
        "FLAG_ANALYTICS": True,
        "FLAG_WEBHOOKS":  True,
        "FLAG_RATE_LIMIT": True,
    },
}


class EnvironmentManager:
    def __init__(self):
        self._env = os.environ.get("ENV", "development").lower()

    @property
    def name(self) -> str:
        return self._env

    @property
    def is_production(self) -> bool:
        return self._env == "production"

    @property
    def is_development(self) -> bool:
        return self._env == "development"

    def get(self, key: str, default: Any = None) -> Any:
        profile = PROFILES.get(self._env, {})
        return profile.get(key, os.environ.get(key, default))

    def apply(self) -> None:
        """Apply environment profile to os.environ (only if not already set)."""
        profile = PROFILES.get(self._env, {})
        for k, v in profile.items():
            if k not in os.environ and not k.startswith("FLAG_"):
                os.environ[k] = str(v)
        # Apply feature flags
        try:
            from config.settings import settings
            for k, v in profile.items():
                if k.startswith("FLAG_"):
                    settings.set_flag(k[5:].lower(), bool(v))
        except Exception:
            pass

    def profile(self) -> dict:
        return PROFILES.get(self._env, {})


env_manager = EnvironmentManager()
