"""Indicadores agregados a partir de las tablas existentes."""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from src.core.database import get_session
from src.models.orm import ClienteORM, MaterialORM, PagoORM, PresupuestoORM, TrabajoORM


def get_dashboard_summary() -> dict:
    today = date.today()
    month_start = today.replace(day=1)
    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1)

    with get_session() as session:
        budget_counts = dict(
            session.execute(
                select(PresupuestoORM.estado, func.count(PresupuestoORM.id_presupuesto)).group_by(
                    PresupuestoORM.estado
                )
            ).all()
        )
        active_work = session.scalar(
            select(func.count(TrabajoORM.id_trabajo)).where(TrabajoORM.estado.in_(("PENDIENTE", "EN_PROCESO")))
        ) or 0
        finished_work = session.scalar(
            select(func.count(TrabajoORM.id_trabajo)).where(TrabajoORM.estado == "FINALIZADO")
        ) or 0
        monthly_income = session.scalar(
            select(func.coalesce(func.sum(PagoORM.monto), 0)).where(
                PagoORM.fecha_pago >= month_start, PagoORM.fecha_pago < next_month
            )
        )
        client_count = session.scalar(select(func.count(ClienteORM.cuit_cliente))) or 0
        material_count = session.scalar(select(func.count(MaterialORM.id_material))) or 0
        return {
            "presupuestos_pendientes": int(budget_counts.get("PENDIENTE", 0)),
            "presupuestos_borrador": int(budget_counts.get("BORRADOR", 0)),
            "trabajos_activos": int(active_work),
            "trabajos_terminados": int(finished_work),
            "ingresos_mes": Decimal(monthly_income or 0),
            "clientes": int(client_count),
            "materiales": int(material_count),
        }
