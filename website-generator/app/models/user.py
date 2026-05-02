"""
app/models/user.py — User model (thin wrapper around db.py)
"""
import db as database


class UserModel:
    """Namespace for user-related DB operations."""

    @staticmethod
    def create(username: str, email: str, password_hash: str) -> bool:
        return database.create_user(username, email, password_hash)

    @staticmethod
    def get_by_username(username: str):
        return database.get_user_by_username(username)

    @staticmethod
    def get_by_id(user_id: int):
        return database.get_user_by_id(user_id)

    @staticmethod
    def update_password(user_id: int, new_hash: str) -> None:
        database.update_user_password(user_id, new_hash)

    @staticmethod
    def get_all():
        return database.get_all_users()

    @staticmethod
    def delete(user_id: int) -> None:
        database.delete_user(user_id)

    @staticmethod
    def make_admin(user_id: int) -> None:
        conn = database.get_db()
        conn.execute("UPDATE users SET is_admin=1 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
