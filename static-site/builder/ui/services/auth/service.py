"""services/auth/service.py — Auth domain service."""
from __future__ import annotations
from services.base import BaseService, ServiceError


class AuthService(BaseService):
    service_name = "auth"

    def register(self, email: str, password: str) -> dict:
        from db.repositories import UserRepository, OrgRepository
        from db.connection import transaction
        import re, uuid
        email = email.lower().strip()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ServiceError("Invalid email address", "INVALID_EMAIL")
        if len(password) < 8:
            raise ServiceError("Password must be at least 8 characters", "WEAK_PASSWORD")
        user_repo = UserRepository(self._conn)
        if user_repo.find_by_email(email):
            raise ServiceError("Email already registered", "EMAIL_EXISTS")
        pw_hash = self._hash_password(password)
        with transaction(self._conn):
            uid    = user_repo.create(email, pw_hash)
            # Auto-create personal org
            slug   = f"personal-{uid[:8]}"
            org_id = OrgRepository(self._conn).create(f"{email.split('@')[0]}'s Workspace", slug)
            OrgRepository(self._conn).add_member(org_id, uid, "owner")
        self._emit("user.registered", {"user_id": uid, "email": email, "org_id": org_id})
        return {"id": uid, "email": email, "org_id": org_id}

    def login(self, email: str, password: str) -> dict:
        from db.repositories import UserRepository
        user = UserRepository(self._conn).find_by_email(email.lower().strip())
        if not user or not self._check_password(password, user["password_hash"]):
            raise ServiceError("Invalid email or password", "INVALID_CREDENTIALS")
        self._emit("user.logged_in", {"user_id": user["id"]})
        return {"id": user["id"], "email": user["email"]}

    def _hash_password(self, pw: str) -> str:
        try:
            import bcrypt
            return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
        except ImportError:
            import hashlib, secrets
            salt = secrets.token_hex(16)
            dk   = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260_000)
            return f"pbkdf2:{salt}:{dk.hex()}"

    def _check_password(self, pw: str, stored: str) -> bool:
        try:
            import bcrypt
            if stored.startswith("$2"):
                return bcrypt.checkpw(pw.encode(), stored.encode())
        except ImportError:
            pass
        if stored.startswith("pbkdf2:"):
            import hashlib, hmac
            _, salt, dk_hex = stored.split(":", 2)
            dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260_000)
            return hmac.compare_digest(dk.hex(), dk_hex)
        return False
