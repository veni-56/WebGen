"""
orchestrator/scheduler.py — Build orchestration scheduler.

Schedules build manifests for execution.
Tracks build state and integrates with the event bus.
"""
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BuildJob:
    id:         str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    project_id: str = ""
    manifest_id: str = ""
    status:     str = "pending"   # pending|running|done|failed
    result:     dict = field(default_factory=dict)
    error:      str = ""
    created_at: float = field(default_factory=time.time)
    started_at: float = 0.0
    finished_at: float = 0.0

    @property
    def duration_ms(self) -> float:
        if self.finished_at and self.started_at:
            return round((self.finished_at - self.started_at) * 1000, 1)
        return 0.0


class BuildScheduler:
    MAX_JOBS = 500

    def __init__(self):
        self._jobs:  dict[str, BuildJob] = {}
        self._lock   = threading.Lock()
        self._pool   = None

    def _executor(self):
        if self._pool is None:
            import concurrent.futures
            self._pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=4, thread_name_prefix="build"
            )
        return self._pool

    def submit(self, manifest, context: dict | None = None) -> BuildJob:
        """Submit a manifest for async execution. Returns a BuildJob."""
        job = BuildJob(project_id=manifest.project_id, manifest_id=manifest.id)
        with self._lock:
            if len(self._jobs) >= self.MAX_JOBS:
                # Evict oldest finished jobs
                finished = sorted(
                    [j for j in self._jobs.values() if j.status in ("done","failed")],
                    key=lambda j: j.created_at
                )
                for old in finished[:50]:
                    del self._jobs[old.id]
            self._jobs[job.id] = job

        self._executor().submit(self._execute, job, manifest, context or {})
        return job

    def get(self, job_id: str) -> BuildJob | None:
        return self._jobs.get(job_id)

    def list_recent(self, limit: int = 20) -> list[dict]:
        with self._lock:
            jobs = sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
        return [
            {"id": j.id, "project_id": j.project_id, "status": j.status,
             "duration_ms": j.duration_ms, "error": j.error}
            for j in jobs[:limit]
        ]

    def _execute(self, job: BuildJob, manifest, context: dict) -> None:
        from orchestrator.dispatcher import dispatcher
        job.status     = "running"
        job.started_at = time.time()
        try:
            from core.event_bus import bus
            bus.publish("build.started", {"job_id": job.id, "project_id": job.project_id})
        except Exception:
            pass
        try:
            result         = dispatcher.dispatch(manifest, context)
            job.result     = result
            job.status     = "done" if result.get("ok") else "failed"
            job.error      = "" if result.get("ok") else str(result.get("error",""))
        except Exception as e:
            job.status = "failed"
            job.error  = str(e)
        finally:
            job.finished_at = time.time()
            try:
                from core.event_bus import bus
                bus.publish("build.completed", {
                    "job_id": job.id, "project_id": job.project_id,
                    "ok": job.status == "done", "duration_ms": job.duration_ms,
                })
            except Exception:
                pass


build_scheduler = BuildScheduler()
