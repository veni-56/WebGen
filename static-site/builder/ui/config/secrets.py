"""
config/secrets.py — Encrypted secrets management.

Secrets are stored encrypted at rest using Fernet symmetric encryption.
Falls back to plaintext env vars if cryptography is not installed.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path


_SECRETS_FILE = Path(os.environ.get("SECRETS_FILE", "./secrets.enc"))
_KEY_ENV      = "SECRETS_KEY"


def _derive_key(password: str) -> bytes:
    """Derive a 32-byte key from a password using PBKDF2."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), b"wbs-secrets-salt", 100_000)
    return base64.urlsafe_b64encode(dk)


class SecretsManager:
    def __init__(self, key: str | None = None):
        self._key     = key or os.environ.get(_KEY_ENV, "")
        self._secrets: dict[str, str] = {}
        self._fernet  = None
        if self._key:
            self._init_fernet()
        self._load()

    def _init_fernet(self) -> None:
        try:
            from cryptography.fernet import Fernet
            self._fernet = Fernet(_derive_key(self._key))
        except ImportError:
            pass

    def _load(self) -> None:
        if not _SECRETS_FILE.exists():
            return
        try:
            data = _SECRETS_FILE.read_bytes()
            if self._fernet:
                data = self._fernet.decrypt(data)
            self._secrets = json.loads(data)
        except Exception:
            self._secrets = {}

    def _save(self) -> None:
        data = json.dumps(self._secrets).encode()
        if self._fernet:
            data = self._fernet.encrypt(data)
        _SECRETS_FILE.write_bytes(data)

    def get(self, key: str, default: str = "") -> str:
        # Env var takes precedence
        env_val = os.environ.get(key)
        if env_val:
            return env_val
        return self._secrets.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._secrets[key] = value
        self._save()

    def delete(self, key: str) -> None:
        self._secrets.pop(key, None)
        self._save()

    def list_keys(self) -> list[str]:
        return list(self._secrets.keys())


secrets = SecretsManager()
