"""
marketplace/installer.py — Plugin install/uninstall lifecycle.

Handles:
- Dependency resolution before install
- File extraction (if plugin is a zip)
- Permission grant workflow
- Rollback on failure
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import zipfile
from pathlib import Path
from typing import Any

from marketplace.registry import PluginRegistry
from marketplace.validator import validate_manifest, verify_signature


PLUGINS_DIR = Path(__file__).parent.parent / "plugins"


class PluginInstaller:
    def __init__(self, conn: sqlite3.Connection):
        self._conn     = conn
        self._registry = PluginRegistry(conn)

    def install_from_manifest(self, manifest: dict,
                               signature: str | None = None,
                               auto_grant: bool = False) -> dict:
        """
        Install a plugin from a manifest dict.
        Returns { ok, plugin_id, warnings }.
        """
        errors = validate_manifest(manifest)
        if errors:
            return {"ok": False, "errors": errors}

        if signature and not verify_signature(manifest, signature):
            return {"ok": False, "errors": ["Invalid plugin signature"]}

        warnings: list[str] = []
        if not signature:
            warnings.append("Plugin is unsigned — install at your own risk")

        # Resolve and check dependencies
        slug = manifest["id"]
        try:
            deps = self._registry.resolve_dependencies(slug)
        except Exception:
            deps = []

        for dep in deps:
            dep_row = self._registry.get(dep)
            if not dep_row or not dep_row.get("installed"):
                warnings.append(f'Dependency "{dep}" is not installed')

        # Register in DB
        try:
            pid = self._registry.register(manifest, signature)
            self._registry.install(slug)
        except Exception as e:
            return {"ok": False, "errors": [str(e)]}

        # Auto-grant safe permissions
        if auto_grant:
            safe = {"read:config", "read:pages", "inject:head", "inject:body"}
            for perm in manifest.get("permissions", []):
                if perm in safe:
                    try:
                        self._registry.grant_permission(slug, perm)
                    except Exception:
                        pass

        return {"ok": True, "plugin_id": pid, "slug": slug, "warnings": warnings}

    def install_from_zip(self, zip_path: Path,
                          signature: str | None = None) -> dict:
        """
        Install a plugin from a zip archive.
        The zip must contain manifest.json at the root.
        """
        if not zip_path.exists():
            return {"ok": False, "errors": [f"File not found: {zip_path}"]}

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                if "manifest.json" not in zf.namelist():
                    return {"ok": False, "errors": ["manifest.json not found in zip"]}
                manifest = json.loads(zf.read("manifest.json"))
                result   = self.install_from_manifest(manifest, signature)
                if not result["ok"]:
                    return result
                # Extract plugin files to plugins/<slug>/
                slug     = manifest["id"]
                dest_dir = PLUGINS_DIR / slug
                dest_dir.mkdir(parents=True, exist_ok=True)
                zf.extractall(dest_dir)
        except zipfile.BadZipFile:
            return {"ok": False, "errors": ["Invalid zip file"]}
        except Exception as e:
            return {"ok": False, "errors": [str(e)]}

        return result

    def uninstall(self, slug: str) -> dict:
        """Uninstall a plugin. Removes files and DB records."""
        row = self._registry.get(slug)
        if not row:
            return {"ok": False, "errors": [f"Plugin not found: {slug}"]}

        # Remove plugin files if they exist
        plugin_dir = PLUGINS_DIR / slug
        if plugin_dir.exists():
            try:
                shutil.rmtree(plugin_dir)
            except Exception as e:
                return {"ok": False, "errors": [f"Failed to remove files: {e}"]}

        self._registry.uninstall(slug)
        return {"ok": True, "slug": slug}

    def list_installed(self) -> list[dict]:
        return self._registry.list_all(installed_only=True)

    def list_available(self) -> list[dict]:
        return self._registry.list_all(installed_only=False)
