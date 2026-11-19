import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.services.client_service import list_clients
from src.ui import (
    client_entry_rows,
    database_error,
    kpi_card,
    page_header,
    records_table,
    section_header,
)

page_header(
    "PADRÓN COMERCIAL",
    "Gestión de Clientes",
    "Registrá clientes por CUIT/CUIL y consultá su directorio histórico y domicilios de contacto asociados.",
    badge="Módulo Clientes",
)

clients = []
try:
    clients = list_clients()
except SQLAlchemyError:
    database_error()

total_clients = len(clients)
with_contacts = sum(1 for c in clients if len(c.get("contactos", [])) > 0)
total_contacts = sum(len(c.get("contactos", [])) for c in clients)

kpis = st.columns(3)
with kpis[0]:
    kpi_card("Clientes registrados", total_clients, "Padrón activo en MySQL", icon="👥", tone="amber")
with kpis[1]:
    kpi_card("Con datos de contacto", with_contacts, "Vinculados a presupuestos", icon="📍", tone="blue")
with kpis[2]:
    kpi_card("Domicilios / teléfonos", total_contacts, "Registros en clientes_contacto", icon="📞", tone="emerald")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

with st.container(border=True):
    section_header(
        "Alta rápida de clientes",
        "Cada fila completa se valida por CUIT y se almacena directamente en la base de datos.",
        icon="➕",
        badge="Captura continua",
    )
    client_entry_rows()

with st.container(border=True):
    section_header(
        "Directorio de clientes",
        "Buscá por nombre, apellido o número de CUIT.",
        icon="📒",
        badge=f"{total_clients} registrados",
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
        "Completá la primera fila en el panel superior para dar de alta un cliente.",
    )
