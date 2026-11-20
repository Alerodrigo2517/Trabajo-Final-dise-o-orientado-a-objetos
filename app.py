import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.components.budget_form import mostrar_formulario_presupuesto
from src.core.authorization import AUDITOR, es_administrador
from src.core.session import obtener_usuario_actual, cerrar_sesion_usuario
from src.services.dashboard_service import obtener_resumen_panel
from src.ui import (
    aplicar_tema,
    mostrar_alta_cliente,
    formatear_moneda,
    mostrar_error_bd,
    tarjeta_indicador,
    encabezado_pagina,
    mostrar_usuario_lateral,
    encabezado_seccion,
)
from src.ui.login import mostrar_inicio_sesion

st.set_page_config(
    page_title="Herrería Don Francisco | Gestión del taller",
    page_icon="src/assets/logo_don_francisco.png",
    layout="wide",
)
st.session_state["_database_error_shown"] = False
aplicar_tema()

usuario = obtener_usuario_actual()
if usuario is None:
    mostrar_inicio_sesion()
    st.stop()

st.sidebar.divider()
mostrar_usuario_lateral(usuario)
if st.sidebar.button("🚪 Cerrar sesión", width="stretch"):
    cerrar_sesion_usuario()
    st.rerun()


def inicio():
    encabezado_pagina(
        "CENTRO DE OPERACIONES",
        f"Hola, {usuario['nombre']}",
        "Supervisá el estado del taller, confeccioná presupuestos vinculados con producción y registrá clientes en un solo lugar.",
        insignia=f"Perfil: {usuario['role_label']}",
        mostrar_logo=True,
    )
    try:
        resumen = obtener_resumen_panel()
        indicadores = st.columns(4)
        with indicadores[0]:
            tarjeta_indicador(
                "Presupuestos",
                resumen["presupuestos_total"],
                subtitulo=f"{resumen['clientes']} clientes registrados",
                icono="📐",
                tono="amber",
            )
        with indicadores[1]:
            tarjeta_indicador(
                "Trabajos activos",
                resumen["trabajos_activos"],
                subtitulo="Órdenes en fabricación",
                icono="⚙️",
                tono="blue",
            )
        with indicadores[2]:
            tarjeta_indicador(
                "Trabajos terminados",
                resumen["trabajos_terminados"],
                subtitulo="Obras finalizadas",
                icono="✅",
                tono="emerald",
            )
        with indicadores[3]:
            tarjeta_indicador(
                "Ingresos del mes",
                formatear_moneda(resumen["ingresos_mes"]),
                subtitulo=f"{resumen['materiales']} materiales en catálogo",
                icono="💳",
                tono="slate",
            )
    except SQLAlchemyError:
        mostrar_error_bd()

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    if usuario.get("role") == AUDITOR:
        st.info("👁️ Estás en modo consulta (Auditor): podés explorar todos los módulos sin modificar registros.")
        pestana_modulos = st.container()
        pestana_presupuesto = None
        pestana_cliente = None
    else:
        pestana_presupuesto, pestana_cliente, pestana_modulos = st.tabs(
            [
                "📐 Crear presupuesto rápido",
                "👥 Alta rápida de clientes",
                "🧭 Accesos directos del taller",
            ]
        )

    if pestana_presupuesto is not None:
        with pestana_presupuesto:
            with st.container(border=True):
                mostrar_formulario_presupuesto(prefijo_clave="inicio_presupuesto", compacto=False)

    if pestana_cliente is not None:
        with pestana_cliente:
            with st.container(border=True):
                mostrar_alta_cliente(prefijo_clave="inicio_clientes")

    with pestana_modulos:
        with st.container(border=True):
            encabezado_seccion(
                "Módulos operativos del taller",
                "Accedé directamente a cada sección de gestión comercial, producción y abastecimiento.",
                icono="🧭",
                insignia="Navegación",
            )
            fila1 = st.columns(3, gap="medium")
            with fila1[0]:
                st.markdown('<p class="panel-heading">COMERCIAL</p>', unsafe_allow_html=True)
                st.page_link("src/pages/01_clientes.py", label="Padrón de Clientes", icon="👥")
                st.caption("Consulta de clientes, CUIT y domicilios asociados.")
            with fila1[1]:
                st.markdown('<p class="panel-heading">COTIZACIONES</p>', unsafe_allow_html=True)
                st.page_link("src/pages/02_presupuestos.py", label="Historial de Presupuestos", icon="📐")
                st.caption("Creación de presupuestos y actualización de estados.")
            with fila1[2]:
                st.markdown('<p class="panel-heading">PRODUCCIÓN</p>', unsafe_allow_html=True)
                st.page_link("src/pages/05_trabajos.py", label="Órdenes de Trabajo", icon="🛠️")
                st.caption("Seguimiento de fabricación y fechas de entrega.")

            st.divider()
            fila2 = st.columns(3, gap="medium")
            with fila2[0]:
                st.markdown('<p class="panel-heading">TESORERÍA</p>', unsafe_allow_html=True)
                st.page_link("src/pages/04_pagos.py", label="Caja y Pagos", icon="💳")
                st.caption("Registro de cobros, anticipos y saldos pendientes.")
            with fila2[1]:
                st.markdown('<p class="panel-heading">INSUMOS</p>', unsafe_allow_html=True)
                st.page_link("src/pages/03_materiales.py", label="Catálogo de Materiales", icon="🧱")
                st.caption("Precios unitarios de referencia para cotizar.")
            with fila2[2]:
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
if es_administrador(usuario):
    paginas["Administración"] = [
        st.Page("src/pages/06_usuarios.py", title="Usuarios", icon=":material/manage_accounts:")
    ]

pagina = st.navigation(paginas)
pagina.run()
