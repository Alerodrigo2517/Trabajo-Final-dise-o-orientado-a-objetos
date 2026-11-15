import streamlit as st

st.set_page_config(page_title="Sistema de Herrería", page_icon="🔨", layout="wide")
st.sidebar.title("🔨 Herrería")
st.sidebar.caption("Gestión del taller")


def inicio():
    st.title("Sistema de Herrería")
    st.write("Un espacio para organizar la información del taller.")

    st.subheader("Secciones del sistema")
    columna1, columna2, columna3 = st.columns(3)

    with columna1:
        with st.container(border=True):
            st.subheader("👥 Clientes")
            st.write("Datos de las personas y empresas que solicitan trabajos.")

    with columna2:
        with st.container(border=True):
            st.subheader("📄 Presupuestos")
            st.write("Cálculo y seguimiento de los trabajos solicitados.")

    with columna3:
        with st.container(border=True):
            st.subheader("🧰 Materiales")
            st.write("Materiales disponibles, precios y proveedores.")

    columna4, columna5 = st.columns(2)

    with columna4:
        with st.container(border=True):
            st.subheader("💳 Pagos")
            st.write("Registro de pagos asociados a los presupuestos.")

    with columna5:
        with st.container(border=True):
            st.subheader("🛠️ Trabajos")
            st.write("Seguimiento del estado de cada trabajo.")

    st.info("Los formularios guardan los datos solo durante esta sesión.")


paginas = [
    st.Page(inicio, title="Inicio", icon="🏠"),
    st.Page("src/pages/01_clientes.py", title="Clientes", icon="👥"),
    st.Page("src/pages/02_presupuestos.py", title="Presupuestos", icon="📄"),
    st.Page("src/pages/03_materiales.py", title="Materiales y proveedores", icon="🧰"),
    st.Page("src/pages/04_pagos.py", title="Pagos", icon="💳"),
    st.Page("src/pages/05_trabajos.py", title="Trabajos", icon="🛠️"),
]

pagina = st.navigation(paginas)
pagina.run()

