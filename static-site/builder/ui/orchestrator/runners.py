"""
orchestrator/runners.py — Build runner abstraction.

Runners execute individual build steps in isolation.
Supported runners:
  LocalRunner   — runs in the current process (default)
  DockerRunner  — runs in a Docker container
  RemoteRunner  — HTTP call to a remote build agent (stub)
"""
from __future__ import annotations

import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class RunnerResult:
    def __init__(self, ok: bool, output: str = "", error: str = "",
                 duration_ms: float = 0.0, artifacts: dict | None = None):
        self.ok          = ok
        self.output      = output
        self.error       = error
        self.duration_ms = duration_ms
        self.artifacts   = artifacts or {}

    def to_dict(self) -> dict:
        return {"ok": self.ok, "output": self.output, "error": self.error,
                "duration_ms": self.duration_ms, "artifacts": self.artifacts}


class BuildRunner(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, step: dict, context: dict) -> RunnerResult: ...

    @abstractmethod
    def available(self) -> bool: ...


class LocalRunner(BuildRunner):
    """Runs build steps in the current process using registered handlers."""
    name = "local"

    # Handler registry: command_name → callable(step, context) → dict
    _handlers: dict[str, Any] = {}

    @classmethod
    def register(cls, command: str, fn) -> None:
        cls._handlers[command] = fn

    def available(self) -> bool:
        return True

    def run(self, step: dict, context: dict) -> RunnerResult:
        t0      = time.time()
        command = step.get("command", "")
        handler = self._handlers.get(command)
        if not handler:
            return RunnerResult(ok=False, error=f"No handler for command: {command}")
        try:
            result = handler(step, context)
            ms     = round((time.time() - t0) * 1000, 1)
            return RunnerResult(ok=True, output=str(result or ""),
                                duration_ms=ms, artifacts=result if isinstance(result, dict) else {})
        except Exception as e:
            ms = round((time.time() - t0) * 1000, 1)
            return RunnerResult(ok=False, error=str(e), duration_ms=ms)


class DockerRunner(BuildRunner):
    """Runs build steps inside a Docker container."""
    name = "docker"

    def __init__(self, image: str = "python:3.12-slim", timeout: int = 300):
        self._image   = image
        self._timeout = timeout

    def available(self) -> bool:
        import shutil
        return shutil.which("docker") is not None

    def run(self, step: dict, context: dict) -> RunnerResult:
        if not self.available():
            return RunnerResult(ok=False, error="Docker not available")
        t0      = time.time()
        command = step.get("command", "echo ok")
        env     = step.get("env", {})
        env_args = []
        for k, v in env.items():
            env_args += ["-e", f"{k}={v}"]
        try:
            result = subprocess.run(
                ["docker", "run", "--rm"] + env_args + [self._image, "sh", "-c", command],
                capture_output=True, text=True, timeout=self._timeout
            )
            ms = round((time.time() - t0) * 1000, 1)
            return RunnerResult(
                ok=result.returncode == 0,
                output=result.stdout[:5000],
                error=result.stderr[:2000] if result.returncode != 0 else "",
                duration_ms=ms,
            )
        except subprocess.TimeoutExpired:
            return RunnerResult(ok=False, error=f"Timeout after {self._timeout}s")
        except Exception as e:
            return RunnerResult(ok=False, error=str(e))


class RemoteRunner(BuildRunner):
    """Delegates build steps to a remote HTTP build agent."""
    name = "remote"

    def __init__(self, agent_url: str, token: str = ""):
        self._url   = agent_url.rstrip("/")
        self._token = token

    def available(self) -> bool:
        try:
            import urllib.request
            urllib.request.urlopen(f"{self._url}/health", timeout=3)
            return True
        except Exception:
            return False

    def run(self, step: dict, context: dict) -> RunnerResult:
        import json, urllib.request, urllib.error
        t0 = time.time()
        payload = json.dumps({"step": step, "context": context}).encode()
        req = urllib.request.Request(
            f"{self._url}/run", data=payload, method="POST",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self._token}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=step.get("timeout", 300)) as resp:
                data = json.loads(resp.read())
                ms   = round((time.time() - t0) * 1000, 1)
                return RunnerResult(ok=data.get("ok", False),
                                    output=data.get("output", ""),
                                    error=data.get("error", ""),
                                    duration_ms=ms,
                                    artifacts=data.get("artifacts", {}))
        except Exception as e:
            return RunnerResult(ok=False, error=str(e))


class RunnerRegistry:
    """Registry of available runners."""

    def __init__(self):
        self._runners: dict[str, BuildRunner] = {}
        # Register defaults
        self.register(LocalRunner())

    def register(self, runner: BuildRunner) -> None:
        self._runners[runner.name] = runner

    def get(self, name: str) -> BuildRunner:
        r = self._runners.get(name)
        if not r:
            raise KeyError(f"Runner '{name}' not registered")
        return r

    def list_available(self) -> list[str]:
        return [name for name, r in self._runners.items() if r.available()]


runner_registry = RunnerRegistry()
