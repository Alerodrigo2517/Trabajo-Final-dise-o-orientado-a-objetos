"""Indicadores de negocio del panel."""

from datetime import date

from src.core.database import get_session
from src.repositories.dashboard_repository import DashboardRepository


def get_dashboard_summary() -> dict:
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    if inicio_mes.month == 12:
        mes_siguiente = inicio_mes.replace(year=inicio_mes.year + 1, month=1)
    else:
        mes_siguiente = inicio_mes.replace(month=inicio_mes.month + 1)

    with get_session() as sesion:
        return DashboardRepository.get_summary(sesion, inicio_mes, mes_siguiente)
