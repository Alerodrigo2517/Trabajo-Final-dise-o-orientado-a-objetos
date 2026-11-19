from datetime import date

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.budget_service import list_budgets
from src.services.work_service import WORK_STATES, create_work, list_works, update_work
from src.ui import (
    currency,
    database_error,
    kpi_card,
    page_header,
    records_table,
    section_header,
)

can_edit = can_write(current_user())
page_header(
    "TALLER Y PRODUCCIÓN",
    "Órdenes de Trabajo",
    "Convertí presupuestos aprobados en órdenes de fabricación y hacé el seguimiento de avance hasta la entrega final.",
    badge="Módulo Producción",
)

budgets = []
works = []
try:
    budgets = list_budgets()
    works = list_works()
except SQLAlchemyError:
    database_error()

eligible = [budget for budget in budgets if budget["estado"] == "APROBADO" and budget["trabajo_id"] is None]
active_works = sum(1 for w in works if w["estado"] in ("PENDIENTE", "EN_PROCESO"))
finished_works = sum(1 for w in works if w["estado"] in ("FINALIZADO", "ENTREGADO", "TERMINADO"))

kpis = st.columns(4)
with kpis[0]:
    kpi_card("Órdenes totales", len(works), "Registradas en el taller", icon="🛠️", tone="slate")
with kpis[1]:
    kpi_card("En fabricación", active_works, "Pendientes o en proceso", icon="⚙️", tone="blue")
with kpis[2]:
    kpi_card("Finalizadas", finished_works, "Trabajos concluidos", icon="✅", tone="emerald")
with kpis[3]:
    kpi_card("Listos para iniciar", len(eligible), "Presupuestos aprobados sin orden", icon="🚀", tone="amber")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    col_create, col_update = st.columns(2, gap="large")
    with col_create:
        with st.container(border=True):
            section_header(
                "Iniciar nueva orden de trabajo",
                "Generá una orden a partir de un presupuesto aprobado.",
                icon="🚀",
                badge=f"{len(eligible)} disponibles",
            )
            if eligible:
                budget_options = {
                    f"#{budget['id_presupuesto']} · {budget['cliente']} · {budget['tipo_trabajo']} ({currency(budget['total_estimado'])})": budget
                    for budget in eligible
                }
                with st.form("create_work_form"):
                    selected_label = st.selectbox("Presupuesto aprobado", list(budget_options))
                    start_date = st.date_input("Fecha de inicio de fabricación", value=date.today())
                    observations = st.text_area(
                        "Observaciones de taller",
                        max_chars=500,
                        height=90,
                        placeholder="Prioridad, responsable asignado, notas de corte o montaje…",
                    )
                    create = st.form_submit_button("🛠️ Crear orden de trabajo", type="primary", width="stretch")
                if create:
                    try:
                        work_id = create_work(
                            budget_id=budget_options[selected_label]["id_presupuesto"],
                            start_date=start_date,
                            observations=observations,
                        )
                        st.success(f"✅ Orden de trabajo #{work_id} iniciada correctamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("No hay presupuestos aprobados pendientes de iniciar orden. Aprobá primero una cotización en Presupuestos.")

    with col_update:
        with st.container(border=True):
            section_header(
                "Actualizar orden existente",
                "Modificá el estado de avance, fecha de cierre u observaciones.",
                icon="🔄",
                badge="Seguimiento",
            )
            if works:
                work_options = {
                    f"#{work['id_trabajo']} · {work['cliente']} · {work['trabajo']} ({work['estado'].replace('_', ' ').title()})": work
                    for work in works
                }
                selected_label = st.selectbox("Seleccionar orden de trabajo", list(work_options), key="work_update_selection")
                selected_work = work_options[selected_label]
                finish = st.checkbox(
                    "Registrar fecha de finalización",
                    value=selected_work["fecha_fin"] is not None,
                    key=f"work_finish_{selected_work['id_trabajo']}",
                )
                end_date = selected_work["fecha_fin"] if finish else None
                if finish:
                    end_date = st.date_input(
                        "Fecha de finalización",
                        value=selected_work["fecha_fin"] or date.today(),
                        key=f"work_end_{selected_work['id_trabajo']}",
                    )
                with st.form(f"work_update_form_{selected_work['id_trabajo']}"):
                    col_s, col_d = st.columns(2)
                    with col_s:
                        status = st.selectbox(
                            "Estado de la orden",
                            WORK_STATES,
                            index=WORK_STATES.index(selected_work["estado"]),
                            format_func=lambda value: value.replace("_", " ").title(),
                        )
                    with col_d:
                        start_date = st.date_input(
                            "Fecha de inicio",
                            value=selected_work["fecha_inicio"] or date.today(),
                            key=f"work_start_{selected_work['id_trabajo']}",
                        )
                    observations = st.text_area(
                        "Observaciones técnicas",
                        value=selected_work["observaciones"],
                        max_chars=500,
                        height=75,
                        key=f"work_observations_{selected_work['id_trabajo']}",
                    )
                    update = st.form_submit_button("💾 Guardar cambios", type="primary", width="stretch")
                if update:
                    try:
                        update_work(
                            work_id=selected_work["id_trabajo"],
                            status=status,
                            start_date=start_date,
                            end_date=end_date,
                            observations=observations,
                        )
                        st.success("✅ Orden de trabajo actualizada.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("Todavía no hay órdenes de trabajo activas para actualizar.")
else:
    st.info("👁️ Tu perfil puede consultar las órdenes de trabajo, pero no crear ni cambiar sus estados.")

with st.container(border=True):
    section_header(
        "Tablero de trabajos registrados",
        "Seguimiento de órdenes vinculadas a presupuestos y clientes.",
        icon="📋",
        badge=f"{len(works)} órdenes",
    )
    work_rows = [
        {
            "N.º": work["id_trabajo"],
            "Presupuesto": f"#{work['id_presupuesto']}",
            "Cliente": work["cliente"],
            "Trabajo": work["trabajo"],
            "Ubicación": f"{work['ubicacion']}, {work['ciudad']}",
            "Inicio": work["fecha_inicio"],
            "Fin": work["fecha_fin"] or "En curso",
            "Estado": work["estado"].replace("_", " ").title(),
        }
        for work in works
    ]
    records_table(
        work_rows,
        "works",
        "Todavía no hay órdenes de trabajo",
        "Cuando apruebes un presupuesto, vas a poder iniciar su orden de fabricación desde esta pantalla.",
    )
