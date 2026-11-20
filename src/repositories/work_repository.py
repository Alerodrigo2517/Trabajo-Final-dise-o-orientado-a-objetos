"""Consultas y persistencia de trabajos."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.orm import ClientesContactoORM, PresupuestoORM, TrabajoORM


class WorkRepository:
    @staticmethod
    def list_works(sesion: Session) -> list[TrabajoORM]:
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
    def create_work(sesion: Session, trabajo: TrabajoORM) -> TrabajoORM:
        sesion.add(trabajo)
        sesion.flush()
        return trabajo

    @staticmethod
    def get_work(sesion: Session, id_trabajo: int) -> TrabajoORM | None:
        return sesion.get(TrabajoORM, id_trabajo)

    @staticmethod
    def work_for_budget(sesion: Session, id_presupuesto: int) -> TrabajoORM | None:
        return sesion.scalar(select(TrabajoORM).where(TrabajoORM.fk_presupuesto == id_presupuesto))

    @staticmethod
    def update_work(
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

