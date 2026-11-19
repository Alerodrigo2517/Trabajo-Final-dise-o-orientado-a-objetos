"""Consultas SQLAlchemy para los indicadores del panel."""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.orm import ClienteORM, MaterialORM, PagoORM, PresupuestoORM, TrabajoORM


class DashboardRepository:
    @staticmethod
    def get_summary(session: Session, month_start: date, next_month: date) -> dict:
        # La tabla presupuesto existente no tiene estado: informamos el total real.
        budget_count = session.scalar(select(func.count(PresupuestoORM.id_presupuesto))) or 0
        active_work = session.scalar(
            select(func.count(TrabajoORM.id_trabajo)).where(
                TrabajoORM.estado.in_(("PENDIENTE", "EN_PROCESO"))
            )
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
            "presupuestos_total": int(budget_count),
            "trabajos_activos": int(active_work),
            "trabajos_terminados": int(finished_work),
            "ingresos_mes": Decimal(monthly_income or 0),
            "clientes": int(client_count),
            "materiales": int(material_count),
        }
