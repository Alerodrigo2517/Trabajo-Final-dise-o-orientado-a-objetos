from datetime import date

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.budget_service import list_budgets
from src.services.work_service import ESTADOS_TRABAJO, create_work, list_works, update_work
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
    "TALLER Y PRODUCCIÓN",
    "Órdenes de Trabajo",
    "Iniciá órdenes de fabricación a partir de presupuestos aprobados y gestioná el avance de obra hasta su finalización.",
    insignia="Módulo Producción",
)

presupuestos = []
trabajos = []
try:
    presupuestos = list_budgets()
    trabajos = list_works()
except SQLAlchemyError:
    database_error()

elegible = [presupuesto for presupuesto in presupuestos if presupuesto["estado"] == "APROBADO" and presupuesto["trabajo_id"] is None]
trabajos_activos = sum(1 for w in trabajos if w["estado"] in ("PENDIENTE", "EN_PROCESO"))
trabajos_terminados = sum(1 for w in trabajos if w["estado"] in ("FINALIZADO", "ENTREGADO", "TERMINADO"))

indicadores = st.columns(4)
with indicadores[0]:
    kpi_card("Total órdenes", len(trabajos), "Registradas en el taller", icono="🛠️", tono="amber")
with indicadores[1]:
    kpi_card("Finalizadas", trabajos_terminados, "Trabajos concluidos", icono="✅", tono="emerald")
with indicadores[2]:
    kpi_card("En fabricación", trabajos_activos, "Pendientes o en proceso", icono="⚙️", tono="blue")
