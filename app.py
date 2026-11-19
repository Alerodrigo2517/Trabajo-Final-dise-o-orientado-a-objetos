import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.components.budget_form import render_budget_form
from src.core.authorization import AUDITOR, is_admin
from src.core.session import current_user, logout_user
from src.services.dashboard_service import get_dashboard_summary
from src.ui import apply_theme, client_entry_rows, currency, database_error, page_header
from src.ui.login import render_login

st.set_page_config(page_title="Herrería | Gestión del taller", page_icon="🔨", layout="wide")
st.session_state["_database_error_shown"] = False
apply_theme()

st.sidebar.markdown("# 🔨 Herrería")
st.sidebar.caption("GESTIÓN DEL TALLER")
st.sidebar.divider()

user = current_user()
if user is None:
    render_login()
    st.stop()

st.sidebar.caption(f"Sesión iniciada: **{user['nombre']}**")
st.sidebar.caption(f"Perfil: {user['role_label']}")
if st.sidebar.button("Cerrar sesión", width="stretch"):
    logout_user()
    st.rerun()


def inicio():
    page_header("OPERACIÓN DEL TALLER", "Sistema de Herrería", "Registrá clientes y prepará presupuestos vinculados con los datos del esquema actual.")
    try:
        summary = get_dashboard_summary()
        metrics = st.columns(4)
        metrics[0].metric("Presupuestos pendientes", summary["presupuestos_pendientes"])
        metrics[1].metric("Trabajos activos", summary["trabajos_activos"])
        metrics[2].metric("Trabajos terminados", summary["trabajos_terminados"])
        metrics[3].metric("Ingresos del mes", currency(summary["ingresos_mes"]))
        st.caption(f"{summary['clientes']} clientes · {summary['materiales']} materiales registrados")
    except SQLAlchemyError:
        database_error()

    if user.get("role") == AUDITOR:
        st.info("Estás en modo consulta: podés revisar la información sin modificarla.")
    else:
        left, right = st.columns([1.05, 1], gap="large")
        with left:
            with st.container(border=True):
                st.markdown('<p class="panel-heading">CLIENTES</p>', unsafe_allow_html=True)
                client_entry_rows()
        with right:
            with st.container(border=True):
                render_budget_form(key_prefix="inicio_presupuesto", compact=True)

    with st.expander("Otras secciones"):
        links = st.columns(4)
        for column, path, label in zip(
            links,
            ("src/pages/03_materiales.py", "src/pages/04_pagos.py", "src/pages/05_trabajos.py", "src/pages/02_presupuestos.py"),
            ("Materiales", "Pagos", "Trabajos", "Historial de presupuestos"),
        ):
            column.page_link(path, label=label)


paginas = [
    st.Page(inicio, title="Inicio", icon="🏠"),
    st.Page("src/pages/01_clientes.py", title="Clientes", icon="👥"),
    st.Page("src/pages/02_presupuestos.py", title="Presupuestos", icon="📄"),
    st.Page("src/pages/03_materiales.py", title="Materiales y proveedores", icon="🧰"),
    st.Page("src/pages/04_pagos.py", title="Pagos", icon="💳"),
    st.Page("src/pages/05_trabajos.py", title="Trabajos", icon="🛠️"),
]
if is_admin(user):
    paginas.append(st.Page("src/pages/06_usuarios.py", title="Usuarios", icon="🔐"))

pagina = st.navigation(paginas)
pagina.run()

