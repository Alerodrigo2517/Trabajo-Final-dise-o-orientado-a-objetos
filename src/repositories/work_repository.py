"""Consultas y persistencia de trabajos."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.orm import ClientesContactoORM, PresupuestoORM, TrabajoORM


class WorkRepository:
    @staticmethod
    def listar_trabajos(sesion: Session) -> list[TrabajoORM]:
        sentencia = (
            select(TrabajoORM)
            .options(
                joinedload(TrabajoORM.presupuesto)
                .joinedload(PresupuestoORM.cliente_contacto)
                .joinedload(ClientesContactoORM.cliente),
                joinedload(TrabajoORM.presupuesto).joinedload(PresupuestoORM.ubicacion_trabajo),
            )
            .order_by(TrabajoORM.fecha_inicio.desc(), TrabajoORM.id_trabajo.desc())
        )
        return list(sesion.scalars(sentencia).unique())

    @staticmethod
    def crear_trabajo(sesion: Session, trabajo: TrabajoORM) -> TrabajoORM:
        sesion.add(trabajo)
        sesion.flush()
        return trabajo

    @staticmethod
    def obtener_trabajo(sesion: Session, id_trabajo: int) -> TrabajoORM | None:
        return sesion.get(TrabajoORM, id_trabajo)

    @staticmethod
    def obtener_trabajo_por_presupuesto(sesion: Session, id_presupuesto: int) -> TrabajoORM | None:
        return sesion.scalar(select(TrabajoORM).where(TrabajoORM.fk_presupuesto == id_presupuesto))

    @staticmethod
    def actualizar_trabajo(
        sesion: Session,
        trabajo: TrabajoORM,
        *,
        estado: str,
        fecha_inicio: date | None,
        fecha_fin: date | None,
        observaciones: str | None,
    ) -> None:
        trabajo.estado = estado
        trabajo.fecha_inicio = fecha_inicio
        trabajo.fecha_fin = fecha_fin
        trabajo.observaciones = observaciones
        sesion.flush()

