import streamlit as st
from datetime import date

st.title("📄 Presupuestos")
st.write("Completa los datos del cliente y del trabajo para registrar un presupuesto.")

if "presupuestos" not in st.session_state:
    st.session_state.presupuestos = []

clientes = st.session_state.get("clientes", [])

with st.container(border=True):
    st.subheader("Nuevo presupuesto")
    tipo_calculo = st.radio("Forma de calcular la mano de obra", ["Por porcentaje", "Por hora"], horizontal=True)
    tiene_vencimiento = st.checkbox("Agregar fecha de vencimiento")
    if tiene_vencimiento:
        fecha_vencimiento = st.date_input("Válido hasta", value=date.today())
    else:
        fecha_vencimiento = None

    with st.form("formulario_presupuesto"):
        if clientes:
            opciones_clientes = [cliente["Nombre"] + " " + cliente["Apellido"] for cliente in clientes]
            cliente_elegido = st.selectbox("Cliente", opciones_clientes)
            indice_cliente = opciones_clientes.index(cliente_elegido)
            cuit_cliente = clientes[indice_cliente]["CUIT"]
        else:
            st.write("Todavía no hay clientes registrados. Puedes escribir el nombre para este presupuesto.")
            cliente_elegido = st.text_input("Nombre del cliente")
            cuit_cliente = st.text_input("CUIT del cliente")

        col1, col2 = st.columns(2)
        with col1:
            direccion = st.text_input("Dirección del trabajo")
            ciudad = st.text_input("Ciudad")
            tipo_trabajo = st.text_input("Tipo de trabajo", placeholder="Reja, portón, reparación...")
        with col2:
            fecha_presupuesto = st.date_input("Fecha del presupuesto", value=date.today())

        descripcion = st.text_area("Descripción del trabajo")

        if tipo_calculo == "Por porcentaje":
            costo_porcentaje = st.number_input("Porcentaje", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
            costo_hora = None
            duracion_horas = None
        else:
            costo_porcentaje = None
            costo_hora = st.number_input("Costo por hora", min_value=0.0, value=0.0, step=100.0)
            duracion_horas = st.number_input("Horas estimadas", min_value=0.0, value=1.0, step=1.0)

        guardar = st.form_submit_button("Guardar presupuesto", type="primary")

if guardar:
    if cliente_elegido.strip() == "" or direccion.strip() == "" or ciudad.strip() == "" or tipo_trabajo.strip() == "":
        st.error("Completa el cliente, la dirección, la ciudad y el tipo de trabajo.")
    elif fecha_vencimiento is not None and fecha_vencimiento < fecha_presupuesto:
        st.error("La fecha de vencimiento no puede ser anterior a la fecha del presupuesto.")
    else:
        presupuesto = {
            "Número": len(st.session_state.presupuestos) + 1,
            "Cliente": cliente_elegido,
            "CUIT": cuit_cliente,
            "Dirección": direccion,
            "Ciudad": ciudad,
            "Trabajo": tipo_trabajo,
            "Fecha": str(fecha_presupuesto),
            "Vencimiento": str(fecha_vencimiento) if fecha_vencimiento else "Sin vencimiento",
            "Descripción": descripcion,
            "Cálculo": tipo_calculo,
            "Porcentaje": costo_porcentaje,
            "Costo por hora": costo_hora,
            "Horas": duracion_horas,
            "Estado": "BORRADOR",
        }
        st.session_state.presupuestos.append(presupuesto)
        st.success("Presupuesto guardado.")

st.subheader("Presupuestos registrados")
if st.session_state.presupuestos:
    st.table(st.session_state.presupuestos)
else:
    st.info("Todavía no hay presupuestos cargados.")

st.caption("Los datos son temporales y se borran al cerrar la aplicación.")
