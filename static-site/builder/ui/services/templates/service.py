"""services/templates/service.py — Template marketplace domain service."""
from __future__ import annotations
from services.base import BaseService


class TemplateService(BaseService):
    service_name = "templates"

    def publish(self, author_id: str, name: str, slug: str,
                template: dict, **meta) -> str:
        from templates_marketplace.registry import TemplateRegistry
        tid = TemplateRegistry(self._conn).publish(author_id, name, slug, template, **meta)
        self._emit("template.published", {"template_id": tid, "author_id": author_id, "name": name})
        return tid

    def install(self, slug: str, current_cfg: dict) -> dict:
        from templates_marketplace.registry import TemplateRegistry
        from marketplace.template import TemplateMarketplace
        reg  = TemplateRegistry(self._conn)
        tpl  = reg.get(slug)
        if not tpl:
            return {"ok": False, "error": "Template not found"}
        new_cfg = TemplateMarketplace.importTemplate(tpl["template"], current_cfg)
        reg.record_install(tpl["id"])
        self._emit("template.installed", {"slug": slug})
        return {"ok": True, "config": new_cfg}

    def search(self, query: str = "", category: str = "",
               limit: int = 20) -> list[dict]:
        from templates_marketplace.registry import TemplateRegistry
        return TemplateRegistry(self._conn).search(query, category, limit)

    def rate(self, slug: str, user_id: str, rating: int, review: str = "") -> None:
        from templates_marketplace.registry import TemplateRegistry
        reg = TemplateRegistry(self._conn)
        tpl = reg.get(slug)
        if tpl:
            reg.rate(tpl["id"], user_id, rating, review)
