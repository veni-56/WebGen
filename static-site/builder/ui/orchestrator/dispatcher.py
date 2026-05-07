"""
orchestrator/dispatcher.py — Build step dispatcher.

Executes a BuildManifest by dispatching each step to the appropriate runner.
Supports parallel execution of independent steps.
"""
from __future__ import annotations

import concurrent.futures
import time
from typing import Any


class BuildDispatcher:
    def __init__(self, runner_registry=None, max_parallel: int = 4):
        self._runners     = runner_registry
        self._max_parallel = max_parallel

    def _registry(self):
        if self._runners is None:
            from orchestrator.runners import runner_registry
            self._runners = runner_registry
        return self._runners

    def dispatch(self, manifest, context: dict | None = None) -> dict:
        """
        Execute all steps in topological order.
        Independent steps run in parallel.
        Returns { ok, steps: {step_id: result}, total_ms }.
        """
        context  = context or {}
        steps    = manifest.topological_order()
        results  = {}
        t0       = time.time()
        ok       = True

        # Group steps by dependency level for parallel execution
        levels   = self._level_groups(steps)

        for level in levels:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(self._max_parallel, len(level))
            ) as pool:
                futures = {
                    pool.submit(self._run_step, step, context, results): step
                    for step in level
                }
                for future in concurrent.futures.as_completed(futures):
                    step   = futures[future]
                    result = future.result()
                    results[step.id] = result.to_dict()
                    if not result.ok:
                        ok = False

        total_ms = round((time.time() - t0) * 1000, 1)
        return {"ok": ok, "steps": results, "total_ms": total_ms,
                "manifest_id": manifest.id}

    def _run_step(self, step, context: dict, prior_results: dict):
        runner_name = step.runner or "local"
        try:
            runner = self._registry().get(runner_name)
        except KeyError:
            runner = self._registry().get("local")
        return runner.run(step.to_dict(), {**context, "prior": prior_results})

    def _level_groups(self, steps: list) -> list[list]:
        """Group steps into parallel levels based on dependencies."""
        id_to_step = {s.id: s for s in steps}
        levels: list[list] = []
        placed: set[str]   = set()

        remaining = list(steps)
        while remaining:
            ready = [s for s in remaining
                     if all(dep in placed for dep in s.inputs)]
            if not ready:
                # Cycle or unresolvable — add all remaining as one level
                ready = remaining
            levels.append(ready)
            for s in ready:
                placed.add(s.id)
                remaining.remove(s)
        return levels


dispatcher = BuildDispatcher()
