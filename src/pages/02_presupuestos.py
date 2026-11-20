import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.components.budget_form import mostrar_formulario_presupuesto
from src.core.authorization import puede_escribir
from src.core.session import obtener_usuario_actual
from src.services.budget_service import PRESUPUESTO_ESTADOS, listar_presupuestos, actualizar_estado_presupuesto
from src.ui import (
    formatear_moneda,
    mostrar_error_bd,
    tarjeta_indicador,
    encabezado_pagina,
    mostrar_tabla_registros,
    encabezado_seccion,
)

usuario = obtener_usuario_actual()
puede_editar = puede_escribir(usuario)

encabezado_pagina(
    "VENTAS Y COTIZACIONES",
    "Presupuestos",
    "Confeccioná cotizaciones detalladas con materiales y mano de obra, y gestioná el ciclo de aprobación comercial.",
    insignia="Módulo Comercial",
)

presupuestos = []
try:
    presupuestos = listar_presupuestos()
except SQLAlchemyError:
    mostrar_error_bd()

cantidad_total = len(presupuestos)
cantidad_aprobados = sum(1 for b in presupuestos if b["estado"] == "APROBADO")
cantidad_pendientes = sum(1 for b in presupuestos if b["estado"] in ("BORRADOR", "PENDIENTE"))
total_cotizado = sum(float(b["total_estimado"] or 0) for b in presupuestos)

indicadores = st.columns(4)
with indicadores[0]:
    tarjeta_indicador("Total presupuestos", cantidad_total, "Emitidos en el sistema", icono="📐", tono="amber")
with indicadores[1]:
    tarjeta_indicador("Aprobados", cantidad_aprobados, "Listos para producción", icono="✅", tono="emerald")
with indicadores[2]:
    tarjeta_indicador("En evaluación", cantidad_pendientes, "Borrador o pendientes", icono="⏳", tono="blue")
with indicadores[3]:
    tarjeta_indicador("Volumen cotizado", formatear_moneda(total_cotizado), "Suma total estimada", icono="💰", tono="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if puede_editar:
    pestana_lista, pestana_nuevo = st.tabs(["📋 Historial y estados de presupuestos", "➕ Crear nuevo presupuesto"])
else:
    st.info("👁️ Tu perfil puede consultar presupuestos, pero no crear ni cambiar sus estados.")
    pestana_lista = st.container()
    pestana_nuevo = None

if pestana_nuevo is not None:
    with pestana_nuevo:
        with st.container(border=True):
            mostrar_formulario_presupuesto(prefijo_clave="pagina_presupuestos")

with pestana_lista:
    if puede_editar and presupuestos:
        with st.container(border=True):
            encabezado_seccion(
                "Actualizar estado comercial",
                "Cambiá el estado de una cotización (al pasar a Aprobado se habilita su orden de trabajo).",
                icono="🔄",
                insignia="Gestión de estado",
            )
            opciones_presupuestos = {
                f"#{presupuesto['id_presupuesto']} · {presupuesto['cliente']} · {presupuesto['tipo_trabajo']} ({presupuesto['estado']})": presupuesto
                for presupuesto in presupuestos
            }
            col_selector, col_formulario = st.columns([1.3, 1], gap="large")
            with col_selector:
                etiqueta_seleccionada = st.selectbox("Seleccionar presupuesto", list(opciones_presupuestos), key="budget_status_selection")
                presupuesto_seleccionado = opciones_presupuestos[etiqueta_seleccionada]
                st.caption(
                    f"Cliente: **{presupuesto_seleccionado['cliente']}** · Total estimado: **{formatear_moneda(presupuesto_seleccionado['total_estimado'])}** · "
                    f"Saldo: **{formatear_moneda(presupuesto_seleccionado['saldo_estimado'])}**"
                )
            etiquetas = {
                "BORRADOR": "Borrador",
                "PENDIENTE": "Pendiente",
                "APROBADO": "Aprobado",
                "RECHAZADO": "Rechazado",
                "VENCIDO": "Vencido",
                "CANCELADO": "Cancelado",
            }
            with col_formulario:
                with st.form("budget_status_form"):
                    estado_nuevo = st.selectbox(
                        "Nuevo estado",
                        PRESUPUESTO_ESTADOS,
                        index=PRESUPUESTO_ESTADOS.index(presupuesto_seleccionado["estado"]),
                        format_func=lambda valor: etiquetas[valor],
                    )
                    update = st.form_submit_button("Guardar nuevo estado", type="primary", width="stretch")
                if update:
                    try:
                        actualizar_estado_presupuesto(presupuesto_seleccionado["id_presupuesto"], estado_nuevo)
                        st.success("✅ Estado del presupuesto actualizado correctamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        if isinstance(error, SQLAlchemyError):
                            mostrar_error_bd()
                        else:
                            st.error(str(error))

    with st.container(border=True):
        encabezado_seccion(
            "Registro histórico de presupuestos",
            "Detalle de costos de materiales, mano de obra, pagos acumulados y saldo estimado.",
            icono="📊",
            insignia=f"{cantidad_total} presupuestos",
        )
        filas = [
            {
                "N.º": presupuesto["id_presupuesto"],
                "Fecha": presupuesto["fecha"],
                "Cliente": presupuesto["cliente"],
                "Trabajo": presupuesto["tipo_trabajo"],
                "Ubicación": f"{presupuesto['ubicacion']}, {presupuesto['ciudad']}",
                "Estado": presupuesto["estado"].replace("_", " ").title(),
                "Materiales": formatear_moneda(presupuesto["materiales"]),
                "Mano de obra": formatear_moneda(presupuesto["mano_obra"]),
                "Total estimado": formatear_moneda(presupuesto["total_estimado"]),
                "Pagado": formatear_moneda(presupuesto["pagado"]),
                "Saldo estimado": formatear_moneda(presupuesto["saldo_estimado"]),
            }
            for presupuesto in presupuestos
        ]
        mostrar_tabla_registros(
            filas,
            "presupuestos_db",
            "Todavía no hay presupuestos registrados",
            "Abrí la pestaña «Crear nuevo presupuesto» para cargar la primera cotización.",
        )
