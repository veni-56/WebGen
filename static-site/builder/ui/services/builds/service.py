"""services/builds/service.py — Build domain service."""
from __future__ import annotations
from services.base import BaseService


class BuildService(BaseService):
    service_name = "builds"

    def enqueue_publish(self, project_id: str, config: dict,
                        user_id: str = "") -> str:
        from worker import JobQueue
        jid = JobQueue.enqueue("publish", {"cfg": config, "pid": project_id}, priority=10)
        self._emit("build.started", {
            "job_id": jid, "project_id": project_id,
            "kind": "publish", "user_id": user_id,
        })
        self._log("BUILD_ENQUEUE", {"jid": jid, "pid": project_id, "kind": "publish"})
        return jid

    def enqueue_preview(self, project_id: str, config: dict,
                        page: str = "home") -> str:
        from worker import JobQueue
        jid = JobQueue.enqueue("preview", {"cfg": config, "pid": project_id, "page": page}, priority=5)
        self._emit("build.started", {"job_id": jid, "project_id": project_id, "kind": "preview"})
        return jid

    def get_status(self, job_id: str) -> dict | None:
        from worker import JobQueue
        job = JobQueue.get_job(job_id)
        if not job:
            return None
        if job.get("status") == "done":
            self._emit("build.completed", {
                "job_id": job_id,
                "result": job.get("result", {}),
            })
        return {"status": job["status"], "result": job.get("result"), "error": job.get("error")}

    def queue_stats(self) -> dict:
        from worker import JobQueue
        return JobQueue.queue_stats()
