"""services/plugins/service.py — Plugin domain service."""
from __future__ import annotations
from services.base import BaseService


class PluginService(BaseService):
    service_name = "plugins"

    def install(self, manifest: dict, signature: str | None = None,
                user_id: str = "", org_id: str = "") -> dict:
        from marketplace.installer import PluginInstaller
        result = PluginInstaller(self._conn).install_from_manifest(manifest, signature)
        if result.get("ok"):
            self._emit("plugin.installed", {
                "slug": manifest.get("id"), "user_id": user_id, "org_id": org_id,
            })
        return result

    def uninstall(self, slug: str, user_id: str = "") -> dict:
        from marketplace.installer import PluginInstaller
        result = PluginInstaller(self._conn).uninstall(slug)
        if result.get("ok"):
            self._emit("plugin.uninstalled", {"slug": slug, "user_id": user_id})
        return result

    def list_installed(self) -> list[dict]:
        from marketplace.installer import PluginInstaller
        return PluginInstaller(self._conn).list_installed()
