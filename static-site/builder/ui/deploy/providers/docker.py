"""
deploy/providers/docker.py — Docker deployment provider.

Builds a Docker image from the published static site and
optionally pushes it to a registry.

Requires Docker CLI to be installed on the host.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


_DOCKERFILE_TEMPLATE = """\
FROM nginx:1.25-alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""


class DockerProvider:
    name = "docker"

    def __init__(self, registry: str | None = None, tag: str | None = None):
        self.registry = registry or os.environ.get("DOCKER_REGISTRY", "")
        self.tag      = tag      or os.environ.get("DOCKER_TAG", "latest")

    def validate(self, build_dir: Path) -> list[str]:
        errors = []
        if not shutil.which("docker"):
            errors.append("Docker CLI not found in PATH")
        if not build_dir.exists():
            errors.append(f"Build directory not found: {build_dir}")
        return errors

    def build(self, cfg: dict, build_dir: Path) -> dict:
        """Build is handled by the existing pipeline."""
        return {"ok": True, "dir": str(build_dir)}

    def deploy(self, build_dir: Path, project_name: str) -> dict:
        errors = self.validate(build_dir)
        if errors:
            return {"ok": False, "errors": errors}

        image_name = self._image_name(project_name)

        # Write Dockerfile into a temp context dir
        with tempfile.TemporaryDirectory() as ctx:
            ctx_path = Path(ctx)
            shutil.copytree(build_dir, ctx_path / "site", dirs_exist_ok=True)
            (ctx_path / "Dockerfile").write_text(_DOCKERFILE_TEMPLATE)

            result = subprocess.run(
                ["docker", "build", "-t", image_name, "."],
                cwd=ctx_path, capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                return {"ok": False, "error": result.stderr[:2000]}

        # Push if registry is configured
        if self.registry:
            push = subprocess.run(
                ["docker", "push", image_name],
                capture_output=True, text=True, timeout=300
            )
            if push.returncode != 0:
                return {"ok": False, "error": f"Push failed: {push.stderr[:1000]}"}

        return {"ok": True, "image": image_name,
                "url": f"docker run -p 80:80 {image_name}"}

    def rollback(self, image_tag: str) -> dict:
        """Re-tag a previous image as latest."""
        image_name = self._image_name("site")
        result = subprocess.run(
            ["docker", "tag", f"{image_name}:{image_tag}", f"{image_name}:latest"],
            capture_output=True, text=True
        )
        return {"ok": result.returncode == 0, "error": result.stderr}

    def _image_name(self, project_name: str) -> str:
        slug = project_name.lower().replace(" ", "-")
        if self.registry:
            return f"{self.registry}/{slug}:{self.tag}"
        return f"{slug}:{self.tag}"
