import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.components.budget_form import render_budget_form
from src.core.authorization import AUDITOR, is_admin
from src.core.session import current_user, logout_user
from src.services.dashboard_service import get_dashboard_summary
from src.ui import (
    apply_theme,
    client_entry_rows,
    currency,
    database_error,
    kpi_card,
    page_header,
    render_sidebar_user,
    section_header,
)
from src.ui.login import render_login

st.set_page_config(page_title="Herrería | Gestión del taller", page_icon="🔨", layout="wide")
st.session_state["_database_error_shown"] = False
apply_theme()

user = current_user()
if user is None:
    render_login()
    st.stop()

st.sidebar.markdown(
    '<div class="brand-lockup"><span class="brand-mark">🔨</span>'
    '<span class="brand-copy"><strong>Herrería</strong><small>GESTIÓN INDUSTRIAL</small></span></div>',
    unsafe_allow_html=True,
)
render_sidebar_user(user)
if st.sidebar.button("🚪 Cerrar sesión", width="stretch"):
    logout_user()
    st.rerun()
st.sidebar.divider()


def inicio():
    page_header(
        "CENTRO DE OPERACIONES",
        f"Hola, {user['nombre']}",
        "Supervisá el estado del taller, registrá clientes al instante y confeccioná presupuestos vinculados con producción y caja.",
        badge=f"Perfil: {user['role_label']}",
    )
    try:
        summary = get_dashboard_summary()
        metrics = st.columns(4)
        with metrics[0]:
            kpi_card(
                "Presupuestos",
                summary["presupuestos_total"],
                subtitle=f"{summary['clientes']} clientes registrados",
                icon="📐",
                tone="amber",
            )
        with metrics[1]:
            kpi_card(
                "Trabajos activos",
                summary["trabajos_activos"],
                subtitle="Órdenes en fabricación",
                icon="⚙️",
                tone="blue",
            )
        with metrics[2]:
            kpi_card(
                "Trabajos terminados",
                summary["trabajos_terminados"],
                subtitle="Obras finalizadas",
                icon="✅",
                tone="emerald",
            )
        with metrics[3]:
            kpi_card(
                "Ingresos del mes",
                currency(summary["ingresos_mes"]),
                subtitle=f"{summary['materiales']} materiales en catálogo",
                icon="💳",
                tone="slate",
            )
    except SQLAlchemyError:
        database_error()

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        section_header(
            "Navegación rápida del taller",
            "Accedé directamente a los módulos operativos del sistema.",
            icon="🧭",
            badge="Módulos",
        )
        links = st.columns(5)
        for column, path, label, icon in zip(
            links,
            (
                "src/pages/02_presupuestos.py",
                "src/pages/03_materiales.py",
                "src/pages/07_proveedores.py",
                "src/pages/04_pagos.py",
                "src/pages/05_trabajos.py",
            ),
            (
                "Historial de presupuestos",
                "Catálogo de materiales",
                "Directorio de proveedores",
                "Caja y registro de pagos",
                "Órdenes de trabajo",
            ),
            ("📐", "🧱", "🏭", "💳", "🛠️"),
        ):
            column.page_link(path, label=label, icon=icon)

    if user.get("role") == AUDITOR:
        st.info("👁️ Estás en modo consulta (Auditor): podés explorar todos los módulos sin modificar registros.")
    else:
        left, right = st.columns([1, 1.15], gap="large")
        with left:
            with st.container(border=True):
                section_header(
                    "Alta rápida de Clientes",
                    "Guardado automático al completar cada fila.",
                    icon="👥",
                    badge="Clientes",
                )
                client_entry_rows()
        with right:
            with st.container(border=True):
                render_budget_form(key_prefix="inicio_presupuesto", compact=True)


paginas = {
    "Gestión del taller": [
        st.Page(inicio, title="Inicio", icon=":material/home:"),
        st.Page("src/pages/01_clientes.py", title="Clientes", icon=":material/groups:"),
        st.Page("src/pages/02_presupuestos.py", title="Presupuestos", icon=":material/request_quote:"),
        st.Page("src/pages/05_trabajos.py", title="Trabajos", icon=":material/engineering:"),
        st.Page("src/pages/04_pagos.py", title="Pagos", icon=":material/payments:"),
    ],
    "Abastecimiento": [
        st.Page("src/pages/03_materiales.py", title="Materiales", icon=":material/inventory_2:"),
        st.Page("src/pages/07_proveedores.py", title="Proveedores", icon=":material/factory:"),
    ],
}
if is_admin(user):
    paginas["Administración"] = [
        st.Page("src/pages/06_usuarios.py", title="Usuarios", icon=":material/manage_accounts:")
    ]

pagina = st.navigation(paginas)
pagina.run()
