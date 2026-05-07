"""orchestrator/artifacts.py — Artifact management for build outputs."""
from __future__ import annotations
from pathlib import Path


class ArtifactManager:
    def __init__(self, storage=None):
        self._storage = storage

    def _store(self):
        if self._storage:
            return self._storage
        from storage.manifest import storage_registry
        try:
            return storage_registry.get()
        except KeyError:
            from storage.filesystem import FilesystemBackend
            import os
            root = Path(os.environ.get("PUBLISH_DIR", "./published")) / "_artifacts"
            return FilesystemBackend(root)

    def store_build(self, build_id: str, build_dir: Path) -> dict:
        store   = self._store()
        keys    = []
        for f in build_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(build_dir)).replace("\\", "/")
                key = f"builds/{build_id}/{rel}"
                store.put(key, f.read_bytes())
                keys.append(key)
        return {"build_id": build_id, "files": len(keys), "keys": keys}

    def get_url(self, key: str, expires_in: int = 3600) -> str:
        return self._store().signed_url(key, expires_in)

    def list_build(self, build_id: str) -> list[str]:
        return self._store().list_prefix(f"builds/{build_id}/")


artifact_manager = ArtifactManager()
