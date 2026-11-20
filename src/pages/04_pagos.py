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

puede_editar = can_write(current_user())
page_header(
    "TESORERÍA Y COBRANZAS",
    "Pagos",
    "Registrá cobros parciales o totales asociados a cada presupuesto y consultá el estado de cuenta de cada obra.",
    insignia="Módulo Caja",
)

presupuestos = []
pagos = []
try:
    presupuestos = list_budgets()
    pagos = list_payments()
except SQLAlchemyError:
    database_error()

total_cobrado = sum(float(p["monto"] or 0) for p in pagos)
saldos_pendientes = sum(max(0.0, float(b["saldo_estimado"] or 0)) for b in presupuestos if b["estado"] == "APROBADO")
presupuestos_con_saldo = sum(1 for b in presupuestos if float(b["saldo_estimado"] or 0) > 0 and b["estado"] == "APROBADO")
pago_promedio = (total_cobrado / len(pagos)) if pagos else 0.0

indicadores = st.columns(4)
with indicadores[0]:
    kpi_card("Total cobrado", currency(total_cobrado), "Ingresos acumulados en caja", icono="💳", tono="emerald")
with indicadores[1]:
    kpi_card("Saldo por cobrar", currency(saldos_pendientes), f"En {presupuestos_con_saldo} presupuestos aprobados", icono="⏳", tono="amber")
with indicadores[2]:
    kpi_card("Cobros registrados", len(pagos), "Comprobantes asentados", icono="🧾", tono="blue")
with indicadores[3]:
    kpi_card("Cobro promedio", currency(pago_promedio), "Ticket medio por operación", icono="📊", tono="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if puede_editar:
    pestana_lista, pestana_nuevo = st.tabs(["📋 Historial de pagos y estado de cuenta", "➕ Registrar nuevo cobro"])
else:
    st.info("👁️ Tu perfil puede consultar el historial de cobros, pero no registrar nuevos pagos.")
    pestana_lista = st.container()
    pestana_nuevo = None

if pestana_nuevo is not None:
    with pestana_nuevo:
        with st.container(border=True):
            section_header(
                "Registrar un cobro",
                "Seleccioná el presupuesto a imputar, verificá su saldo pendiente y asentá el pago recibido.",
                icono="💵",
                insignia="Ingreso de caja",
            )
            if presupuestos:
                opciones_presupuestos = {
                    f"#{fila['id_presupuesto']} · {fila['cliente']} · {fila['tipo_trabajo']} (Saldo: {currency(fila['saldo_estimado'])})": fila
                    for fila in presupuestos
                }
                etiqueta_seleccionada = st.selectbox(
                    "1. Seleccionar presupuesto a imputar",
                    list(opciones_presupuestos),
                    key="payment_budget_sel",
                )
                presupuesto_seleccionado = opciones_presupuestos[etiqueta_seleccionada]

                with st.form("payment_form"):
                    st.markdown('<p class="panel-heading">ESTADO DE CUENTA DEL PRESUPUESTO</p>', unsafe_allow_html=True)
                    b_col1, b_col2, b_col3 = st.columns(3)
                    with b_col1:
                        st.text_input("Cliente", value=presupuesto_seleccionado["cliente"], disabled=True)
                    with b_col2:
                        st.text_input("Total presupuestado", value=currency(presupuesto_seleccionado["total_estimado"]), disabled=True)
                    with b_col3:
                        st.text_input("Saldo estimado pendiente", value=currency(presupuesto_seleccionado["saldo_estimado"]), disabled=True)

                    st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">DETALLES DEL COBRO</p>', unsafe_allow_html=True)
                    p_col1, p_col2 = st.columns(2)
                    with p_col1:
                        fecha_pago = st.date_input("Fecha del pago", value=date.today())
                        monto = st.number_input("Monto recibido (ARS $)", min_value=0.0, value=0.0, step=1000.0)
                    with p_col2:
                        metodo = st.selectbox("Medio de pago", ["Efectivo", "Transferencia", "Tarjeta", "Otro"])
                        referencia = st.text_input(
                            "N.º de comprobante o referencia (opcional)",
                            max_chars=100,
                            placeholder="Ej. Transferencia CBU #48291",
                        )
                    enviado = st.form_submit_button("💾 Guardar pago", type="primary", width="stretch")
                if enviado:
                    try:
                        id_pago = create_payment(
                            id_presupuesto=presupuesto_seleccionado["id_presupuesto"],
                            fecha_pago=fecha_pago,
                            monto=monto,
                            metodo=metodo,
                            referencia=referencia,
                        )
                        st.success(f"✅ Pago #{id_pago} registrado exitosamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("Creá primero un presupuesto para poder asociar un pago.")
                st.page_link("src/pages/02_presupuestos.py", label="Ir a Presupuestos", icon="📐")

with pestana_lista:
    if presupuestos:
        with st.container(border=True):
            section_header(
                "Consulta rápida de saldo por presupuesto",
                "Revisá cuánto se cobró y cuánto resta abonar en cualquier cotización.",
                icono="🔎",
                insignia="Estado de cuenta",
            )
            opciones_inspeccion = {
                f"#{fila['id_presupuesto']} · {fila['cliente']} · {fila['tipo_trabajo']}": fila
                for fila in presupuestos
            }
            col_selector, col_resumen = st.columns([1.15, 1.35], gap="large")
            with col_selector:
                etiqueta_inspeccion = st.selectbox(
                    "Presupuesto a consultar",
                    list(opciones_inspeccion),
                    key="payment_inspect_budget",
                )
                inspeccionado = opciones_inspeccion[etiqueta_inspeccion]
                st.caption(
                    f"Estado comercial: **{inspeccionado['estado'].replace('_', ' ').title()}** · "
                    f"Fecha: **{inspeccionado['fecha']}**"
                )
            with col_resumen:
                m1, m2, m3 = st.columns(3)
                m1.metric("Total estimado", currency(inspeccionado["total_estimado"]))
                m2.metric("Pagado", currency(inspeccionado["pagado"]))
                m3.metric("Saldo pendiente", currency(inspeccionado["saldo_estimado"]))

    with st.container(border=True):
        section_header(
            "Registro histórico de pagos",
            "Detalle de todos los cobros asentados con su fecha, cliente, monto, medio de pago y comprobante.",
            icono="📊",
            insignia=f"{len(pagos)} pagos",
        )
        filas_pagos = [
            {
                "N.º": fila["id_pago"],
                "Fecha": fila["fecha"],
                "Presupuesto": f"#{fila['id_presupuesto']}",
                "Cliente": fila["cliente"],
                "Monto": currency(fila["monto"]),
                "Método": fila["metodo"],
                "Referencia": fila["referencia"],
            }
            for fila in pagos
        ]
        records_table(
            filas_pagos,
            "payments",
            "Todavía no hay pagos registrados",
            "Abrí la pestaña «Registrar nuevo cobro» para cargar el primer movimiento de caja.",
        )
