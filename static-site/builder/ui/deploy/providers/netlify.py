"""
deploy/providers/netlify.py — Netlify deployment provider.
Requires NETLIFY_TOKEN and NETLIFY_SITE_ID env vars.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
import urllib.error
from pathlib import Path


class NetlifyProvider:
    name = "netlify"

    def __init__(self, token: str | None = None, site_id: str | None = None):
        self.token   = token   or os.environ.get("NETLIFY_TOKEN", "")
        self.site_id = site_id or os.environ.get("NETLIFY_SITE_ID", "")
        self._api    = "https://api.netlify.com/api/v1"

    def validate(self, build_dir: Path) -> list[str]:
        errors = []
        if not self.token:   errors.append("NETLIFY_TOKEN is not set")
        if not self.site_id: errors.append("NETLIFY_SITE_ID is not set")
        if not build_dir.exists(): errors.append(f"Build dir not found: {build_dir}")
        return errors

    def build(self, cfg: dict, build_dir: Path) -> dict:
        return {"ok": True, "dir": str(build_dir)}

    def deploy(self, build_dir: Path, project_name: str = "") -> dict:
        errors = self.validate(build_dir)
        if errors:
            return {"ok": False, "errors": errors}

        # Step 1: create deploy with file digest map
        file_map = {}
        file_contents = {}
        for f in build_dir.rglob("*"):
            if f.is_file():
                rel = "/" + str(f.relative_to(build_dir)).replace("\\", "/")
                content = f.read_bytes()
                digest  = hashlib.sha1(content).hexdigest()
                file_map[rel]      = digest
                file_contents[rel] = content

        payload = json.dumps({"files": file_map}).encode()
        req = urllib.request.Request(
            f"{self._api}/sites/{self.site_id}/deploys",
            data=payload, method="POST",
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                deploy = json.loads(resp.read())
        except Exception as e:
            return {"ok": False, "error": str(e)}

        deploy_id = deploy.get("id")
        required  = deploy.get("required", [])

        # Step 2: upload required files
        for digest in required:
            # Find file by digest
            for path, content in file_contents.items():
                if hashlib.sha1(content).hexdigest() == digest:
                    upload_req = urllib.request.Request(
                        f"{self._api}/deploys/{deploy_id}/files{path}",
                        data=content, method="PUT",
                        headers={"Authorization": f"Bearer {self.token}",
                                 "Content-Type": "application/octet-stream"},
                    )
                    try:
                        urllib.request.urlopen(upload_req, timeout=30)
                    except Exception:
                        pass
                    break

        return {"ok": True, "deploy_id": deploy_id,
                "url": deploy.get("deploy_ssl_url") or deploy.get("url")}

    def rollback(self, deploy_id: str) -> dict:
        req = urllib.request.Request(
            f"{self._api}/sites/{self.site_id}/deploys/{deploy_id}/restore",
            data=b"{}", method="POST",
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return {"ok": True, "data": json.loads(resp.read())}
        except Exception as e:
            return {"ok": False, "error": str(e)}
