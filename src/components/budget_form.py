"""Formulario de presupuesto adaptado a las relaciones del esquema actual."""

from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.budget_service import create_budget, list_budgets, materials_for_budget
from src.services.client_service import list_client_contacts, list_clients
from src.ui import currency, handle_database_error, section_header


def render_budget_form(*, key_prefix: str = "presupuesto", compact: bool = False) -> None:
    if not can_write(current_user()):
        st.info("Tu perfil puede consultar presupuestos, pero no crear ni modificar datos.")
        return
    try:
        clients = list_clients()
        materials = materials_for_budget()
    except SQLAlchemyError as error:
        handle_database_error(error)
        return

    section_header(
        "Confección de Presupuesto",
        "Seleccioná el cliente, definí la ubicación de obra y cargá los materiales a cotizar.",
        icon="📐",
        badge="Cotizador",
    )

    if not clients:
        st.info("Primero registrá un cliente para poder asociarlo al presupuesto.")
        st.page_link("src/pages/01_clientes.py", label="Ir a Clientes", icon="👥")
        return

    client_options = {
        f"{client['cuit_display']} · {client['nombre_completo']}": client for client in clients
    }
    sel_col1, sel_col2 = st.columns([1.15, 1])
    with sel_col1:
        selected_label = st.selectbox(
            "1. Seleccionar cliente",
            list(client_options),
            index=None,
            placeholder="Elegí un cliente por CUIT o nombre…",
            key=f"{key_prefix}_client",
        )
    if selected_label is None:
        st.caption("👆 Seleccioná un cliente del padrón para desplegar el formulario completo de cotización.")
        return

    client = client_options[selected_label]
    entry_key = f"{key_prefix}_{client['cuit_cliente']}"

    try:
        contacts = list_client_contacts(client["cuit_cliente"])
    except (ValueError, SQLAlchemyError) as error:
        handle_database_error(error)
        return

    contact_labels = {"➕ Registrar nuevo contacto": None}
    for contact in contacts:
        label = f"📍 {contact['direccion']} · {contact['ciudad']} · 📞 {contact['telefono']} (#{contact['id_contacto']})"
        contact_labels[label] = contact

    with sel_col2:
        contact_label = st.selectbox(
            "2. Contacto del cliente",
            list(contact_labels),
            key=f"{key_prefix}_contact_{client['cuit_cliente']}",
        )
    selected_contact = contact_labels[contact_label]

    opt_col1, opt_col2 = st.columns([1.2, 1])
    with opt_col1:
        calc_label = st.radio(
            "Modalidad de mano de obra",
            ("Porcentaje sobre materiales", "Por hora"),
            horizontal=True,
            key=f"{entry_key}_calculation",
        )
    calculation_type = "PORCENTAJE" if calc_label == "Porcentaje sobre materiales" else "POR_HORA"

    with opt_col2:
        has_expiration = st.checkbox("Incluir fecha de validez", key=f"{entry_key}_has_expiration")
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
        st.markdown('<p class="panel-heading">DATOS DEL CLIENTE Y CONTACTO</p>', unsafe_allow_html=True)
        name_col, cuit_col = st.columns(2)
        with name_col:
            st.text_input("Cliente", value=client["nombre_completo"], disabled=True, key=f"{entry_key}_client_name")
        with cuit_col:
            st.text_input("CUIT / CUIL", value=client["cuit_display"], disabled=True, key=f"{entry_key}_client_cuit")

        if selected_contact is None:
            st.caption("Completá el domicilio, localidad y teléfono de contacto del cliente.")
            contact_col1, contact_col2, contact_col3 = st.columns([1.2, 1, 1])
            with contact_col1:
                contact_address = st.text_input("Dirección del cliente", placeholder="Calle y número", key=f"{entry_key}_contact_address")
            with contact_col2:
                contact_city = st.text_input("Ciudad del cliente", placeholder="Localidad", key=f"{entry_key}_contact_city")
            with contact_col3:
                contact_phone = st.text_input("Teléfono del cliente", placeholder="Código de área + número", key=f"{entry_key}_contact_phone")
        else:
            contact_address = selected_contact["direccion"]
            contact_city = selected_contact["ciudad"]
            contact_phone = selected_contact["telefono"]
            st.caption(f"📍 Contacto seleccionado: **{contact_address}, {contact_city}** · 📞 **{contact_phone}**")

        st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">UBICACIÓN Y ESPECIFICACIÓN DE OBRA</p>', unsafe_allow_html=True)
        work_col1, work_col2 = st.columns(2)
        with work_col1:
            work_address = st.text_input("Dirección de la obra / instalación", placeholder="Domicilio donde se realizará el trabajo", key=f"{entry_key}_work_address")
        with work_col2:
            work_city = st.text_input("Ciudad de la obra", placeholder="Localidad de la obra", key=f"{entry_key}_work_city")

        meta_col1, meta_col2 = st.columns(2)
        with meta_col1:
            budget_date = st.date_input("Fecha de emisión", value=date.today(), key=f"{entry_key}_budget_date")
        with meta_col2:
            work_type = st.text_input("Tipo de trabajo", placeholder="Ej. Portón corredizo, Reja de frente, Estructura…", key=f"{entry_key}_work_type")

        description = st.text_area(
            "Descripción técnica y especificaciones",
            max_chars=500,
            height=85,
            placeholder="Medidas, espesores, terminación, pintura y detalles constructivos…",
            key=f"{entry_key}_description",
        )

        st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">DESGLOSE DE MATERIALES Y MANO DE OBRA</p>', unsafe_allow_html=True)
        if material_labels:
            initial_items = pd.DataFrame([{"Material": None, "Cantidad": 1.0}])
            item_rows = st.data_editor(
                initial_items,
                key=f"{entry_key}_materials",
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                column_config={
                    "Material": st.column_config.SelectboxColumn("Material del catálogo", options=list(material_labels), width="large"),
                    "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=0.01, step=0.5, format="%.2f", width="small"),
                },
            )
        else:
            item_rows = pd.DataFrame(columns=["Material", "Cantidad"])
            st.info("No hay materiales cargados en el catálogo. Podés guardar el presupuesto y registrar materiales luego.")

        if calculation_type == "PORCENTAJE":
            st.caption("El porcentaje se aplica sobre el subtotal de los materiales incluidos arriba.")
            percentage = st.number_input(
                "Porcentaje de mano de obra (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=5.0,
                key=f"{entry_key}_percentage",
            )
            hourly_rate = None
            hours = None
        else:
            percentage = None
            labor_col1, labor_col2 = st.columns(2)
            with labor_col1:
                hourly_rate = st.number_input(
                    "Valor por hora de taller (ARS $)",
                    min_value=0.0,
                    value=0.0,
                    step=500.0,
                    key=f"{entry_key}_hourly_rate",
                )
            with labor_col2:
                hours = st.number_input(
                    "Horas estimadas de trabajo",
                    min_value=0.0,
                    value=1.0,
                    step=0.5,
                    key=f"{entry_key}_hours",
                )

        submitted = st.form_submit_button("💾 Guardar presupuesto", type="primary", width="stretch")

    if not submitted:
        return

    selected_items = []
    for _, item in item_rows.iterrows():
        label = item.get("Material")
        if label in (None, "") or pd.isna(label):
            continue
        selected_material = material_labels.get(str(label))
        if selected_material is None:
            st.error("Uno de los materiales seleccionados ya no está disponible. Actualizá la pantalla.")
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
        st.success(f"✅ Presupuesto #{budget_id} registrado exitosamente.")
        st.metric("Total estimado · materiales + mano de obra", currency(saved_budget["total_estimado"]))
    except (ValueError, SQLAlchemyError) as error:
        handle_database_error(error)
