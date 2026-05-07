"""
deploy/providers/cloudflare.py — Cloudflare Pages deployment provider.

Deploys via the Cloudflare Pages Direct Upload API.
Requires CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID env vars.
"""
from __future__ import annotations

import json
import mimetypes
import os
import urllib.request
import urllib.error
from pathlib import Path


class CloudflareProvider:
    name = "cloudflare"

    def __init__(self, token: str | None = None, account_id: str | None = None):
        self.token      = token      or os.environ.get("CLOUDFLARE_API_TOKEN", "")
        self.account_id = account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        self._api       = "https://api.cloudflare.com/client/v4"

    def validate(self, build_dir: Path) -> list[str]:
        errors = []
        if not self.token:      errors.append("CLOUDFLARE_API_TOKEN is not set")
        if not self.account_id: errors.append("CLOUDFLARE_ACCOUNT_ID is not set")
        if not build_dir.exists(): errors.append(f"Build dir not found: {build_dir}")
        return errors

    def build(self, cfg: dict, build_dir: Path) -> dict:
        return {"ok": True, "dir": str(build_dir)}

    def deploy(self, build_dir: Path, project_name: str) -> dict:
        errors = self.validate(build_dir)
        if errors:
            return {"ok": False, "errors": errors}

        slug = project_name.lower().replace(" ", "-")

        # Step 1: Create or get project
        project = self._ensure_project(slug)
        if not project.get("ok"):
            return project

        # Step 2: Create deployment
        deployment = self._create_deployment(slug)
        if not deployment.get("ok"):
            return deployment

        deploy_id = deployment["deployment_id"]

        # Step 3: Upload files
        for f in build_dir.rglob("*"):
            if not f.is_file():
                continue
            rel  = str(f.relative_to(build_dir)).replace("\\", "/")
            mime = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
            upload_result = self._upload_file(slug, deploy_id, rel, f.read_bytes(), mime)
            if not upload_result.get("ok"):
                return upload_result

        # Step 4: Finalize
        return self._finalize_deployment(slug, deploy_id)

    def rollback(self, deployment_id: str) -> dict:
        return {"ok": False, "error": "Cloudflare Pages rollback must be done via dashboard"}

    def _request(self, method: str, path: str, data: bytes | None = None,
                 content_type: str = "application/json") -> dict:
        url = f"{self._api}{path}"
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type":  content_type,
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read())
                return {"ok": body.get("success", True), "data": body}
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            return {"ok": False, "error": f"HTTP {e.code}: {body[:500]}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _ensure_project(self, slug: str) -> dict:
        payload = json.dumps({"name": slug, "production_branch": "main"}).encode()
        result  = self._request("POST",
                                f"/accounts/{self.account_id}/pages/projects",
                                data=payload)
        # 409 = already exists — that's fine
        if not result["ok"] and "already exists" not in result.get("error", ""):
            return result
        return {"ok": True}

    def _create_deployment(self, slug: str) -> dict:
        result = self._request("POST",
                               f"/accounts/{self.account_id}/pages/projects/{slug}/deployments")
        if not result["ok"]:
            return result
        deploy_id = result["data"].get("result", {}).get("id", "")
        return {"ok": True, "deployment_id": deploy_id}

    def _upload_file(self, slug: str, deploy_id: str, path: str,
                     content: bytes, mime: str) -> dict:
        return self._request(
            "PUT",
            f"/accounts/{self.account_id}/pages/projects/{slug}/deployments/{deploy_id}/files/{path}",
            data=content, content_type=mime
        )

    def _finalize_deployment(self, slug: str, deploy_id: str) -> dict:
        result = self._request(
            "PATCH",
            f"/accounts/{self.account_id}/pages/projects/{slug}/deployments/{deploy_id}",
            data=b"{}"
        )
        url = result.get("data", {}).get("result", {}).get("url", "")
        return {"ok": result["ok"], "url": url, "deployment_id": deploy_id}
