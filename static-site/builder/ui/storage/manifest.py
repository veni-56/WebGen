"""
storage/manifest.py — Artifact manifest system.

A manifest maps logical artifact names to their storage keys.
Enables deduplication: if two builds produce identical files,
they share the same storage key.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ArtifactEntry:
    name:         str
    key:          str          # storage key (content-addressed)
    size:         int = 0
    content_type: str = "application/octet-stream"
    hash:         str = ""     # sha256 of content
    meta:         dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"name": self.name, "key": self.key, "size": self.size,
                "content_type": self.content_type, "hash": self.hash, "meta": self.meta}


@dataclass
class BuildArtifactManifest:
    build_id:   str
    project_id: str
    version:    str = "1"
    created_at: float = field(default_factory=time.time)
    artifacts:  list[ArtifactEntry] = field(default_factory=list)
    meta:       dict = field(default_factory=dict)

    def add(self, name: str, data: bytes, storage: Any,
            content_type: str = "application/octet-stream") -> ArtifactEntry:
        h   = hashlib.sha256(data).hexdigest()
        key = f"artifacts/{h[:2]}/{h}"
        storage.put(key, data, content_type=content_type)
        entry = ArtifactEntry(name=name, key=key, size=len(data),
                              content_type=content_type, hash=h)
        self.artifacts.append(entry)
        return entry

    def get_entry(self, name: str) -> ArtifactEntry | None:
        return next((a for a in self.artifacts if a.name == name), None)

    def to_dict(self) -> dict:
        return {
            "build_id":   self.build_id,
            "project_id": self.project_id,
            "version":    self.version,
            "created_at": self.created_at,
            "artifacts":  [a.to_dict() for a in self.artifacts],
            "meta":       self.meta,
        }

    def save(self, storage: Any) -> str:
        """Persist manifest JSON to storage. Returns storage key."""
        key  = f"manifests/{self.build_id}.json"
        data = json.dumps(self.to_dict(), indent=2).encode()
        storage.put(key, data, content_type="application/json")
        return key

    @classmethod
    def load(cls, build_id: str, storage: Any) -> "BuildArtifactManifest | None":
        key  = f"manifests/{build_id}.json"
        data = storage.get(key)
        if not data:
            return None
        d = json.loads(data)
        m = cls(build_id=d["build_id"], project_id=d["project_id"],
                version=d.get("version","1"), created_at=d.get("created_at",0),
                meta=d.get("meta",{}))
        m.artifacts = [ArtifactEntry(**a) for a in d.get("artifacts",[])]
        return m


# ── Storage registry ──────────────────────────────────────────────────────────

class StorageRegistry:
    """Registry of named storage backends."""

    def __init__(self):
        self._backends: dict[str, Any] = {}
        self._default:  str | None     = None

    def register(self, name: str, backend: Any, default: bool = False) -> None:
        self._backends[name] = backend
        if default or self._default is None:
            self._default = name

    def get(self, name: str | None = None) -> Any:
        key = name or self._default
        if not key or key not in self._backends:
            raise KeyError(f"Storage backend '{key}' not registered")
        return self._backends[key]

    def list(self) -> list[str]:
        return list(self._backends)


storage_registry = StorageRegistry()
