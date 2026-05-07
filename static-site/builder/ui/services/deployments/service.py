"""services/deployments/service.py — Deployment domain service."""
from __future__ import annotations
from services.base import BaseService


class DeploymentService(BaseService):
    service_name = "deployments"

    def deploy(self, project_id: str, provider: str,
               build_dir: str, project_name: str,
               user_id: str = "") -> dict:
        from pathlib import Path
        from deploy.providers import get_provider
        p      = get_provider(provider)
        errors = p.validate(Path(build_dir))
        if errors:
            return {"ok": False, "errors": errors}
        result = p.deploy(Path(build_dir), project_name)
        if result.get("ok"):
            self._emit("deployment.finished", {
                "project_id": project_id, "provider": provider,
                "url": result.get("url"), "user_id": user_id,
            })
        return result

    def rollback(self, provider: str, deployment_id: str) -> dict:
        from deploy.providers import get_provider
        return get_provider(provider).rollback(deployment_id)
