import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.components.budget_form import render_budget_form
from src.services.budget_service import PRESUPUESTO_ESTADOS, list_budgets, update_budget_status
from src.ui import currency, database_error, page_header, records_table

user = current_user()
can_edit = can_write(user)
page_header("VENTAS Y PLANIFICACIÓN", "Presupuestos", "Cada cotización queda relacionada con el cliente, el contacto, la ubicación y los materiales registrados en la base.")

if can_edit:
    with st.container(border=True):
        render_budget_form(key_prefix="pagina_presupuestos")
else:
    st.info("Tu perfil puede consultar presupuestos, pero no crear ni cambiar sus estados.")

st.subheader("Presupuestos registrados")
try:
    budgets = list_budgets()
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
    records_table(rows, "presupuestos_db", "Todavía no hay presupuestos", "Creá el primero desde el formulario de arriba.")

    if can_edit and budgets:
        st.subheader("Actualizar estado")
        budget_options = {
            f"#{budget['id_presupuesto']} · {budget['cliente']} · {budget['tipo_trabajo']}": budget
            for budget in budgets
        }
        selected_label = st.selectbox("Presupuesto", list(budget_options), key="budget_status_selection")
        selected_budget = budget_options[selected_label]
        labels = {
            "BORRADOR": "Borrador",
            "PENDIENTE": "Pendiente",
            "APROBADO": "Aprobado",
            "RECHAZADO": "Rechazado",
            "VENCIDO": "Vencido",
            "CANCELADO": "Cancelado",
        }
        with st.form("budget_status_form"):
            new_status = st.selectbox(
                "Estado nuevo",
                PRESUPUESTO_ESTADOS,
                index=PRESUPUESTO_ESTADOS.index(selected_budget["estado"]),
                format_func=lambda value: labels[value],
            )
            update = st.form_submit_button("Actualizar estado")
        if update:
            try:
                update_budget_status(selected_budget["id_presupuesto"], new_status)
                st.success("Estado actualizado en la base de datos.")
                st.rerun()
            except (ValueError, SQLAlchemyError) as error:
                if isinstance(error, SQLAlchemyError):
                    database_error()
                else:
                    st.error(str(error))
except SQLAlchemyError:
    database_error()
