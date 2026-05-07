"""
worker/scheduler.py — Cron-style job scheduler.

Schedules recurring jobs (e.g. cleanup, metrics flush, backup).
Uses a background thread with a simple interval-based loop.
No external dependencies.

Usage:
    from worker.scheduler import scheduler
    scheduler.every(3600, 'cleanup_uploads', {'older_than_days': 7})
    scheduler.start()
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class ScheduledTask:
    name:         str
    interval_s:   float
    job_type:     str
    payload:      dict = field(default_factory=dict)
    last_run:     float = 0.0
    run_count:    int   = 0
    enabled:      bool  = True

    def is_due(self) -> bool:
        return self.enabled and (time.time() - self.last_run) >= self.interval_s

    def mark_run(self) -> None:
        self.last_run  = time.time()
        self.run_count += 1


class Scheduler:
    def __init__(self):
        self._tasks:  list[ScheduledTask] = []
        self._lock    = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop    = threading.Event()
        self._enqueue: Callable | None = None   # injected by server bootstrap

    def set_enqueue(self, fn: Callable) -> None:
        """Inject the enqueue function (avoids circular imports)."""
        self._enqueue = fn

    def every(self, interval_s: float, job_type: str,
              payload: dict | None = None, name: str = "") -> None:
        task = ScheduledTask(
            name       = name or job_type,
            interval_s = interval_s,
            job_type   = job_type,
            payload    = payload or {},
        )
        with self._lock:
            self._tasks.append(task)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="scheduler")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def status(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "name":       t.name,
                    "job_type":   t.job_type,
                    "interval_s": t.interval_s,
                    "last_run":   t.last_run,
                    "run_count":  t.run_count,
                    "enabled":    t.enabled,
                    "next_in_s":  max(0, round(t.interval_s - (time.time() - t.last_run))),
                }
                for t in self._tasks
            ]

    def _loop(self) -> None:
        while not self._stop.is_set():
            with self._lock:
                due = [t for t in self._tasks if t.is_due()]
            for task in due:
                if self._enqueue:
                    try:
                        self._enqueue(task.job_type, task.payload, priority=1)
                    except Exception as e:
                        print(f"[Scheduler] Failed to enqueue {task.name}: {e}")
                task.mark_run()
            time.sleep(10)   # check every 10 s


scheduler = Scheduler()
