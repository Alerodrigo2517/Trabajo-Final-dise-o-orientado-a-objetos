"""Formulario de presupuesto adaptado a las relaciones del esquema actual."""

from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.services.budget_service import create_budget, list_budgets, materials_for_budget
from src.services.client_service import list_client_contacts, list_clients
from src.ui import currency, handle_database_error


def render_budget_form(*, key_prefix: str = "presupuesto", compact: bool = False) -> None:
    try:
        clients = list_clients()
        materials = materials_for_budget()
    except SQLAlchemyError as error:
        handle_database_error(error)
        return

    st.markdown('<p class="panel-heading">PRESUPUESTO</p>', unsafe_allow_html=True)
    if not clients:
        st.info("Primero registrá un cliente para poder asociarlo al presupuesto.")
        st.page_link("src/pages/01_clientes.py", label="Ir a Clientes", icon="👥")
        return

    client_options = {
        f"{client['cuit_display']} · {client['nombre_completo']}": client for client in clients
    }
    selected_label = st.selectbox(
        "Buscar cliente",
        list(client_options),
        index=None,
        placeholder="Elegí un cliente…",
        key=f"{key_prefix}_client",
    )
    if selected_label is None:
        st.caption("Al seleccionar el cliente se completan su nombre y CUIT.")
        return
    client = client_options[selected_label]
    entry_key = f"{key_prefix}_{client['cuit_cliente']}"

    try:
        contacts = list_client_contacts(client["cuit_cliente"])
    except (ValueError, SQLAlchemyError) as error:
        handle_database_error(error)
        return

    contact_labels = {"Nuevo contacto": None}
    for contact in contacts:
        label = f"{contact['direccion']} · {contact['ciudad']} · {contact['telefono']} · #{contact['id_contacto']}"
        contact_labels[label] = contact
    contact_label = st.selectbox(
        "Contacto del cliente",
        list(contact_labels),
        key=f"{key_prefix}_contact_{client['cuit_cliente']}",
    )
    selected_contact = contact_labels[contact_label]

    calc_label = st.radio(
        "Mano de obra",
        ("Porcentaje sobre materiales", "Por hora"),
        horizontal=True,
        key=f"{entry_key}_calculation",
    )
    calculation_type = "PORCENTAJE" if calc_label == "Porcentaje sobre materiales" else "POR_HORA"
    has_expiration = st.checkbox("Agregar fecha de vencimiento", key=f"{entry_key}_has_expiration")
    expiration_date = (
        st.date_input("Válido hasta", value=date.today(), key=f"{entry_key}_expiration")
        if has_expiration
        else None
    )

    material_labels = {
        f"#{material['id_material']} · {material['descripcion']} · {currency(material['precio_unitario'])}": material
        for material in materials
    }
    with st.form(f"{key_prefix}_form"):
        name_col, cuit_col = st.columns(2)
        with name_col:
            st.text_input("Nombre", value=client["nombre_completo"], disabled=True, key=f"{entry_key}_client_name")
        with cuit_col:
            st.text_input("CUIT", value=client["cuit_display"], disabled=True, key=f"{entry_key}_client_cuit")

        if selected_contact is None:
            st.caption("Contacto nuevo: estos datos se guardan en clientes_contacto, como requiere el esquema.")
            contact_col1, contact_col2 = st.columns(2)
            with contact_col1:
                contact_address = st.text_input("Dirección del cliente", key=f"{entry_key}_contact_address")
                contact_phone = st.text_input("Teléfono del cliente", key=f"{entry_key}_contact_phone")
            with contact_col2:
                contact_city = st.text_input("Ciudad del cliente", key=f"{entry_key}_contact_city")
        else:
            contact_address = selected_contact["direccion"]
            contact_city = selected_contact["ciudad"]
            contact_phone = selected_contact["telefono"]
            st.caption(f"Contacto vigente: {contact_address}, {contact_city} · {contact_phone}")

        work_col1, work_col2 = st.columns(2)
        with work_col1:
            work_address = st.text_input("Dirección del trabajo", key=f"{entry_key}_work_address")
        with work_col2:
            work_city = st.text_input("Ciudad del trabajo", key=f"{entry_key}_work_city")

        work_col1, work_col2 = st.columns(2)
        with work_col1:
            budget_date = st.date_input("Fecha del presupuesto", value=date.today(), key=f"{entry_key}_budget_date")
        with work_col2:
            work_type = st.text_input("Tipo de trabajo", placeholder="Reja, portón, reparación…", key=f"{entry_key}_work_type")

        description = st.text_area("Descripción y especificaciones", max_chars=500, height=90, key=f"{entry_key}_description")

        st.markdown("**Materiales del presupuesto**")
        if material_labels:
            initial_items = pd.DataFrame([{"Material": None, "Cantidad": 1.0}])
            item_rows = st.data_editor(
                initial_items,
                key=f"{entry_key}_materials",
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                column_config={
                    "Material": st.column_config.SelectboxColumn("Material", options=list(material_labels)),
                    "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=0.01, step=0.5, format="%.2f"),
                },
            )
        else:
            item_rows = pd.DataFrame(columns=["Material", "Cantidad"])
            st.info("No hay materiales registrados. Podés guardar el presupuesto y cargarlos después en Materiales.")

        if calculation_type == "PORCENTAJE":
            st.caption("El porcentaje se calcula sobre el subtotal de los materiales seleccionados.")
            percentage = st.number_input("Mano de obra (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key=f"{entry_key}_percentage")
            hourly_rate = None
            hours = None
        else:
            percentage = None
            labor_col1, labor_col2 = st.columns(2)
            with labor_col1:
                hourly_rate = st.number_input("Costo por hora (ARS $)", min_value=0.0, value=0.0, step=100.0, key=f"{entry_key}_hourly_rate")
            with labor_col2:
                hours = st.number_input("Horas estimadas", min_value=0.0, value=1.0, step=0.5, key=f"{entry_key}_hours")

        submitted = st.form_submit_button("Guardar presupuesto", type="primary", width="stretch")

    if not submitted:
        return

    selected_items = []
    for _, item in item_rows.iterrows():
        label = item.get("Material")
        if label in (None, "") or pd.isna(label):
            continue
        selected_material = material_labels.get(str(label))
        if selected_material is None:
            st.error("Uno de los materiales ya no está disponible. Actualizá la pantalla.")
            return
        selected_items.append(
            {"material_id": selected_material["id_material"], "cantidad": item.get("Cantidad", 0)}
        )

    try:
        budget_id = create_budget(
            client_cuit=client["cuit_cliente"],
            client_contact_id=selected_contact["id_contacto"] if selected_contact else None,
            contact_address=contact_address,
            contact_city=contact_city,
            contact_phone=contact_phone,
            work_address=work_address,
            work_city=work_city,
            work_type=work_type,
            description=description,
            budget_date=budget_date,
            expiration_date=expiration_date,
            calculation_type=calculation_type,
            percentage=percentage,
            hourly_rate=hourly_rate,
            hours=hours,
            materials=selected_items,
        )
        saved_budget = next(row for row in list_budgets() if row["id_presupuesto"] == budget_id)
        st.success(f"Presupuesto #{budget_id} guardado en la base de datos.")
        st.metric("Total estimado · materiales + mano de obra", currency(saved_budget["total_estimado"]))
        st.caption("El total se calcula desde los detalles almacenados; el esquema actual no tiene una columna de total ni de margen.")
    except (ValueError, SQLAlchemyError) as error:
        handle_database_error(error)
