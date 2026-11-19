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
    "Iniciá órdenes de fabricación a partir de presupuestos aprobados y gestioná el avance de obra hasta su finalización.",
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
    kpi_card("Total órdenes", len(works), "Registradas en el taller", icon="🛠️", tone="amber")
with kpis[1]:
    kpi_card("Finalizadas", finished_works, "Trabajos concluidos", icon="✅", tone="emerald")
with kpis[2]:
    kpi_card("En fabricación", active_works, "Pendientes o en proceso", icon="⚙️", tone="blue")
with kpis[3]:
    kpi_card("Listos para iniciar", len(eligible), "Presupuestos aprobados sin orden", icon="🚀", tone="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    tab_list, tab_new = st.tabs(
        [
            "📋 Historial y estados de órdenes",
            f"➕ Iniciar nueva orden de trabajo ({len(eligible)})",
        ]
    )
else:
    st.info("👁️ Tu perfil puede consultar las órdenes de trabajo, pero no crear órdenes ni cambiar sus estados.")
    tab_list = st.container()
    tab_new = None

if tab_new is not None:
    with tab_new:
        with st.container(border=True):
            section_header(
                "Apertura de orden de trabajo",
                "Seleccioná un presupuesto aprobado para generar su orden de fabricación en el taller.",
                icon="🚀",
                badge=f"{len(eligible)} presupuestos disponibles",
            )
            if eligible:
                budget_options = {
                    f"#{budget['id_presupuesto']} · {budget['cliente']} · {budget['tipo_trabajo']} ({currency(budget['total_estimado'])})": budget
                    for budget in eligible
                }
                selected_budget_label = st.selectbox(
                    "1. Seleccionar presupuesto aprobado",
                    list(budget_options),
                    key="create_work_budget_selector",
                )
                target_budget = budget_options[selected_budget_label]

                with st.form("create_work_form"):
                    st.markdown('<p class="panel-heading">RESUMEN DEL PRESUPUESTO VINCULADO</p>', unsafe_allow_html=True)
                    info_c1, info_c2 = st.columns(2)
                    with info_c1:
                        st.text_input("Cliente", value=target_budget["cliente"], disabled=True)
                        st.text_input("Tipo de trabajo", value=target_budget["tipo_trabajo"], disabled=True)
                    with info_c2:
                        st.text_input(
                            "Ubicación de obra",
                            value=f"{target_budget['ubicacion']}, {target_budget['ciudad']}",
                            disabled=True,
                        )
                        st.text_input(
                            "Total presupuestado",
                            value=currency(target_budget["total_estimado"]),
                            disabled=True,
                        )

                    st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">PLANIFICACIÓN DE TALLER</p>', unsafe_allow_html=True)
                    start_date = st.date_input("Fecha programada de inicio", value=date.today())
                    observations = st.text_area(
                        "Observaciones e instrucciones de fabricación",
                        max_chars=500,
                        height=95,
                        placeholder="Prioridad, operario asignado, detalles de corte, soldadura o montaje en obra…",
                    )
                    create = st.form_submit_button("🛠️ Crear orden de trabajo", type="primary", width="stretch")
                if create:
                    try:
                        work_id = create_work(
                            budget_id=target_budget["id_presupuesto"],
                            start_date=start_date,
                            observations=observations,
                        )
                        st.success(f"✅ Orden de trabajo #{work_id} creada exitosamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("No hay presupuestos aprobados pendientes de iniciar orden. Aprobá primero una cotización en la sección Presupuestos.")
                st.page_link("src/pages/02_presupuestos.py", label="Ir a Presupuestos", icon="📐")

with tab_list:
    if can_edit and works:
        with st.container(border=True):
            section_header(
                "Actualizar estado y seguimiento de orden",
                "Modificá la etapa de producción, fechas de ejecución y notas técnicas de una orden activa.",
                icon="🔄",
                badge="Gestión de estado",
            )
            work_options = {
                f"#{work['id_trabajo']} · {work['cliente']} · {work['trabajo']} ({work['estado'].replace('_', ' ').title()})": work
                for work in works
            }
            col_sel, col_form = st.columns([1.15, 1.35], gap="large")
            with col_sel:
                selected_label = st.selectbox("Seleccionar orden de trabajo", list(work_options), key="work_update_selection")
                selected_work = work_options[selected_label]
                st.caption(
                    f"Presupuesto: **#{selected_work['id_presupuesto']}** · Cliente: **{selected_work['cliente']}** · "
                    f"Ubicación: **{selected_work['ubicacion']}, {selected_work['ciudad']}**"
                )
                finish = st.checkbox(
                    "Incluir fecha de finalización",
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

            with col_form:
                with st.form(f"work_update_form_{selected_work['id_trabajo']}"):
                    f_col1, f_col2 = st.columns(2)
                    with f_col1:
                        status = st.selectbox(
                            "Nuevo estado",
                            WORK_STATES,
                            index=WORK_STATES.index(selected_work["estado"]),
                            format_func=lambda value: value.replace("_", " ").title(),
                        )
                    with f_col2:
                        start_date = st.date_input(
                            "Fecha de inicio",
                            value=selected_work["fecha_inicio"] or date.today(),
                            key=f"work_start_{selected_work['id_trabajo']}",
                        )
                    observations = st.text_area(
                        "Observaciones de avance",
                        value=selected_work["observaciones"],
                        max_chars=500,
                        height=75,
                        key=f"work_observations_{selected_work['id_trabajo']}",
                    )
                    update = st.form_submit_button("Guardar cambios de la orden", type="primary", width="stretch")
                if update:
                    try:
                        update_work(
                            work_id=selected_work["id_trabajo"],
                            status=status,
                            start_date=start_date,
                            end_date=end_date,
                            observations=observations,
                        )
                        st.success("✅ Orden de trabajo actualizada correctamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))

    with st.container(border=True):
        section_header(
            "Registro histórico de órdenes de trabajo",
            "Listado completo de trabajos con sus fechas de inicio, finalización y estado actual.",
            icon="📊",
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
            "Todavía no hay órdenes de trabajo registradas",
            "Abrí la pestaña «Iniciar nueva orden de trabajo» para poner en marcha un presupuesto aprobado.",
        )
