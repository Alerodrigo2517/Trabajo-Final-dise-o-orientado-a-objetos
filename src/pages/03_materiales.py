import streamlit as st

st.title("🧰 Materiales y proveedores")
st.write("Primero registra un proveedor y luego podrás asociarle materiales.")

if "proveedores" not in st.session_state:
    st.session_state.proveedores = []
if "materiales" not in st.session_state:
    st.session_state.materiales = []

with st.container(border=True):
    st.subheader("Registrar proveedor")
    with st.form("formulario_proveedor"):
        nombre_proveedor = st.text_input("Nombre del proveedor")
        rubro = st.text_input("Rubro")
        telefono_proveedor = st.text_input("Teléfono")
        guardar_proveedor = st.form_submit_button("Guardar proveedor")

if guardar_proveedor:
    if nombre_proveedor.strip() == "" or rubro.strip() == "" or telefono_proveedor.strip() == "":
        st.error("Completa todos los datos del proveedor.")
    else:
        proveedor = {
            "Número": len(st.session_state.proveedores) + 1,
            "Nombre": nombre_proveedor,
            "Rubro": rubro,
            "Teléfono": telefono_proveedor,
        }
        st.session_state.proveedores.append(proveedor)
        st.success("Proveedor guardado.")

st.subheader("Registrar material")
if st.session_state.proveedores:
    nombres_proveedores = [proveedor["Nombre"] for proveedor in st.session_state.proveedores]
    with st.form("formulario_material"):
        descripcion = st.text_input("Descripción del material")
        precio = st.number_input("Precio unitario", min_value=0.0, value=0.0, step=100.0)
        proveedor_elegido = st.selectbox("Proveedor", nombres_proveedores)
        guardar_material = st.form_submit_button("Guardar material", type="primary")

    if guardar_material:
        if descripcion.strip() == "":
            st.error("Escribe la descripción del material.")
        else:
            material = {
                "Número": len(st.session_state.materiales) + 1,
                "Descripción": descripcion,
                "Precio unitario": precio,
                "Proveedor": proveedor_elegido,
            }
            st.session_state.materiales.append(material)
            st.success("Material guardado.")
else:
    st.info("Registra un proveedor antes de agregar materiales.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Proveedores")
    if st.session_state.proveedores:
        st.table(st.session_state.proveedores)
    else:
        st.write("Todavía no hay proveedores.")
with col2:
    st.subheader("Materiales")
    if st.session_state.materiales:
        st.table(st.session_state.materiales)
    else:
        st.write("Todavía no hay materiales.")

st.caption("Los datos son temporales y se borran al cerrar la aplicación.")
