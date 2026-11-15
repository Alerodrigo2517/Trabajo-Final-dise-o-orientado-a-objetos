import streamlit as st

st.title("👥 Clientes")
st.write("Completa los datos para agregar un cliente.")

if "clientes" not in st.session_state:
    st.session_state.clientes = []

with st.container(border=True):
    st.subheader("Nuevo cliente")
    with st.form("formulario_cliente"):
        columna1, columna2 = st.columns(2)
        with columna1:
            cuit = st.text_input("CUIT", placeholder="20-12345678-9")
            nombre = st.text_input("Nombre")
        with columna2:
            apellido = st.text_input("Apellido")
        guardar = st.form_submit_button("Guardar cliente", type="primary")

if guardar:
    if cuit == "" or nombre == "" or apellido == "":
        st.error("Completa todos los campos.")
    else:
        existe = False
        for cliente in st.session_state.clientes:
            if cliente["CUIT"] == cuit:
                existe = True

        if existe:
            st.error("Ya existe un cliente con ese CUIT.")
        else:
            cliente = {"CUIT": cuit, "Nombre": nombre, "Apellido": apellido}
            st.session_state.clientes.append(cliente)
            st.success("Cliente guardado.")

st.subheader("Clientes registrados")

if len(st.session_state.clientes) == 0:
    st.info("Todavía no hay clientes cargados.")
else:
    st.table(st.session_state.clientes)

st.caption("Los datos se borran al cerrar la aplicación. Todavía no están guardados en la base de datos.")
