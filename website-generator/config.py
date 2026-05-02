"""
config.py — Environment-aware configuration for WebGen SaaS
Supports: development, production, testing
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    """Base configuration shared across all environments."""

    # ── Core ──────────────────────────────────────────────────────────────────
    SECRET_KEY       = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    APP_NAME         = "WebGen"
    APP_VERSION      = "2.0.0"

    # ── Database ──────────────────────────────────────────────────────────────
    # PostgreSQL in production, SQLite in dev
    DATABASE_URL     = os.environ.get("DATABASE_URL", "")
    SQLITE_PATH      = str(BASE_DIR / "platform.db")

    # ── Storage ───────────────────────────────────────────────────────────────
    GENERATED_DIR    = str(BASE_DIR / "generated")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ── Stripe ────────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY       = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY  = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET   = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRO_PRICE_ID     = os.environ.get("STRIPE_PRO_PRICE_ID", "price_pro")
    STRIPE_BIZ_PRICE_ID     = os.environ.get("STRIPE_BIZ_PRICE_ID", "price_business")

    # ── OpenAI (optional) ─────────────────────────────────────────────────────
    OPENAI_API_KEY   = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL     = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    # ── Rate limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_WINDOW_HOURS = 1

    # ── Session ───────────────────────────────────────────────────────────────
    SESSION_COOKIE_SECURE   = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL  = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # ── Security ──────────────────────────────────────────────────────────────
    WTF_CSRF_ENABLED = True
    BCRYPT_LOG_ROUNDS = 12

    @classmethod
    def use_postgres(cls) -> bool:
        return bool(cls.DATABASE_URL and "postgres" in cls.DATABASE_URL)

    @classmethod
    def use_openai(cls) -> bool:
        return bool(cls.OPENAI_API_KEY)


class DevelopmentConfig(Config):
    DEBUG            = True
    TESTING          = False
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL        = "DEBUG"
    BCRYPT_LOG_ROUNDS = 4  # Faster in dev


class ProductionConfig(Config):
    DEBUG            = False
    TESTING          = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL        = os.environ.get("LOG_LEVEL", "WARNING")

    @classmethod
    def validate(cls):
        """Raise if required production env vars are missing."""
        required = ["SECRET_KEY"]
        missing  = [k for k in required if not os.environ.get(k)]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Copy .env.example to .env and fill in the values."
            )


class TestingConfig(Config):
    DEBUG            = True
    TESTING          = True
    SQLITE_PATH      = ":memory:"
    WTF_CSRF_ENABLED = False
    BCRYPT_LOG_ROUNDS = 4


# ── Config selector ───────────────────────────────────────────────────────────
_configs = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
}


def get_config() -> Config:
    """Return the appropriate config class based on FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    cfg = _configs.get(env, DevelopmentConfig)
    if env == "production":
        cfg.validate()
    return cfg
