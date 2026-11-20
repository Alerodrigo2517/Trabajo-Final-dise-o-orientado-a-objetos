"""Indicadores de negocio del panel."""

from datetime import date

from src.core.database import obtener_sesion_bd
from src.repositories.dashboard_repository import DashboardRepository


def obtener_resumen_panel() -> dict:
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    if inicio_mes.month == 12:
        mes_siguiente = inicio_mes.replace(year=inicio_mes.year + 1, month=1)
    else:
        mes_siguiente = inicio_mes.replace(month=inicio_mes.month + 1)

    with obtener_sesion_bd() as sesion:
        return DashboardRepository.obtener_resumen(sesion, inicio_mes, mes_siguiente)
