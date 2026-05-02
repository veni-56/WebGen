"""
app/services/file_service.py — File & project storage service
Handles all file system operations for generated projects.
"""
import shutil
from pathlib import Path
from generator import GENERATED_DIR, read_file, project_exists, make_zip


class FileService:
    """Handles generated project file operations."""

    @staticmethod
    def read(project_id: str, filepath: str) -> str | None:
        return read_file(project_id, filepath)

    @staticmethod
    def exists(project_id: str) -> bool:
        return project_exists(project_id)

    @staticmethod
    def zip(project_id: str) -> Path:
        return make_zip(project_id)

    @staticmethod
    def copy(src_id: str, dst_id: str) -> bool:
        """Copy a generated project to a new ID."""
        src = GENERATED_DIR / src_id
        dst = GENERATED_DIR / dst_id
        if src.exists() and not dst.exists():
            shutil.copytree(src, dst)
            return True
        return False

    @staticmethod
    def delete(project_id: str) -> None:
        """Remove all generated files for a project."""
        path = GENERATED_DIR / project_id
        if path.exists():
            shutil.rmtree(path)

    @staticmethod
    def list_files(project_id: str) -> list[str]:
        """Return sorted list of relative file paths in a project."""
        path = GENERATED_DIR / project_id
        if not path.exists():
            return []
        return sorted(
            str(f.relative_to(path))
            for f in path.rglob("*")
            if f.is_file()
        )
