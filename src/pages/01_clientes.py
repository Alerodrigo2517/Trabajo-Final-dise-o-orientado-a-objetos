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

user = current_user()
can_edit = can_write(user)

page_header(
    "PADRÓN COMERCIAL",
    "Clientes",
    "Registrá clientes por CUIT/CUIL, consultá sus domicilios de contacto y mantené actualizado el directorio comercial.",
    badge="Módulo Clientes",
)

clients = []
try:
    clients = list_clients()
except SQLAlchemyError:
    database_error()

total_clients = len(clients)
with_contacts = sum(1 for c in clients if len(c.get("contactos", [])) > 0)
without_contacts = total_clients - with_contacts
total_contacts = sum(len(c.get("contactos", [])) for c in clients)

kpis = st.columns(4)
with kpis[0]:
    kpi_card("Total clientes", total_clients, "Registrados en el padrón", icon="👥", tone="amber")
with kpis[1]:
    kpi_card("Con contacto activo", with_contacts, "Vinculados a presupuestos", icon="✅", tone="emerald")
with kpis[2]:
    kpi_card("Domicilios / teléfonos", total_contacts, "En clientes_contacto", icon="📍", tone="blue")
with kpis[3]:
    kpi_card("Sin contacto aún", without_contacts, "Se completan al presupuestar", icon="📋", tone="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    tab_list, tab_new = st.tabs(["📋 Directorio y contactos de clientes", "➕ Registrar nuevo cliente"])
else:
    st.info("👁️ Tu perfil puede consultar el padrón de clientes, pero no registrar ni modificar datos.")
    tab_list = st.container()
    tab_new = None

if tab_new is not None:
    with tab_new:
        with st.container(border=True):
            client_entry_rows(key_prefix="pagina_clientes")

with tab_list:
    if clients:
        with st.container(border=True):
            section_header(
                "Ficha rápida de contacto por cliente",
                "Seleccioná un cliente para revisar sus domicilios, localidades y teléfonos registrados.",
                icon="📍",
                badge="Consulta rápida",
            )
            client_options = {
                f"{client['cuit_display']} · {client['nombre_completo']}": client for client in clients
            }
            col_sel, col_detail = st.columns([1.15, 1.35], gap="large")
            with col_sel:
                selected_label = st.selectbox(
                    "Seleccionar cliente",
                    list(client_options),
                    key="client_directory_inspect",
                )
                selected_client = client_options[selected_label]
                st.caption(
                    f"Nombre completo: **{selected_client['nombre_completo']}** · "
                    f"CUIT: **{selected_client['cuit_display']}**"
                )
            with col_detail:
                contacts = selected_client.get("contactos", [])
                if contacts:
                    st.markdown('<p class="panel-heading">DOMICILIOS Y TELÉFONOS REGISTRADOS</p>', unsafe_allow_html=True)
                    for item in contacts:
                        st.markdown(
                            f"- 📍 **{item['direccion']}**, {item['ciudad']} · 📞 **{item['telefono']}** (`#{item['id_contacto']}`)"
                        )
                else:
                    st.info("Este cliente todavía no tiene domicilios registrados. Se agregan automáticamente al crearle su primer presupuesto.")

    with st.container(border=True):
        section_header(
            "Padrón general de clientes",
            "Listado completo de clientes identificados por CUIT y cantidad de contactos asociados.",
            icon="📒",
            badge=f"{total_clients} clientes",
        )
        rows = [
            {
                "Nombre": client["nombre"],
                "Apellido": client["apellido"],
                "CUIT": client["cuit_display"],
                "Contactos registrados": len(client["contactos"]),
            }
            for client in clients
        ]
        records_table(
            rows,
            "clientes",
            "Todavía no hay clientes registrados",
            "Abrí la pestaña «Registrar nuevo cliente» para cargar el primero en la base de datos.",
        )
