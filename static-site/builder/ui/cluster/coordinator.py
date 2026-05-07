"""
cluster/coordinator.py — Cluster coordinator.

Coordinates job dispatch across the worker cluster:
- Selects the best worker for each job type
- Handles worker draining and failover
- Monitors cluster health
- Triggers dead-job recovery when workers die
"""
from __future__ import annotations

import threading
import time
from pathlib import Path


class ClusterCoordinator:
    HEALTH_INTERVAL = 30   # seconds between health sweeps

    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        self._stop    = threading.Event()
        self._thread: threading.Thread | None = None
        self._registry = None
        self._leases   = None

    def _get_registry(self):
        if self._registry is None:
            from cluster.registry import WorkerRegistry
            self._registry = WorkerRegistry(self._db_path)
        return self._registry

    def _get_leases(self):
        if self._leases is None:
            from cluster.leases import LeaseManager
            self._leases = LeaseManager(self._db_path)
        return self._leases

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="cluster-coordinator"
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def select_worker(self, job_type: str) -> dict | None:
        """Return the least-loaded capable worker, or None."""
        workers = self._get_registry().list_capable(job_type)
        idle    = [w for w in workers if w["status"] == "idle"]
        if not idle:
            return None
        return min(idle, key=lambda w: w["load"])

    def drain_worker(self, worker_id: str) -> None:
        """Mark a worker as draining — no new jobs will be assigned."""
        self._get_registry().mark_draining(worker_id)

    def cluster_status(self) -> dict:
        reg   = self._get_registry()
        stats = reg.stats()
        alive = reg.list_alive()
        return {
            "workers":     alive,
            "stats":       stats,
            "total_alive": len(alive),
        }

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._health_sweep()
            except Exception:
                pass
            time.sleep(self.HEALTH_INTERVAL)

    def _health_sweep(self) -> None:
        """Clean up dead workers and expired leases."""
        reg    = self._get_registry()
        leases = self._get_leases()
        dead   = reg.cleanup_dead()
        exp    = leases.cleanup_expired()
        if dead or exp:
            try:
                from logger_server import slog
                slog("CLUSTER_SWEEP", {"dead_workers": dead, "expired_leases": exp})
            except Exception:
                pass
        # Recover jobs whose workers died
        if dead:
            try:
                from worker import JobQueue
                recovered = JobQueue._recover_stuck()
                if recovered:
                    try:
                        from logger_server import slog
                        slog("CLUSTER_RECOVERY", {"recovered_jobs": recovered}, "WARNING")
                    except Exception:
                        pass
            except Exception:
                pass


coordinator = None   # initialized by bootstrap


def get_coordinator(db_path: str | Path | None = None) -> ClusterCoordinator:
    global coordinator
    if coordinator is None:
        if db_path is None:
            import os
            db_path = os.environ.get("DB_PATH", "./projects.db")
        coordinator = ClusterCoordinator(db_path)
    return coordinator
