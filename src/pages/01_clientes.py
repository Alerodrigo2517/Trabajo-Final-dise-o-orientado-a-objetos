import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.client_service import create_client, list_clients
from src.ui import (
    client_entry_rows,
    database_error,
    kpi_card,
    page_header,
    records_table,
    section_header,
)

usuario = current_user()
puede_editar = can_write(usuario)

page_header(
    "PADRÓN COMERCIAL",
    "Clientes",
    "Registrá clientes por CUIT/CUIL, consultá sus domicilios de contacto y mantené actualizado el directorio comercial.",
    insignia="Módulo Clientes",
)

clientes = []
try:
    clientes = list_clients()
except SQLAlchemyError:
    database_error()

total_clientes = len(clientes)
con_contactos = sum(1 for c in clientes if len(c.get("contactos", [])) > 0)
sin_contactos = total_clientes - con_contactos
total_contactos = sum(len(c.get("contactos", [])) for c in clientes)

indicadores = st.columns(4)
with indicadores[0]:
    kpi_card("Total clientes", total_clientes, "Registrados en el padrón", icono="👥", tono="amber")
with indicadores[1]:
    kpi_card("Con contacto activo", con_contactos, "Vinculados a presupuestos", icono="✅", tono="emerald")
with indicadores[2]:
    kpi_card("Domicilios / teléfonos", total_contactos, "Contactos registrados", icono="📍", tono="blue")
with indicadores[3]:
    kpi_card("Sin contacto aún", sin_contactos, "Se completan al presupuestar", icono="📋", tono="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if puede_editar:
    pestana_lista, pestana_nuevo = st.tabs(["📋 Directorio y contactos de clientes", "➕ Registrar nuevo cliente"])
else:
    st.info("👁️ Tu perfil puede consultar el padrón de clientes, pero no registrar ni modificar datos.")
    pestana_lista = st.container()
    pestana_nuevo = None

if pestana_nuevo is not None:
    with pestana_nuevo:
        with st.container(border=True):
            client_entry_rows(prefijo_clave="pagina_clientes")

with pestana_lista:
    if clientes:
        with st.container(border=True):
            section_header(
                "Ficha rápida de contacto por cliente",
                "Seleccioná un cliente para revisar sus domicilios, localidades y teléfonos registrados.",
                icono="📍",
                insignia="Consulta rápida",
            )
            opciones_clientes = {
                f"{cliente['cuit_display']} · {cliente['nombre_completo']}": cliente for cliente in clientes
            }
            col_selector, col_detalle = st.columns([1.15, 1.35], gap="large")
            with col_selector:
                etiqueta_seleccionada = st.selectbox(
                    "Seleccionar cliente",
                    list(opciones_clientes),
                    key="client_directory_inspect",
                )
                cliente_seleccionado = opciones_clientes[etiqueta_seleccionada]
                st.caption(
                    f"Nombre completo: **{cliente_seleccionado['nombre_completo']}** · "
                    f"CUIT: **{cliente_seleccionado['cuit_display']}**"
                )
            with col_detalle:
                contactos = cliente_seleccionado.get("contactos", [])
                if contactos:
                    st.markdown('<p class="panel-heading">DOMICILIOS Y TELÉFONOS REGISTRADOS</p>', unsafe_allow_html=True)
                    for elemento in contactos:
                        st.markdown(
                            f"- 📍 **{elemento['direccion']}**, {elemento['ciudad']} · 📞 **{elemento['telefono']}** (`#{elemento['id_contacto']}`)"
                        )
                else:
                    st.info("Este cliente todavía no tiene domicilios registrados. Se agregan automáticamente al crearle su primer presupuesto.")

    with st.container(border=True):
        section_header(
            "Padrón general de clientes",
            "Listado completo de clientes identificados por CUIT y cantidad de contactos asociados.",
            icono="📒",
            insignia=f"{total_clientes} clientes",
        )
        filas = [
            {
                "Nombre": cliente["nombre"],
                "Apellido": cliente["apellido"],
                "CUIT": cliente["cuit_display"],
                "Contactos registrados": len(cliente["contactos"]),
            }
            for cliente in clientes
        ]
        records_table(
            filas,
            "clientes",
            "Todavía no hay clientes registrados",
            "Abrí la pestaña «Registrar nuevo cliente» para dar de alta el primero.",
        )
