import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.components.budget_form import render_budget_form
from src.core.authorization import can_write
from src.core.session import current_user
from src.services.budget_service import PRESUPUESTO_ESTADOS, list_budgets, update_budget_status
from src.ui import (
    currency,
    database_error,
    kpi_card,
    page_header,
    records_table,
    section_header,
)

user = current_user()
can_edit = can_write(user)

page_header(
    "VENTAS Y COTIZACIONES",
    "Presupuestos",
    "Confeccioná cotizaciones detalladas con materiales y mano de obra, y gestioná el ciclo de aprobación comercial.",
    badge="Módulo Comercial",
)

budgets = []
try:
    budgets = list_budgets()
except SQLAlchemyError:
    database_error()

total_count = len(budgets)
approved_count = sum(1 for b in budgets if b["estado"] == "APROBADO")
pending_count = sum(1 for b in budgets if b["estado"] in ("BORRADOR", "PENDIENTE"))
total_quoted = sum(float(b["total_estimado"] or 0) for b in budgets)

kpis = st.columns(4)
with kpis[0]:
    kpi_card("Total presupuestos", total_count, "Emitidos en el sistema", icon="📐", tone="amber")
with kpis[1]:
    kpi_card("Aprobados", approved_count, "Listos para producción", icon="✅", tone="emerald")
with kpis[2]:
    kpi_card("En evaluación", pending_count, "Borrador o pendientes", icon="⏳", tone="blue")
with kpis[3]:
    kpi_card("Volumen cotizado", currency(total_quoted), "Suma total estimada", icon="💰", tone="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    tab_list, tab_new = st.tabs(["📋 Historial y estados de presupuestos", "➕ Crear nuevo presupuesto"])
else:
    st.info("👁️ Tu perfil puede consultar presupuestos, pero no crear ni cambiar sus estados.")
    tab_list = st.container()
    tab_new = None

if tab_new is not None:
    with tab_new:
        with st.container(border=True):
            render_budget_form(key_prefix="pagina_presupuestos")

with tab_list:
    if can_edit and budgets:
        with st.container(border=True):
            section_header(
                "Actualizar estado comercial",
                "Cambiá el estado de una cotización (al pasar a Aprobado se habilita su orden de trabajo).",
                icon="🔄",
                badge="Gestión de estado",
            )
            budget_options = {
                f"#{budget['id_presupuesto']} · {budget['cliente']} · {budget['tipo_trabajo']} ({budget['estado']})": budget
                for budget in budgets
            }
            col_sel, col_form = st.columns([1.3, 1], gap="large")
            with col_sel:
                selected_label = st.selectbox("Seleccionar presupuesto", list(budget_options), key="budget_status_selection")
                selected_budget = budget_options[selected_label]
                st.caption(
                    f"Cliente: **{selected_budget['cliente']}** · Total estimado: **{currency(selected_budget['total_estimado'])}** · "
                    f"Saldo: **{currency(selected_budget['saldo_estimado'])}**"
                )
            labels = {
                "BORRADOR": "Borrador",
                "PENDIENTE": "Pendiente",
                "APROBADO": "Aprobado",
                "RECHAZADO": "Rechazado",
                "VENCIDO": "Vencido",
                "CANCELADO": "Cancelado",
            }
            with col_form:
                with st.form("budget_status_form"):
                    new_status = st.selectbox(
                        "Nuevo estado",
                        PRESUPUESTO_ESTADOS,
                        index=PRESUPUESTO_ESTADOS.index(selected_budget["estado"]),
                        format_func=lambda value: labels[value],
                    )
                    update = st.form_submit_button("Guardar nuevo estado", type="primary", width="stretch")
                if update:
                    try:
                        update_budget_status(selected_budget["id_presupuesto"], new_status)
                        st.success("✅ Estado del presupuesto actualizado correctamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        if isinstance(error, SQLAlchemyError):
                            database_error()
                        else:
                            st.error(str(error))

    with st.container(border=True):
        section_header(
            "Registro histórico de presupuestos",
            "Detalle de costos de materiales, mano de obra, pagos acumulados y saldo estimado.",
            icon="📊",
            badge=f"{total_count} presupuestos",
        )
        rows = [
            {
                "N.º": budget["id_presupuesto"],
                "Fecha": budget["fecha"],
                "Cliente": budget["cliente"],
                "Trabajo": budget["tipo_trabajo"],
                "Ubicación": f"{budget['ubicacion']}, {budget['ciudad']}",
                "Estado": budget["estado"].replace("_", " ").title(),
                "Materiales": currency(budget["materiales"]),
                "Mano de obra": currency(budget["mano_obra"]),
                "Total estimado": currency(budget["total_estimado"]),
                "Pagado": currency(budget["pagado"]),
                "Saldo estimado": currency(budget["saldo_estimado"]),
            }
            for budget in budgets
        ]
        records_table(
            rows,
            "presupuestos_db",
            "Todavía no hay presupuestos registrados",
            "Abrí la pestaña «Crear nuevo presupuesto» para cargar la primera cotización.",
        )
