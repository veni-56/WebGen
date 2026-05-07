"""
storage/filesystem.py — Local filesystem storage backend.

Implements the StorageBackend interface for local disk.
Artifacts are content-addressed (SHA-256 hash of content).
Immutable: once written, a file is never overwritten.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import shutil
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


# ── Backend interface ─────────────────────────────────────────────────────────

class StorageBackend(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Store data under key. Returns the canonical storage key."""

    @abstractmethod
    def get(self, key: str) -> bytes | None:
        """Retrieve data by key. Returns None if not found."""

    @abstractmethod
    def exists(self, key: str) -> bool: ...

    @abstractmethod
    def delete(self, key: str) -> bool: ...

    @abstractmethod
    def list_prefix(self, prefix: str) -> list[str]: ...

    @abstractmethod
    def signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Return a URL (possibly signed) for direct access."""

    def put_file(self, key: str, path: Path) -> str:
        return self.put(key, path.read_bytes())

    def content_key(self, data: bytes) -> str:
        """Content-addressed key: sha256 of data."""
        return hashlib.sha256(data).hexdigest()


# ── Filesystem backend ────────────────────────────────────────────────────────

class FilesystemBackend(StorageBackend):
    """
    Local filesystem storage.
    Layout: <root>/<prefix>/<key>
    Content-addressed artifacts go under <root>/cas/<sha256[:2]>/<sha256>
    """

    def __init__(self, root: str | Path):
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # Sanitize key to prevent path traversal
        safe = key.replace("..", "").lstrip("/\\")
        return self._root / safe

    def put(self, key: str, data: bytes,
            content_type: str = "application/octet-stream") -> str:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():   # immutable: never overwrite
            p.write_bytes(data)
        return key

    def put_immutable(self, data: bytes) -> str:
        """Store with content-addressed key. Returns the key."""
        key = f"cas/{hashlib.sha256(data).hexdigest()[:2]}/{hashlib.sha256(data).hexdigest()}"
        self.put(key, data)
        return key

    def get(self, key: str) -> bytes | None:
        p = self._path(key)
        return p.read_bytes() if p.exists() else None

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def delete(self, key: str) -> bool:
        p = self._path(key)
        if p.exists():
            p.unlink()
            return True
        return False

    def list_prefix(self, prefix: str) -> list[str]:
        base = self._path(prefix)
        if not base.exists():
            return []
        return [
            str(f.relative_to(self._root)).replace("\\", "/")
            for f in base.rglob("*") if f.is_file()
        ]

    def signed_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate a signed URL for local serving.
        Format: /storage/<key>?sig=<hmac>&exp=<ts>
        """
        exp = int(time.time()) + expires_in
        sig = _sign_url(key, exp)
        return f"/storage/{key}?sig={sig}&exp={exp}"

    def copy_dir(self, src: Path, dest_prefix: str) -> list[str]:
        """Copy a directory tree into storage. Returns list of keys."""
        keys = []
        for f in src.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(src)).replace("\\", "/")
                key = f"{dest_prefix}/{rel}"
                self.put(key, f.read_bytes())
                keys.append(key)
        return keys


# ── URL signing ───────────────────────────────────────────────────────────────

_SIGN_SECRET = os.environ.get("STORAGE_SIGN_SECRET", "wbs-storage-secret").encode()


def _sign_url(key: str, exp: int) -> str:
    msg = f"{key}:{exp}".encode()
    return hmac.new(_SIGN_SECRET, msg, hashlib.sha256).hexdigest()[:16]


def verify_signed_url(key: str, sig: str, exp: str) -> bool:
    try:
        exp_int = int(exp)
        if time.time() > exp_int:
            return False
        return hmac.compare_digest(_sign_url(key, exp_int), sig)
    except Exception:
        return False
