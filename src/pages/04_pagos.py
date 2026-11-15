import streamlit as st
from datetime import date

st.title("💳 Pagos")
st.write("Registra pagos y asócialos a un presupuesto.")

if "pagos" not in st.session_state:
    st.session_state.pagos = []

presupuestos = st.session_state.get("presupuestos", [])

with st.container(border=True):
    st.subheader("Registrar pago")
    with st.form("formulario_pago"):
        if presupuestos:
            opciones = ["Presupuesto " + str(p["Número"]) + " - " + p["Cliente"] for p in presupuestos]
            presupuesto_elegido = st.selectbox("Presupuesto", opciones)
            indice = opciones.index(presupuesto_elegido)
            numero_presupuesto = presupuestos[indice]["Número"]
        else:
            st.write("Todavía no hay presupuestos. Puedes escribir el número para completar el formulario.")
            numero_presupuesto = st.number_input("Número de presupuesto", min_value=1, step=1)

        fecha_pago = st.date_input("Fecha del pago", value=date.today())
        monto = st.number_input("Monto", min_value=0.0, value=0.0, step=1000.0)
        metodo = st.selectbox("Método de pago", ["Efectivo", "Transferencia", "Tarjeta", "Otro"])
        referencia = st.text_input("Referencia o número de comprobante (opcional)")
        guardar = st.form_submit_button("Guardar pago", type="primary")

if guardar:
    if monto <= 0:
        st.error("El monto debe ser mayor que cero.")
    else:
        pago = {
            "Número": len(st.session_state.pagos) + 1,
            "Presupuesto": numero_presupuesto,
            "Fecha": str(fecha_pago),
            "Monto": monto,
            "Método": metodo,
            "Referencia": referencia,
        }
        st.session_state.pagos.append(pago)
        st.success("Pago guardado.")

st.subheader("Pagos registrados")
if st.session_state.pagos:
    st.table(st.session_state.pagos)
else:
    st.info("Todavía no hay pagos cargados.")

st.caption("Los datos son temporales y se borran al cerrar la aplicación.")
