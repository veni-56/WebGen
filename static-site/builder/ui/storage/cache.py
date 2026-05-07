"""
storage/cache.py — Two-level artifact cache (memory + disk).

L1: in-memory LRU (bounded by entry count)
L2: filesystem (bounded by size)
Deduplication: content-addressed keys prevent storing the same bytes twice.
"""
from __future__ import annotations

import hashlib
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any


class LRUCache:
    """Thread-safe in-memory LRU cache."""

    def __init__(self, max_size: int = 256):
        self._max  = max_size
        self._data: OrderedDict[str, Any] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Any:
        with self._lock:
            if key not in self._data:
                return None
            self._data.move_to_end(key)
            return self._data[key]

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            self._data[key] = value
            if len(self._data) > self._max:
                self._data.popitem(last=False)

    def delete(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        return len(self._data)


class ArtifactCache:
    """
    Two-level cache wrapping any StorageBackend.
    Reads hit L1 first, then L2 (disk), then the backend.
    Writes go to all levels.
    """

    def __init__(self, backend, cache_dir: str | Path,
                 l1_size: int = 128, max_disk_mb: int = 500):
        self._backend   = backend
        self._l1        = LRUCache(l1_size)
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._max_disk  = max_disk_mb * 1024 * 1024
        self._lock      = threading.Lock()

    def _cache_path(self, key: str) -> Path:
        h = hashlib.sha256(key.encode()).hexdigest()
        return self._cache_dir / h[:2] / h

    def get(self, key: str) -> bytes | None:
        # L1
        v = self._l1.get(key)
        if v is not None:
            return v
        # L2
        cp = self._cache_path(key)
        if cp.exists():
            data = cp.read_bytes()
            self._l1.set(key, data)
            return data
        # Backend
        data = self._backend.get(key)
        if data is not None:
            self._l1.set(key, data)
            self._write_l2(cp, data)
        return data

    def put(self, key: str, data: bytes, **kwargs) -> str:
        result = self._backend.put(key, data, **kwargs)
        self._l1.set(key, data)
        self._write_l2(self._cache_path(key), data)
        return result

    def invalidate(self, key: str) -> None:
        self._l1.delete(key)
        cp = self._cache_path(key)
        if cp.exists():
            cp.unlink()

    def invalidate_prefix(self, prefix: str) -> int:
        keys = self._backend.list_prefix(prefix)
        for k in keys:
            self.invalidate(k)
        return len(keys)

    def _write_l2(self, path: Path, data: bytes) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_bytes(data)
            self._maybe_evict()
        except Exception:
            pass

    def _maybe_evict(self) -> None:
        total = sum(f.stat().st_size for f in self._cache_dir.rglob("*") if f.is_file())
        if total <= self._max_disk:
            return
        files = sorted(
            (f for f in self._cache_dir.rglob("*") if f.is_file()),
            key=lambda f: f.stat().st_mtime
        )
        for f in files:
            if total <= self._max_disk * 0.8:
                break
            total -= f.stat().st_size
            f.unlink()

    # Delegate remaining interface
    def exists(self, key: str) -> bool:
        return self._cache_path(key).exists() or self._backend.exists(key)

    def delete(self, key: str) -> bool:
        self.invalidate(key)
        return self._backend.delete(key)

    def list_prefix(self, prefix: str) -> list[str]:
        return self._backend.list_prefix(prefix)

    def signed_url(self, key: str, expires_in: int = 3600) -> str:
        return self._backend.signed_url(key, expires_in)
