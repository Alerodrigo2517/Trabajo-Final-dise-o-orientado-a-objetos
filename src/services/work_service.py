"""Reglas de negocio para órdenes de trabajo según el enum existente."""

from datetime import date

from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.core.validators import clean_text
from src.models.orm import TrabajoORM
from src.repositories.budget_repository import BudgetRepository
from src.repositories.work_repository import WorkRepository

WORK_STATES = ("PENDIENTE", "EN_PROCESO", "FINALIZADO", "CANCELADO")


def list_works() -> list[dict]:
    with get_session() as session:
        rows = WorkRepository.list_works(session)
        return [
            {
                "id_trabajo": row.id_trabajo,
                "id_presupuesto": row.fk_presupuesto,
                "cliente": f"{row.presupuesto.cliente_contacto.cliente.nombre} {row.presupuesto.cliente_contacto.cliente.apellido}",
                "trabajo": row.presupuesto.tipo_trabajo.nombre_tipo,
                "ubicacion": row.presupuesto.ubicacion_trabajo.domicilio,
                "ciudad": row.presupuesto.ubicacion_trabajo.ciudad.nombre_ciudad,
                "fecha_inicio": row.fecha_inicio,
                "fecha_fin": row.fecha_fin,
                "estado": row.estado,
                "observaciones": row.observaciones or "",
            }
            for row in rows
        ]


def create_work(*, budget_id: int, start_date: date | None, observations: str = "") -> int:
    cleaned_observations = (observations or "").strip()
    if len(cleaned_observations) > 500:
        raise ValueError("Las observaciones admiten hasta 500 caracteres.")
    try:
        with get_session() as session:
            budget = BudgetRepository.get_budget(session, int(budget_id))
            if budget is None:
                raise ValueError("El presupuesto seleccionado ya no existe.")
            if budget.estado != "APROBADO":
                raise ValueError("Solo podés iniciar un trabajo con un presupuesto aprobado.")
            if WorkRepository.work_for_budget(session, int(budget_id)) is not None:
                raise ValueError("Ese presupuesto ya tiene una orden de trabajo.")
            work = TrabajoORM(
                presupuesto=budget,
                fecha_inicio=start_date,
                estado="PENDIENTE",
                observaciones=cleaned_observations or None,
            )
            WorkRepository.create_work(session, work)
            return work.id_trabajo
    except IntegrityError as exc:
        raise ValueError("Ese presupuesto ya tiene una orden de trabajo.") from exc


def update_work(
    *, work_id: int, status: str, start_date: date | None, end_date: date | None, observations: str = ""
) -> None:
    if status not in WORK_STATES:
        raise ValueError("El estado elegido no es válido para un trabajo.")
    if start_date and end_date and end_date < start_date:
        raise ValueError("La fecha de finalización no puede ser anterior a la fecha de inicio.")
    if status == "FINALIZADO" and end_date is None:
        raise ValueError("Indicá la fecha de finalización para cerrar el trabajo.")
    cleaned_observations = (observations or "").strip()
    if len(cleaned_observations) > 500:
        raise ValueError("Las observaciones admiten hasta 500 caracteres.")
    with get_session() as session:
        work = WorkRepository.get_work(session, int(work_id))
        if work is None:
            raise ValueError("La orden de trabajo ya no existe.")
        WorkRepository.update_work(
            session,
            work,
            status=status,
            start_date=start_date,
            end_date=end_date,
            observations=cleaned_observations or None,
        )

