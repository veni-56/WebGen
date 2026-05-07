"""
orchestrator/manifests.py — Build manifest system.

A build manifest describes what needs to be built, in what order,
with what inputs, and where outputs go.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class BuildStep:
    id:       str
    name:     str
    runner:   str = "local"          # local | docker | remote
    inputs:   list[str] = field(default_factory=list)   # step IDs this depends on
    command:  str = ""
    env:      dict = field(default_factory=dict)
    timeout:  int = 300              # seconds
    cache_key: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "runner": self.runner,
            "inputs": self.inputs, "command": self.command,
            "env": self.env, "timeout": self.timeout, "cache_key": self.cache_key,
        }


@dataclass
class BuildManifest:
    id:         str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    project_id: str = ""
    version:    str = "1"
    steps:      list[BuildStep] = field(default_factory=list)
    artifacts:  list[str] = field(default_factory=list)   # expected output paths
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    meta:       dict = field(default_factory=dict)

    def add_step(self, name: str, runner: str = "local",
                 inputs: list[str] | None = None, **kwargs) -> BuildStep:
        step = BuildStep(
            id=uuid.uuid4().hex[:8], name=name, runner=runner,
            inputs=inputs or [], **kwargs
        )
        self.steps.append(step)
        return step

    def topological_order(self) -> list[BuildStep]:
        """Return steps in dependency order (Kahn's algorithm)."""
        id_map   = {s.id: s for s in self.steps}
        in_deg   = {s.id: len(s.inputs) for s in self.steps}
        ready    = [s for s in self.steps if not s.inputs]
        ordered  = []
        while ready:
            step = ready.pop(0)
            ordered.append(step)
            for s in self.steps:
                if step.id in s.inputs:
                    in_deg[s.id] -= 1
                    if in_deg[s.id] == 0:
                        ready.append(s)
        return ordered

    def fingerprint(self) -> str:
        data = json.dumps([s.to_dict() for s in self.steps], sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "id": self.id, "project_id": self.project_id,
            "version": self.version, "created_at": self.created_at,
            "steps": [s.to_dict() for s in self.steps],
            "artifacts": self.artifacts, "meta": self.meta,
        }

    @classmethod
    def for_static_site(cls, project_id: str, config: dict) -> "BuildManifest":
        """Create a standard static site build manifest."""
        m = cls(project_id=project_id)
        validate = m.add_step("validate",  runner="local", command="validate_config")
        render   = m.add_step("render",    runner="local", inputs=[validate.id], command="render_pages")
        optimize = m.add_step("optimize",  runner="local", inputs=[render.id],   command="optimize_assets")
        package  = m.add_step("package",   runner="local", inputs=[optimize.id], command="package_output")
        m.artifacts = ["index.html", "style.css", "script.js"]
        return m
