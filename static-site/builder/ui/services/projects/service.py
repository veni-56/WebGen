"""services/projects/service.py — Project domain service."""
from __future__ import annotations
from services.base import BaseService, ServiceError


class ProjectService(BaseService):
    service_name = "projects"

    def create(self, user_id: str, org_id: str, ws_id: str | None,
               name: str, config: dict) -> dict:
        from db.repositories import ProjectRepository, AuditRepository
        from db.connection import transaction
        slug = name.lower().replace(" ", "-")
        with transaction(self._conn):
            pid = ProjectRepository(self._conn).create(
                user_id, org_id, ws_id, name, slug, config
            )
            AuditRepository(self._conn).log(
                org_id, user_id, "project.create", "project", pid
            )
        self._emit("project.created", {
            "project_id": pid, "user_id": user_id,
            "org_id": org_id, "name": name,
        })
        self._log("PROJECT_CREATE", {"pid": pid, "name": name})
        return {"id": pid, "name": name, "slug": slug}

    def update(self, pid: str, user_id: str, **fields) -> bool:
        from db.repositories import ProjectRepository
        changed = ProjectRepository(self._conn).update(pid, **fields)
        if changed:
            self._emit("project.updated", {"project_id": pid, "user_id": user_id, "fields": list(fields)})
        return changed

    def delete(self, pid: str, user_id: str, org_id: str) -> None:
        from db.repositories import ProjectRepository, AuditRepository
        from db.connection import transaction
        with transaction(self._conn):
            ProjectRepository(self._conn).delete(pid)
            AuditRepository(self._conn).log(org_id, user_id, "project.delete", "project", pid)
        self._emit("project.deleted", {"project_id": pid, "user_id": user_id})

    def get(self, pid: str) -> dict | None:
        from db.repositories import ProjectRepository
        return ProjectRepository(self._conn).find_by_id(pid)

    def list_for_workspace(self, ws_id: str, limit: int = 50) -> list[dict]:
        from db.repositories import ProjectRepository
        projects = ProjectRepository(self._conn).list_for_workspace(ws_id, limit)
        for p in projects:
            p.pop("config", None)
        return projects
