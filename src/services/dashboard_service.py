"""Indicadores de negocio del panel."""

from datetime import date

from src.core.database import get_session
from src.repositories.dashboard_repository import DashboardRepository


def get_dashboard_summary() -> dict:
    today = date.today()
    month_start = today.replace(day=1)
    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1)

    with get_session() as session:
        return DashboardRepository.get_summary(session, month_start, next_month)
