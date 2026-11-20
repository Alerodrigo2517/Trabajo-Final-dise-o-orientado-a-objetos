from __future__ import annotations
from contextlib import contextmanager

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import configuracion


class Base(DeclarativeBase):
    pass


motor = create_engine(
    configuracion.url_base_datos,
    pool_pre_ping=True,
    pool_recycle=1800
)

FabricaSesiones = sessionmaker(
    bind=motor,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


@contextmanager
def obtener_sesion_bd():
    sesion = FabricaSesiones()
    try:
        yield sesion
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()


def probar_conexion_bd() -> bool:
    with motor.connect() as conexion:
        return conexion.scalar(select(1)) == 1
