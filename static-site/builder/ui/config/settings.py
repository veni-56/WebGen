"""
config/settings.py — Runtime configuration with hot-reload and feature flags.

Settings are loaded from environment variables and .env files.
Feature flags can be toggled at runtime without restart.
"""
from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any


class Settings:
    """
    Centralized settings store.
    Reads from environment variables with typed defaults.
    Supports runtime override and feature flags.
    """

    def __init__(self):
        self._overrides: dict[str, Any] = {}
        self._flags:     dict[str, bool] = {}
        self._lock       = threading.RLock()
        self._load_env()

    def _load_env(self) -> None:
        try:
            from dotenv import load_dotenv
            load_dotenv(Path(__file__).parent.parent / ".env")
        except ImportError:
            pass

    # ── Typed getters ─────────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            if key in self._overrides:
                return self._overrides[key]
        return os.environ.get(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        try:
            return int(self.get(key, default))
        except (TypeError, ValueError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        v = self.get(key, str(default))
        return str(v).lower() in ("1", "true", "yes", "on")

    def get_list(self, key: str, sep: str = ",", default: list | None = None) -> list:
        v = self.get(key, "")
        if not v:
            return default or []
        return [x.strip() for x in str(v).split(sep) if x.strip()]

    # ── Runtime override ──────────────────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._overrides[key] = value

    def unset(self, key: str) -> None:
        with self._lock:
            self._overrides.pop(key, None)

    def reload(self) -> None:
        """Reload from .env file."""
        self._load_env()

    # ── Feature flags ─────────────────────────────────────────────────────────

    def flag(self, name: str, default: bool = False) -> bool:
        with self._lock:
            if name in self._flags:
                return self._flags[name]
        return self.get_bool(f"FLAG_{name.upper()}", default)

    def set_flag(self, name: str, value: bool) -> None:
        with self._lock:
            self._flags[name] = value

    def all_flags(self) -> dict[str, bool]:
        with self._lock:
            return dict(self._flags)

    # ── Common settings ───────────────────────────────────────────────────────

    @property
    def db_path(self) -> str:
        return self.get("DB_PATH", "./projects.db")

    @property
    def secret_key(self) -> str:
        return self.get("SECRET_KEY", "dev-secret-change-me")

    @property
    def port(self) -> int:
        return self.get_int("PORT", 4000)

    @property
    def debug(self) -> bool:
        return self.get_bool("FLASK_DEBUG", False)

    @property
    def worker_count(self) -> int:
        return self.get_int("WORKER_COUNT", 2)

    @property
    def uploads_dir(self) -> str:
        return self.get("UPLOADS_DIR", "./uploads")

    @property
    def publish_dir(self) -> str:
        return self.get("PUBLISH_DIR", "./published")

    @property
    def log_dir(self) -> str:
        return self.get("LOG_DIR", "./logs")


settings = Settings()
