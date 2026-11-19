from datetime import date

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.budget_service import list_budgets
from src.services.payment_service import create_payment, list_payments
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
    "TESORERÍA Y COBRANZAS",
    "Caja y Pagos",
    "Registrá señas, anticipos y cancelaciones asociadas a presupuestos, con trazabilidad por fecha y medio de cobro.",
    badge="Módulo Caja",
)

budgets = []
payments = []
try:
    budgets = list_budgets()
    payments = list_payments()
except SQLAlchemyError:
    database_error()

total_collected = sum(float(p["monto"] or 0) for p in payments)
pending_balances = sum(max(0.0, float(b["saldo_estimado"] or 0)) for b in budgets if b["estado"] == "APROBADO")
budgets_with_debt = sum(1 for b in budgets if float(b["saldo_estimado"] or 0) > 0 and b["estado"] == "APROBADO")

kpis = st.columns(3)
with kpis[0]:
    kpi_card("Total cobrado acumulado", currency(total_collected), f"En {len(payments)} pagos registrados", icon="💳", tone="emerald")
with kpis[1]:
    kpi_card("Saldo por cobrar (Aprobados)", currency(pending_balances), f"{budgets_with_debt} presupuestos con saldo", icon="📊", tone="amber")
with kpis[2]:
    kpi_card("Operaciones de caja", len(payments), "Comprobantes asentados", icon="🧾", tone="blue")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    form_col, table_col = st.columns([1, 1.35], gap="large")
    with form_col:
        with st.container(border=True):
            section_header(
                "Registrar un cobro",
                "Seleccioná el presupuesto e imputá el pago recibido.",
                icon="💵",
                badge="Nuevo ingreso",
            )
            if budgets:
                budget_options = {
                    f"#{row['id_presupuesto']} · {row['cliente']} · Saldo: {currency(row['saldo_estimado'])}": row
                    for row in budgets
                }
                selected_label = st.selectbox("Presupuesto a imputar", list(budget_options), key="payment_budget_sel")
                sel_budget = budget_options[selected_label]
                st.caption(
                    f"Total presupuestado: **{currency(sel_budget['total_estimado'])}** · "
                    f"Pagado: **{currency(sel_budget['pagado'])}** · "
                    f"Saldo estimado: **{currency(sel_budget['saldo_estimado'])}**"
                )
                with st.form("payment_form"):
                    col_d, col_m = st.columns(2)
                    with col_d:
                        payment_date = st.date_input("Fecha del pago", value=date.today())
                    with col_m:
                        method = st.selectbox("Medio de pago", ["Efectivo", "Transferencia", "Tarjeta", "Otro"])
                    amount = st.number_input("Monto recibido (ARS $)", min_value=0.0, value=0.0, step=1000.0)
                    reference = st.text_input(
                        "N.º de comprobante o referencia (opcional)",
                        max_chars=100,
                        placeholder="Ej. Transferencia CBU #48291",
                    )
                    submitted = st.form_submit_button("💾 Guardar cobro", type="primary", width="stretch")
                if submitted:
                    try:
                        payment_id = create_payment(
                            budget_id=sel_budget["id_presupuesto"],
                            payment_date=payment_date,
                            amount=amount,
                            method=method,
                            reference=reference,
                        )
                        st.success(f"✅ Pago #{payment_id} registrado exitosamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("Creá primero un presupuesto para poder imputar un pago.")
    with table_col:
        with st.container(border=True):
            section_header(
                "Historial de pagos",
                "Movimientos de caja ordenados por fecha y presupuesto.",
                icon="🧾",
                badge=f"{len(payments)} cobros",
            )
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
            records_table(
                payment_rows,
                "payments",
                "Todavía no hay pagos registrados",
                "Los cobros que registres en el panel izquierdo aparecerán automáticamente acá.",
            )
else:
    st.info("👁️ Tu perfil puede consultar el historial de cobros, pero no registrar nuevos pagos.")
    with st.container(border=True):
        section_header(
            "Historial de pagos",
            "Movimientos de caja ordenados por fecha y presupuesto.",
            icon="🧾",
            badge=f"{len(payments)} cobros",
        )
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
        records_table(
            payment_rows,
            "payments",
            "Todavía no hay pagos registrados",
            "Los pagos guardados aparecerán aquí.",
        )
