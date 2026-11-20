"""Consultas SQLAlchemy para los indicadores del panel."""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.orm import ClienteORM, MaterialORM, PagoORM, PresupuestoORM, TrabajoORM


class DashboardRepository:
    @staticmethod
    def get_summary(sesion: Session, inicio_mes: date, mes_siguiente: date) -> dict:
        # La tabla presupuesto existente no tiene estado: informamos el total real.
        cantidad_presupuestos = sesion.scalar(select(func.count(PresupuestoORM.id_presupuesto))) or 0
        trabajo_activo = sesion.scalar(
            select(func.count(TrabajoORM.id_trabajo)).where(
                TrabajoORM.estado.in_(("PENDIENTE", "EN_PROCESO"))
            )
        ) or 0
        trabajo_terminado = sesion.scalar(
            select(func.count(TrabajoORM.id_trabajo)).where(TrabajoORM.estado == "FINALIZADO")
        ) or 0
        ingreso_mensual = sesion.scalar(
            select(func.coalesce(func.sum(PagoORM.monto), 0)).where(
                PagoORM.fecha_pago >= inicio_mes, PagoORM.fecha_pago < mes_siguiente
            )
        )
        cantidad_clientes = sesion.scalar(select(func.count(ClienteORM.cuit_cliente))) or 0
        cantidad_materiales = sesion.scalar(select(func.count(MaterialORM.id_material))) or 0
        return {
            "presupuestos_total": int(cantidad_presupuestos),
            "trabajos_activos": int(trabajo_activo),
            "trabajos_terminados": int(trabajo_terminado),
            "ingresos_mes": Decimal(ingreso_mensual or 0),
            "clientes": int(cantidad_clientes),
            "materiales": int(cantidad_materiales),
        }
