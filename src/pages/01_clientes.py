import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.services.client_service import list_clients
from src.ui import client_entry_rows, database_error, page_header, records_table

page_header("PERSONAS Y EMPRESAS", "Clientes", "El CUIT identifica a cada cliente; los datos de contacto se guardan al preparar un presupuesto.")

with st.container(border=True):
    client_entry_rows()

st.subheader("Directorio de clientes")
try:
    clients = list_clients()
    rows = [
        {
            "Nombre": client["nombre"],
            "Apellido": client["apellido"],
            "CUIT": client["cuit_display"],
            "Contactos registrados": len(client["contactos"]),
        }
        for client in clients
    ]
    records_table(rows, "clientes", "Todavía no hay clientes", "Al completar una fila, el cliente se guarda en MySQL.")
except SQLAlchemyError:
    database_error()
