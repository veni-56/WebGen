"""
app/models/project.py — Project model (thin wrapper around db.py)
"""
import db as database


class ProjectModel:
    """Namespace for project-related DB operations."""

    @staticmethod
    def save(project_id, user_id, name, website_type, prompt, config, project_type):
        database.save_project(project_id, user_id, name, website_type,
                              prompt, config, project_type)

    @staticmethod
    def get(project_id: str):
        return database.get_project(project_id)

    @staticmethod
    def get_for_user(user_id: int) -> list:
        return database.get_user_projects(user_id)

    @staticmethod
    def update_config(project_id, user_id, name, config) -> bool:
        return database.update_project_config(project_id, user_id, name, config)

    @staticmethod
    def delete(project_id, user_id) -> None:
        database.delete_project(project_id, user_id)

    @staticmethod
    def duplicate(project_id, user_id, new_id) -> bool:
        return database.duplicate_project(project_id, user_id, new_id)

    @staticmethod
    def rename(project_id, user_id, new_name) -> bool:
        return database.rename_project(project_id, user_id, new_name)

    @staticmethod
    def save_version(project_id, config, label="") -> None:
        database.save_version(project_id, config, label)

    @staticmethod
    def get_versions(project_id) -> list:
        return database.get_versions(project_id)

    @staticmethod
    def log(user_id, project_id, event, meta=None) -> None:
        database.log_event(user_id, project_id, event, meta or {})
