import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def database_url_from_environment() -> str | URL:
    configured_url = os.getenv("DATABASE_URL", "").strip()
    if configured_url:
        return configured_url

    return URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "presupuesto_herreria_poo"),
        query={"charset": "utf8mb4"},
    )


@dataclass
class Settings:
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Sistema de Herrería"))
    app_secret: str = field(default_factory=lambda: os.getenv("APP_SECRET", ""))
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "127.0.0.1"))
    db_port: str = field(default_factory=lambda: os.getenv("DB_PORT", "3306"))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "presupuesto_herreria_poo"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "root"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    db_ssl_ca: str = field(default_factory=lambda: os.getenv("DB_SSL_CA", ""))
    fernet_key: str = field(default_factory=lambda: os.getenv("FERNET_KEY", ""))
    bcrypt_rounds: int = field(default_factory=lambda: int(os.getenv("BCRYPT_ROUNDS", "12")))
    session_timeout_minutes: int = field(default_factory=lambda: int(os.getenv("SESSION_TIMEOUT_MINUTES", "60")))
    max_login_attempts: int = field(default_factory=lambda: int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")))
    lock_account_minutes: int = field(default_factory=lambda: int(os.getenv("LOCK_ACCOUNT_MINUTES", "60")))
    database_url: str | URL = field(default_factory=database_url_from_environment)


settings = Settings()