with indicadores[3]:
    kpi_card("Listos para iniciar", len(elegible), "Presupuestos aprobados sin orden", icono="🚀", tono="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if puede_editar:
    pestana_lista, pestana_nuevo = st.tabs(
        [
            "📋 Historial y estados de órdenes",
            f"➕ Iniciar nueva orden de trabajo ({len(elegible)})",
        ]
    )
else:
    st.info("👁️ Tu perfil puede consultar las órdenes de trabajo, pero no crear órdenes ni cambiar sus estados.")
    pestana_lista = st.container()
    pestana_nuevo = None

if pestana_nuevo is not None:
    with pestana_nuevo:
        with st.container(border=True):
            section_header(
                "Apertura de orden de trabajo",
                "Seleccioná un presupuesto aprobado para generar su orden de fabricación en el taller.",
                icono="🚀",
                insignia=f"{len(elegible)} presupuestos disponibles",
            )
            if elegible:
                opciones_presupuestos = {
                    f"#{presupuesto['id_presupuesto']} · {presupuesto['cliente']} · {presupuesto['tipo_trabajo']} ({currency(presupuesto['total_estimado'])})": presupuesto
                    for presupuesto in elegible
                }
                etiqueta_presupuesto_seleccionado = st.selectbox(
                    "1. Seleccionar presupuesto aprobado",
                    list(opciones_presupuestos),
                    key="create_work_budget_selector",
                )
                presupuesto_objetivo = opciones_presupuestos[etiqueta_presupuesto_seleccionado]

                with st.form("create_work_form"):
                    st.markdown('<p class="panel-heading">RESUMEN DEL PRESUPUESTO VINCULADO</p>', unsafe_allow_html=True)
                    info_c1, info_c2 = st.columns(2)
                    with info_c1:
                        st.text_input("Cliente", value=presupuesto_objetivo["cliente"], disabled=True)
                        st.text_input("Tipo de trabajo", value=presupuesto_objetivo["tipo_trabajo"], disabled=True)
                    with info_c2:
                        st.text_input(
                            "Ubicación de obra",
                            value=f"{presupuesto_objetivo['ubicacion']}, {presupuesto_objetivo['ciudad']}",
                            disabled=True,
                        )
                        st.text_input(
                            "Total presupuestado",
                            value=currency(presupuesto_objetivo["total_estimado"]),
                            disabled=True,
                        )

                    st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">PLANIFICACIÓN DE TALLER</p>', unsafe_allow_html=True)
                    fecha_inicio = st.date_input("Fecha programada de inicio", value=date.today())
                    observaciones = st.text_area(
                        "Observaciones e instrucciones de fabricación",
                        max_chars=500,
                        height=95,
                        placeholder="Prioridad, operario asignado, detalles de corte, soldadura o montaje en obra…",
                    )
                    create = st.form_submit_button("🛠️ Crear orden de trabajo", type="primary", width="stretch")
                if create:
                    try:
                        id_trabajo = create_work(
                            id_presupuesto=presupuesto_objetivo["id_presupuesto"],
                            fecha_inicio=fecha_inicio,
                            observaciones=observaciones,
                        )
                        st.success(f"✅ Orden de trabajo #{id_trabajo} creada exitosamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("No hay presupuestos aprobados pendientes de iniciar orden. Aprobá primero una cotización en la sección Presupuestos.")
                st.page_link("src/pages/02_presupuestos.py", label="Ir a Presupuestos", icon="📐")

with pestana_lista:
    if puede_editar and trabajos:
        with st.container(border=True):
            section_header(
                "Actualizar estado y seguimiento de orden",
                "Modificá la etapa de producción, fechas de ejecución y notas técnicas de una orden activa.",
                icono="🔄",
                insignia="Gestión de estado",
            )
            opciones_trabajos = {
                f"#{trabajo['id_trabajo']} · {trabajo['cliente']} · {trabajo['trabajo']} ({trabajo['estado'].replace('_', ' ').title()})": trabajo
                for trabajo in trabajos
            }
            col_selector, col_formulario = st.columns([1.15, 1.35], gap="large")
            with col_selector:
                etiqueta_seleccionada = st.selectbox("Seleccionar orden de trabajo", list(opciones_trabajos), key="work_update_selection")
                trabajo_seleccionado = opciones_trabajos[etiqueta_seleccionada]
                st.caption(
                    f"Presupuesto: **#{trabajo_seleccionado['id_presupuesto']}** · Cliente: **{trabajo_seleccionado['cliente']}** · "
                    f"Ubicación: **{trabajo_seleccionado['ubicacion']}, {trabajo_seleccionado['ciudad']}**"
                )
                finalizar = st.checkbox(
                    "Incluir fecha de finalización",
                    value=trabajo_seleccionado["fecha_fin"] is not None,
                    key=f"work_finish_{trabajo_seleccionado['id_trabajo']}",
                )
                fecha_fin = trabajo_seleccionado["fecha_fin"] if finalizar else None
                if finalizar:
                    fecha_fin = st.date_input(
                        "Fecha de finalización",
                        value=trabajo_seleccionado["fecha_fin"] or date.today(),
                        key=f"work_end_{trabajo_seleccionado['id_trabajo']}",
                    )

            with col_formulario:
                with st.form(f"work_update_form_{trabajo_seleccionado['id_trabajo']}"):
                    f_col1, f_col2 = st.columns(2)
                    with f_col1:
                        estado = st.selectbox(
                            "Nuevo estado",
                            ESTADOS_TRABAJO,
                            index=ESTADOS_TRABAJO.index(trabajo_seleccionado["estado"]),
                            format_func=lambda valor: valor.replace("_", " ").title(),
                        )
                    with f_col2:
                        fecha_inicio = st.date_input(
                            "Fecha de inicio",
                            value=trabajo_seleccionado["fecha_inicio"] or date.today(),
                            key=f"work_start_{trabajo_seleccionado['id_trabajo']}",
                        )
                    observaciones = st.text_area(
                        "Observaciones de avance",
                        value=trabajo_seleccionado["observaciones"],
                        max_chars=500,
                        height=75,
                        key=f"work_observations_{trabajo_seleccionado['id_trabajo']}",
                    )
                    update = st.form_submit_button("Guardar cambios de la orden", type="primary", width="stretch")
                if update:
                    try:
                        update_work(
                            id_trabajo=trabajo_seleccionado["id_trabajo"],
                            estado=estado,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            observaciones=observaciones,
                        )
                        st.success("✅ Orden de trabajo actualizada correctamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))

    with st.container(border=True):
        section_header(
            "Registro histórico de órdenes de trabajo",
            "Listado completo de trabajos con sus fechas de inicio, finalización y estado actual.",
            icono="📊",
            insignia=f"{len(trabajos)} órdenes",
        )
        filas_trabajos = [
            {
                "N.º": trabajo["id_trabajo"],
                "Presupuesto": f"#{trabajo['id_presupuesto']}",
                "Cliente": trabajo["cliente"],
                "Trabajo": trabajo["trabajo"],
                "Ubicación": f"{trabajo['ubicacion']}, {trabajo['ciudad']}",
                "Inicio": trabajo["fecha_inicio"],
                "Fin": trabajo["fecha_fin"] or "En curso",
                "Estado": trabajo["estado"].replace("_", " ").title(),
            }
            for trabajo in trabajos
        ]
        records_table(
            filas_trabajos,
            "works",
            "Todavía no hay órdenes de trabajo registradas",
            "Abrí la pestaña «Iniciar nueva orden de trabajo» para poner en marcha un presupuesto aprobado.",
        )
