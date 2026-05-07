"""
cluster/balancing.py — Load balancing strategies for job dispatch.

Strategies:
  RoundRobin   — cycle through workers
  LeastLoaded  — pick worker with lowest load
  Capability   — route by job type capability
  Random       — random selection (for testing)
"""
from __future__ import annotations

import random
import threading
from abc import ABC, abstractmethod
from typing import Any


class BalancingStrategy(ABC):
    @abstractmethod
    def select(self, workers: list[dict], job: dict) -> dict | None: ...


class RoundRobinStrategy(BalancingStrategy):
    def __init__(self):
        self._idx  = 0
        self._lock = threading.Lock()

    def select(self, workers: list[dict], job: dict) -> dict | None:
        if not workers:
            return None
        with self._lock:
            w = workers[self._idx % len(workers)]
            self._idx += 1
        return w


class LeastLoadedStrategy(BalancingStrategy):
    def select(self, workers: list[dict], job: dict) -> dict | None:
        if not workers:
            return None
        return min(workers, key=lambda w: (w.get("load", 0), w.get("jobs_done", 0)))


class CapabilityStrategy(BalancingStrategy):
    """Route to workers that declare the job type as a capability."""

    def select(self, workers: list[dict], job: dict) -> dict | None:
        job_type = job.get("type", "")
        capable  = [w for w in workers
                    if job_type in w.get("capabilities", [])
                    or "*" in w.get("capabilities", [])]
        if not capable:
            return None
        return min(capable, key=lambda w: w.get("load", 0))


class RandomStrategy(BalancingStrategy):
    def select(self, workers: list[dict], job: dict) -> dict | None:
        return random.choice(workers) if workers else None


class LoadBalancer:
    """
    Selects a worker for a job using a pluggable strategy.
    Falls back to LeastLoaded if the primary strategy returns None.
    """

    STRATEGIES = {
        "round_robin":  RoundRobinStrategy,
        "least_loaded": LeastLoadedStrategy,
        "capability":   CapabilityStrategy,
        "random":       RandomStrategy,
    }

    def __init__(self, strategy: str = "capability"):
        cls = self.STRATEGIES.get(strategy, CapabilityStrategy)
        self._primary  = cls()
        self._fallback = LeastLoadedStrategy()

    def select(self, workers: list[dict], job: dict) -> dict | None:
        w = self._primary.select(workers, job)
        if w is None:
            w = self._fallback.select(workers, job)
        return w

    def set_strategy(self, strategy: str) -> None:
        cls = self.STRATEGIES.get(strategy)
        if cls:
            self._primary = cls()


balancer = LoadBalancer()
