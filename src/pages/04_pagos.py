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
    "Pagos",
    "Registrá cobros parciales o totales asociados a cada presupuesto y consultá el estado de cuenta de cada obra.",
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
avg_payment = (total_collected / len(payments)) if payments else 0.0

kpis = st.columns(4)
with kpis[0]:
    kpi_card("Total cobrado", currency(total_collected), "Ingresos acumulados en caja", icon="💳", tone="emerald")
with kpis[1]:
    kpi_card("Saldo por cobrar", currency(pending_balances), f"En {budgets_with_debt} presupuestos aprobados", icon="⏳", tone="amber")
with kpis[2]:
    kpi_card("Cobros registrados", len(payments), "Comprobantes asentados", icon="🧾", tone="blue")
with kpis[3]:
    kpi_card("Cobro promedio", currency(avg_payment), "Ticket medio por operación", icon="📊", tone="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    tab_list, tab_new = st.tabs(["📋 Historial de pagos y estado de cuenta", "➕ Registrar nuevo cobro"])
else:
    st.info("👁️ Tu perfil puede consultar el historial de cobros, pero no registrar nuevos pagos.")
    tab_list = st.container()
    tab_new = None

if tab_new is not None:
    with tab_new:
        with st.container(border=True):
            section_header(
                "Registrar un cobro",
                "Seleccioná el presupuesto a imputar, verificá su saldo pendiente y asentá el pago recibido.",
                icon="💵",
                badge="Ingreso de caja",
            )
            if budgets:
                budget_options = {
                    f"#{row['id_presupuesto']} · {row['cliente']} · {row['tipo_trabajo']} (Saldo: {currency(row['saldo_estimado'])})": row
                    for row in budgets
                }
                selected_label = st.selectbox(
                    "1. Seleccionar presupuesto a imputar",
                    list(budget_options),
                    key="payment_budget_sel",
                )
                sel_budget = budget_options[selected_label]

                with st.form("payment_form"):
                    st.markdown('<p class="panel-heading">ESTADO DE CUENTA DEL PRESUPUESTO</p>', unsafe_allow_html=True)
                    b_col1, b_col2, b_col3 = st.columns(3)
                    with b_col1:
                        st.text_input("Cliente", value=sel_budget["cliente"], disabled=True)
                    with b_col2:
                        st.text_input("Total presupuestado", value=currency(sel_budget["total_estimado"]), disabled=True)
                    with b_col3:
                        st.text_input("Saldo estimado pendiente", value=currency(sel_budget["saldo_estimado"]), disabled=True)

                    st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">DETALLES DEL COBRO</p>', unsafe_allow_html=True)
                    p_col1, p_col2 = st.columns(2)
                    with p_col1:
                        payment_date = st.date_input("Fecha del pago", value=date.today())
                        amount = st.number_input("Monto recibido (ARS $)", min_value=0.0, value=0.0, step=1000.0)
                    with p_col2:
                        method = st.selectbox("Medio de pago", ["Efectivo", "Transferencia", "Tarjeta", "Otro"])
                        reference = st.text_input(
                            "N.º de comprobante o referencia (opcional)",
                            max_chars=100,
                            placeholder="Ej. Transferencia CBU #48291",
                        )
                    submitted = st.form_submit_button("💾 Guardar pago", type="primary", width="stretch")
                if submitted:
                    try:
                        payment_id = create_payment(
                            budget_id=sel_budget["id_presupuesto"],
                            payment_date=payment_date,
                            amount=amount,
                            method=method,
                            reference=reference,
                        )
                        st.success(f"✅ Pago #{payment_id} registrado exitosamente en la base de datos.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("Creá primero un presupuesto para poder asociar un pago.")
                st.page_link("src/pages/02_presupuestos.py", label="Ir a Presupuestos", icon="📐")

with tab_list:
    if budgets:
        with st.container(border=True):
            section_header(
                "Consulta rápida de saldo por presupuesto",
                "Revisá cuánto se cobró y cuánto resta abonar en cualquier cotización.",
                icon="🔎",
                badge="Estado de cuenta",
            )
            inspect_options = {
                f"#{row['id_presupuesto']} · {row['cliente']} · {row['tipo_trabajo']}": row
                for row in budgets
            }
            col_sel, col_summary = st.columns([1.15, 1.35], gap="large")
            with col_sel:
                inspect_label = st.selectbox(
                    "Presupuesto a consultar",
                    list(inspect_options),
                    key="payment_inspect_budget",
                )
                inspected = inspect_options[inspect_label]
                st.caption(
                    f"Estado comercial: **{inspected['estado'].replace('_', ' ').title()}** · "
                    f"Fecha: **{inspected['fecha']}**"
                )
            with col_summary:
                m1, m2, m3 = st.columns(3)
                m1.metric("Total estimado", currency(inspected["total_estimado"]))
                m2.metric("Pagado", currency(inspected["pagado"]))
                m3.metric("Saldo pendiente", currency(inspected["saldo_estimado"]))

    with st.container(border=True):
        section_header(
            "Registro histórico de pagos",
            "Detalle de todos los cobros asentados con su fecha, cliente, monto, medio de pago y comprobante.",
            icon="📊",
            badge=f"{len(payments)} pagos",
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
            "Abrí la pestaña «Registrar nuevo cobro» para cargar el primer movimiento de caja.",
        )
