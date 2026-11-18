import streamlit as st
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

from src.services.budget_service import list_budgets
from src.services.work_service import WORK_STATES, create_work, list_works, update_work
from src.ui import currency, database_error, page_header, records_table

page_header("PRODUCCIÓN", "Trabajos", "Iniciá órdenes desde presupuestos aprobados y actualizá los estados permitidos por la base de datos.")

budgets = []
works = []
try:
    budgets = list_budgets()
    works = list_works()
except SQLAlchemyError:
    database_error()

with st.container(border=True):
    st.subheader("Iniciar trabajo")
    eligible = [budget for budget in budgets if budget["estado"] == "APROBADO" and budget["trabajo_id"] is None]
    if eligible:
        budget_options = {
            f"#{budget['id_presupuesto']} · {budget['cliente']} · {budget['tipo_trabajo']} · {currency(budget['total_estimado'])}": budget
            for budget in eligible
        }
        with st.form("create_work_form"):
            selected_label = st.selectbox("Presupuesto aprobado", list(budget_options))
            start_date = st.date_input("Fecha de inicio", value=date.today())
            observations = st.text_area("Observaciones", max_chars=500)
            create = st.form_submit_button("Crear orden de trabajo", type="primary")
        if create:
            try:
                work_id = create_work(
                    budget_id=budget_options[selected_label]["id_presupuesto"],
                    start_date=start_date,
                    observations=observations,
                )
                st.success(f"Orden de trabajo #{work_id} guardada.")
                st.rerun()
            except (ValueError, SQLAlchemyError) as error:
                database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
    else:
        st.info("No hay presupuestos aprobados y disponibles para iniciar un trabajo.")

st.subheader("Trabajos registrados")
work_rows = [
    {
        "N.º": work["id_trabajo"],
        "Presupuesto": f"#{work['id_presupuesto']}",
        "Cliente": work["cliente"],
        "Trabajo": work["trabajo"],
        "Ubicación": f"{work['ubicacion']}, {work['ciudad']}",
        "Inicio": work["fecha_inicio"],
        "Fin": work["fecha_fin"] or "—",
        "Estado": work["estado"].replace("_", " ").title(),
    }
    for work in works
]
records_table(work_rows, "works", "Todavía no hay trabajos", "Al aprobar un presupuesto, vas a poder iniciar su orden desde acá.")

if works:
    st.subheader("Actualizar trabajo")
    work_options = {
        f"#{work['id_trabajo']} · {work['cliente']} · {work['trabajo']}": work for work in works
    }
    selected_label = st.selectbox("Orden de trabajo", list(work_options), key="work_update_selection")
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
        status = st.selectbox(
            "Estado",
            WORK_STATES,
            index=WORK_STATES.index(selected_work["estado"]),
            format_func=lambda value: value.replace("_", " ").title(),
        )
        start_date = st.date_input(
            "Fecha de inicio",
            value=selected_work["fecha_inicio"] or date.today(),
            key=f"work_start_{selected_work['id_trabajo']}",
        )
        observations = st.text_area(
            "Observaciones",
            value=selected_work["observaciones"],
            max_chars=500,
            key=f"work_observations_{selected_work['id_trabajo']}",
        )
        update = st.form_submit_button("Guardar cambios")
    if update:
        try:
            update_work(
                work_id=selected_work["id_trabajo"],
                status=status,
                start_date=start_date,
                end_date=end_date,
                observations=observations,
            )
            st.success("Orden de trabajo actualizada.")
            st.rerun()
        except (ValueError, SQLAlchemyError) as error:
            database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
