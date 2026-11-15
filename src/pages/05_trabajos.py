import streamlit as st
from datetime import date

st.title("🛠️ Trabajos")
st.write("Registra y actualiza el estado de los trabajos aprobados.")

if "trabajos" not in st.session_state:
    st.session_state.trabajos = []

presupuestos = st.session_state.get("presupuestos", [])

with st.container(border=True):
    st.subheader("Registrar trabajo")
    finalizado = st.checkbox("Ingresar fecha de finalización")
    if finalizado:
        fecha_fin = st.date_input("Fecha de finalización", value=date.today())
    else:
        fecha_fin = None

    with st.form("formulario_trabajo"):
        if presupuestos:
            opciones = ["Presupuesto " + str(p["Número"]) + " - " + p["Cliente"] for p in presupuestos]
            presupuesto_elegido = st.selectbox("Presupuesto", opciones)
            indice = opciones.index(presupuesto_elegido)
            numero_presupuesto = presupuestos[indice]["Número"]
        else:
            st.write("Todavía no hay presupuestos. Puedes escribir el número para completar el formulario.")
            numero_presupuesto = st.number_input("Número de presupuesto", min_value=1, step=1)

        fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
        estado = st.selectbox("Estado", ["PENDIENTE", "EN_PROCESO", "FINALIZADO", "CANCELADO"])
        observaciones = st.text_area("Observaciones")
        guardar = st.form_submit_button("Guardar trabajo", type="primary")

if guardar:
    existe = False
    for trabajo in st.session_state.trabajos:
        if trabajo["Presupuesto"] == numero_presupuesto:
            existe = True

    if existe:
        st.error("Ese presupuesto ya tiene un trabajo registrado.")
    elif fecha_fin is not None and fecha_fin < fecha_inicio:
        st.error("La fecha de finalización no puede ser anterior al inicio.")
    else:
        trabajo = {
            "Número": len(st.session_state.trabajos) + 1,
            "Presupuesto": numero_presupuesto,
            "Inicio": str(fecha_inicio),
            "Fin": str(fecha_fin) if fecha_fin else "Sin finalizar",
            "Estado": estado,
            "Observaciones": observaciones,
        }
        st.session_state.trabajos.append(trabajo)
        st.success("Trabajo guardado.")

st.subheader("Trabajos registrados")
if st.session_state.trabajos:
    st.table(st.session_state.trabajos)
else:
    st.info("Todavía no hay trabajos cargados.")

st.caption("Los datos son temporales y se borran al cerrar la aplicación.")
