"""Consultas y persistencia de trabajos."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.orm import ClientesContactoORM, PresupuestoORM, TrabajoORM


class WorkRepository:
    @staticmethod
    def list_works(session: Session) -> list[TrabajoORM]:
        statement = (
            select(TrabajoORM)
            .options(
                joinedload(TrabajoORM.presupuesto)
                .joinedload(PresupuestoORM.cliente_contacto)
                .joinedload(ClientesContactoORM.cliente),
                joinedload(TrabajoORM.presupuesto).joinedload(PresupuestoORM.ubicacion_trabajo),
            )
            .order_by(TrabajoORM.fecha_inicio.desc(), TrabajoORM.id_trabajo.desc())
        )
        return list(session.scalars(statement).unique())

    @staticmethod
    def create_work(session: Session, work: TrabajoORM) -> TrabajoORM:
        session.add(work)
        session.flush()
        return work

    @staticmethod
    def get_work(session: Session, work_id: int) -> TrabajoORM | None:
        return session.get(TrabajoORM, work_id)

    @staticmethod
    def work_for_budget(session: Session, budget_id: int) -> TrabajoORM | None:
        return session.scalar(select(TrabajoORM).where(TrabajoORM.fk_presupuesto == budget_id))

    @staticmethod
    def update_work(
        session: Session,
        work: TrabajoORM,
        *,
        status: str,
        start_date: date | None,
        end_date: date | None,
        observations: str | None,
    ) -> None:
        work.estado = status
        work.fecha_inicio = start_date
        work.fecha_fin = end_date
        work.observaciones = observations
        session.flush()

