"""
app/models/__init__.py
Data access layer — thin wrappers around db.py for use inside blueprints.
"""
from app.models.user    import UserModel
from app.models.project import ProjectModel

__all__ = ["UserModel", "ProjectModel"]
