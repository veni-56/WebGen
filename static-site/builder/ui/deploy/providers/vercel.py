"""
deploy/providers/vercel.py — Vercel deployment provider.

Deploys a built static site to Vercel via their Deploy API.
Requires VERCEL_TOKEN env var.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from pathlib import Path


class VercelProvider:
    name = "vercel"

    def __init__(self, token: str | None = None, team_id: str | None = None):
        self.token   = token   or os.environ.get("VERCEL_TOKEN", "")
        self.team_id = team_id or os.environ.get("VERCEL_TEAM_ID", "")
        self._api    = "https://api.vercel.com"

    def validate(self, build_dir: Path) -> list[str]:
        errors = []
        if not self.token:
            errors.append("VERCEL_TOKEN is not set")
        if not build_dir.exists():
            errors.append(f"Build directory not found: {build_dir}")
        return errors

    def build(self, cfg: dict, build_dir: Path) -> dict:
        """Build is handled by the existing pipeline — nothing extra needed."""
        return {"ok": True, "dir": str(build_dir)}

    def deploy(self, build_dir: Path, project_name: str) -> dict:
        errors = self.validate(build_dir)
        if errors:
            return {"ok": False, "errors": errors}

        files = []
        for f in build_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(build_dir)).replace("\\", "/")
                content = f.read_bytes()
                files.append({
                    "file":     rel,
                    "data":     content.decode("utf-8", errors="replace"),
                    "encoding": "utf-8",
                })

        payload = json.dumps({
            "name":   project_name,
            "files":  files,
            "target": "production",
        }).encode()

        url = f"{self._api}/v13/deployments"
        if self.team_id:
            url += f"?teamId={self.team_id}"

        req = urllib.request.Request(
            url, data=payload, method="POST",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type":  "application/json",
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                return {"ok": True, "url": data.get("url"), "id": data.get("id")}
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            return {"ok": False, "error": f"HTTP {e.code}: {body}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def rollback(self, deployment_id: str) -> dict:
        """Vercel rollback: promote a previous deployment."""
        req = urllib.request.Request(
            f"{self._api}/v13/deployments/{deployment_id}/promote",
            data=b"{}",
            method="POST",
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return {"ok": True, "data": json.loads(resp.read())}
        except Exception as e:
            return {"ok": False, "error": str(e)}
