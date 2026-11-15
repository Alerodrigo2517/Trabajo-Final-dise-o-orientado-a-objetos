import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


@dataclass
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    app_name: str = os.getenv("APP_NAME", "Sistema de Herrería")
    app_secret: str = os.getenv("APP_SECRET", "")
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: str = os.getenv("DB_PORT", "3306")
    db_name: str = os.getenv("DB_NAME", "presupuesto_herreria_poo")
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_ssl_ca: str = os.getenv("DB_SSL_CA", "")
    fernet_key: str = os.getenv("FERNET_KEY", "")
    bcrypt_rounds: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    max_login_attempts: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    lock_account_minutes: int = int(os.getenv("LOCK_ACCOUNT_MINUTES", "60"))
    database_url: str = os.getenv("DATABASE_URL", "")



settings = Settings()
if not settings.database_url:
    raise RuntimeError("No encontramos la URL de la base de datos")
else:
    print(settings.database_url)
