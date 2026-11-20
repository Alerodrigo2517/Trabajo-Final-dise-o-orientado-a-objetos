import os
from dataclasses import dataclass, field as campo
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

DIRECTORIO_BASE = Path(__file__).resolve().parents[2]
load_dotenv(DIRECTORIO_BASE / ".env")


def crear_url_bd_desde_entorno() -> str | URL:
    url_configurada = os.getenv("DATABASE_URL", "").strip()
    if url_configurada:
        return url_configurada

    return URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "presupuesto_herreria_poo"),
        query={"charset": "utf8mb4"},
    )


@dataclass(frozen=True)
class Settings:
    entorno_aplicacion: str = campo(default_factory=lambda: os.getenv("APP_ENV", "development"))
    nombre_aplicacion: str = campo(default_factory=lambda: os.getenv("APP_NAME", "Sistema de Herrería"))
    secreto_aplicacion: str = campo(default_factory=lambda: os.getenv("APP_SECRET", ""))
    servidor_bd: str = campo(default_factory=lambda: os.getenv("DB_HOST", "127.0.0.1"))
    puerto_bd: str = campo(default_factory=lambda: os.getenv("DB_PORT", "3306"))
    nombre_bd: str = campo(default_factory=lambda: os.getenv("DB_NAME", "presupuesto_herreria_poo"))
    usuario_bd: str = campo(default_factory=lambda: os.getenv("DB_USER", "root"))
    contrasena_bd: str = campo(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    certificado_ssl_bd: str = campo(default_factory=lambda: os.getenv("DB_SSL_CA", ""))
    clave_fernet: str = campo(default_factory=lambda: os.getenv("FERNET_KEY", ""))
    rondas_bcrypt: int = campo(default_factory=lambda: int(os.getenv("BCRYPT_ROUNDS", "12")))
    minutos_expiracion_sesion: int = campo(default_factory=lambda: int(os.getenv("SESSION_TIMEOUT_MINUTES", "60")))
    url_base_datos: str | URL = campo(default_factory=crear_url_bd_desde_entorno)


configuracion = Settings()
