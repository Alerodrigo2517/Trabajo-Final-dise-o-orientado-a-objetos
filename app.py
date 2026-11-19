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

st.set_page_config(
    page_title="Herrería Don Francisco | Gestión del taller",
    page_icon="src/assets/logo_don_francisco.png",
    layout="wide",
)
st.session_state["_database_error_shown"] = False
apply_theme()

user = current_user()
if user is None:
    render_login()
    st.stop()

st.sidebar.divider()
render_sidebar_user(user)
if st.sidebar.button("🚪 Cerrar sesión", width="stretch"):
    logout_user()
    st.rerun()


def inicio():
    page_header(
        "CENTRO DE OPERACIONES",
        f"Hola, {user['nombre']}",
        "Supervisá el estado del taller, confeccioná presupuestos vinculados con producción y registrá clientes en un solo lugar.",
        badge=f"Perfil: {user['role_label']}",
        show_logo=True,
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

    if user.get("role") == AUDITOR:
        st.info("👁️ Estás en modo consulta (Auditor): podés explorar todos los módulos sin modificar registros.")
        tab_modules = st.container()
        tab_budget = None
        tab_client = None
    else:
        tab_budget, tab_client, tab_modules = st.tabs(
            [
                "📐 Crear presupuesto rápido",
                "👥 Alta rápida de clientes",
                "🧭 Accesos directos del taller",
            ]
        )

    if tab_budget is not None:
        with tab_budget:
            with st.container(border=True):
                render_budget_form(key_prefix="inicio_presupuesto", compact=False)

    if tab_client is not None:
        with tab_client:
            with st.container(border=True):
                client_entry_rows(key_prefix="inicio_clientes")

    with tab_modules:
        with st.container(border=True):
            section_header(
                "Módulos operativos del taller",
                "Accedé directamente a cada sección de gestión comercial, producción y abastecimiento.",
                icon="🧭",
                badge="Navegación",
            )
            row1 = st.columns(3, gap="medium")
            with row1[0]:
                st.markdown('<p class="panel-heading">COMERCIAL</p>', unsafe_allow_html=True)
                st.page_link("src/pages/01_clientes.py", label="Padrón de Clientes", icon="👥")
                st.caption("Consulta de clientes, CUIT y domicilios asociados.")
            with row1[1]:
                st.markdown('<p class="panel-heading">COTIZACIONES</p>', unsafe_allow_html=True)
                st.page_link("src/pages/02_presupuestos.py", label="Historial de Presupuestos", icon="📐")
                st.caption("Creación de presupuestos y actualización de estados.")
            with row1[2]:
                st.markdown('<p class="panel-heading">PRODUCCIÓN</p>', unsafe_allow_html=True)
                st.page_link("src/pages/05_trabajos.py", label="Órdenes de Trabajo", icon="🛠️")
                st.caption("Seguimiento de fabricación y fechas de entrega.")

            st.divider()
            row2 = st.columns(3, gap="medium")
            with row2[0]:
                st.markdown('<p class="panel-heading">TESORERÍA</p>', unsafe_allow_html=True)
                st.page_link("src/pages/04_pagos.py", label="Caja y Pagos", icon="💳")
                st.caption("Registro de cobros, anticipos y saldos pendientes.")
            with row2[1]:
                st.markdown('<p class="panel-heading">INSUMOS</p>', unsafe_allow_html=True)
                st.page_link("src/pages/03_materiales.py", label="Catálogo de Materiales", icon="🧱")
                st.caption("Precios unitarios de referencia para cotizar.")
            with row2[2]:
                st.markdown('<p class="panel-heading">COMPRAS</p>', unsafe_allow_html=True)
                st.page_link("src/pages/07_proveedores.py", label="Directorio de Proveedores", icon="🏭")
                st.caption("Empresas proveedoras, rubros y teléfonos.")


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
