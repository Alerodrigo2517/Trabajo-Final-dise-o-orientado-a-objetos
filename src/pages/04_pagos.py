import streamlit as st
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

from src.services.budget_service import list_budgets
from src.services.payment_service import create_payment, list_payments
from src.ui import currency, database_error, page_header, records_table

page_header("CAJA", "Pagos", "Registrá cobros reales asociados a un presupuesto, con su fecha, medio de pago y referencia.")

budgets = []
payments = []
try:
    budgets = list_budgets()
    payments = list_payments()
except SQLAlchemyError:
    database_error()

with st.container(border=True):
    st.subheader("Registrar un cobro")
    if budgets:
        budget_options = {
            f"#{row['id_presupuesto']} · {row['cliente']} · saldo estimado {currency(row['saldo_estimado'])}": row
            for row in budgets
        }
        with st.form("payment_form"):
            selected_label = st.selectbox("Presupuesto", list(budget_options))
            payment_date = st.date_input("Fecha del pago", value=date.today())
            amount = st.number_input("Monto recibido (ARS $)", min_value=0.0, value=0.0, step=1000.0)
            method = st.selectbox("Método de pago", ["Efectivo", "Transferencia", "Tarjeta", "Otro"])
            reference = st.text_input("Referencia o comprobante (opcional)", max_chars=100)
            submitted = st.form_submit_button("Guardar pago", type="primary", width="stretch")
        if submitted:
            try:
                payment_id = create_payment(
                    budget_id=budget_options[selected_label]["id_presupuesto"],
                    payment_date=payment_date,
                    amount=amount,
                    method=method,
                    reference=reference,
                )
                st.success(f"Pago #{payment_id} guardado en la base de datos.")
                st.rerun()
            except (ValueError, SQLAlchemyError) as error:
                database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
    else:
        st.info("Creá primero un presupuesto para poder asociar un pago.")

st.subheader("Historial de pagos")
payment_rows = [
    {
        "N.º": row["id_pago"],
        "Fecha": row["fecha"],
        "Presupuesto": f"#{row['id_presupuesto']}",
        "Cliente": row["cliente"],
        "Monto": currency(row["monto"]),
        "Método": row["metodo"],
        "Referencia": row["referencia"],
    }
    for row in payments
]
records_table(payment_rows, "payments", "Todavía no hay pagos", "Los pagos guardados aparecerán aquí.")
