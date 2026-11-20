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


def render_budget_form(*, prefijo_clave: str = "presupuesto", compacto: bool = False) -> None:
    if not can_write(current_user()):
        st.info("Tu perfil puede consultar presupuestos, pero no crear ni modificar datos.")
        return
    try:
        clientes = list_clients()
        materiales = materials_for_budget()
    except SQLAlchemyError as error:
        handle_database_error(error)
        return

    section_header(
        "Confección de Presupuesto",
        "Seleccioná el cliente, definí la ubicación de obra y cargá los materiales a cotizar.",
        icono="📐",
        insignia="Cotizador",
    )

    if not clientes:
        st.info("Primero registrá un cliente para poder asociarlo al presupuesto.")
        st.page_link("src/pages/01_clientes.py", label="Ir a Clientes", icon="👥")
        return

    opciones_clientes = {
        f"{cliente['cuit_display']} · {cliente['nombre_completo']}": cliente for cliente in clientes
    }
    col_selector1, col_selector2 = st.columns([1.15, 1])
    with col_selector1:
        etiqueta_seleccionada = st.selectbox(
            "1. Seleccionar cliente",
            list(opciones_clientes),
            index=None,
            placeholder="Elegí un cliente por CUIT o nombre…",
            key=f"{prefijo_clave}_client",
        )
    if etiqueta_seleccionada is None:
        st.caption("👆 Seleccioná un cliente del padrón para desplegar el formulario completo de cotización.")
        return

    cliente = opciones_clientes[etiqueta_seleccionada]
    clave_fila = f"{prefijo_clave}_{cliente['cuit_cliente']}"

    try:
        contactos = list_client_contacts(cliente["cuit_cliente"])
    except (ValueError, SQLAlchemyError) as error:
        handle_database_error(error)
        return

    etiquetas_contacto = {"➕ Registrar nuevo contacto": None}
    for contacto in contactos:
        etiqueta = f"📍 {contacto['direccion']} · {contacto['ciudad']} · 📞 {contacto['telefono']} (#{contacto['id_contacto']})"
        etiquetas_contacto[etiqueta] = contacto

    with col_selector2:
        etiqueta_contacto = st.selectbox(
            "2. Contacto del cliente",
            list(etiquetas_contacto),
            key=f"{prefijo_clave}_contact_{cliente['cuit_cliente']}",
        )
    contacto_seleccionado = etiquetas_contacto[etiqueta_contacto]

    opt_col1, opt_col2 = st.columns([1.2, 1])
    with opt_col1:
        etiqueta_calculo = st.radio(
            "Modalidad de mano de obra",
            ("Porcentaje sobre materiales", "Por hora"),
            horizontal=True,
            key=f"{clave_fila}_calculation",
        )
    tipo_calculo = "PORCENTAJE" if etiqueta_calculo == "Porcentaje sobre materiales" else "POR_HORA"

    with opt_col2:
        tiene_vencimiento = st.checkbox("Incluir fecha de validez", key=f"{clave_fila}_has_expiration")
        fecha_vencimiento = (
            st.date_input("Válido hasta", value=date.today(), key=f"{clave_fila}_expiration")
            if tiene_vencimiento
            else None
        )

    etiquetas_materiales = {
        f"#{material['id_material']} · {material['descripcion']} · {currency(material['precio_unitario'])}": material
        for material in materiales
    }

    with st.form(f"{prefijo_clave}_form"):
        st.markdown('<p class="panel-heading">DATOS DEL CLIENTE Y CONTACTO</p>', unsafe_allow_html=True)
        col_nombre, cuit_col = st.columns(2)
        with col_nombre:
            st.text_input("Cliente", value=cliente["nombre_completo"], disabled=True, key=f"{clave_fila}_client_name")
        with cuit_col:
            st.text_input("CUIT / CUIL", value=cliente["cuit_display"], disabled=True, key=f"{clave_fila}_client_cuit")

        if contacto_seleccionado is None:
            st.caption("Completá el domicilio, localidad y teléfono de contacto del cliente.")
            col_contacto1, col_contacto2, col_contacto3 = st.columns([1.2, 1, 1])
            with col_contacto1:
                direccion_contacto = st.text_input("Dirección del cliente", placeholder="Calle y número", key=f"{clave_fila}_contact_address")
            with col_contacto2:
                ciudad_contacto = st.text_input("Ciudad del cliente", placeholder="Localidad", key=f"{clave_fila}_contact_city")
            with col_contacto3:
                telefono_contacto = st.text_input("Teléfono del cliente", placeholder="Código de área + número", key=f"{clave_fila}_contact_phone")
        else:
            direccion_contacto = contacto_seleccionado["direccion"]
            ciudad_contacto = contacto_seleccionado["ciudad"]
            telefono_contacto = contacto_seleccionado["telefono"]
            st.caption(f"📍 Contacto seleccionado: **{direccion_contacto}, {ciudad_contacto}** · 📞 **{telefono_contacto}**")

        st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">UBICACIÓN Y ESPECIFICACIÓN DE OBRA</p>', unsafe_allow_html=True)
        col_trabajo1, col_trabajo2 = st.columns(2)
        with col_trabajo1:
            direccion_trabajo = st.text_input("Dirección de la obra / instalación", placeholder="Domicilio donde se realizará el trabajo", key=f"{clave_fila}_work_address")
        with col_trabajo2:
            ciudad_trabajo = st.text_input("Ciudad de la obra", placeholder="Localidad de la obra", key=f"{clave_fila}_work_city")

        meta_col1, meta_col2 = st.columns(2)
        with meta_col1:
            fecha_presupuesto = st.date_input("Fecha de emisión", value=date.today(), key=f"{clave_fila}_budget_date")
        with meta_col2:
            tipo_trabajo = st.text_input("Tipo de trabajo", placeholder="Ej. Portón corredizo, Reja de frente, Estructura…", key=f"{clave_fila}_work_type")

        descripcion = st.text_area(
            "Descripción técnica y especificaciones",
            max_chars=500,
            height=85,
            placeholder="Medidas, espesores, terminación, pintura y detalles constructivos…",
            key=f"{clave_fila}_description",
        )

        st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">DESGLOSE DE MATERIALES Y MANO DE OBRA</p>', unsafe_allow_html=True)
        if etiquetas_materiales:
            elementos_iniciales = pd.DataFrame([{"Material": None, "Cantidad": 1.0}])
            filas_elementos = st.data_editor(
                elementos_iniciales,
                key=f"{clave_fila}_materials",
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                column_config={
                    "Material": st.column_config.SelectboxColumn("Material del catálogo", options=list(etiquetas_materiales), width="large"),
                    "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=0.01, step=0.5, format="%.2f", width="small"),
                },
            )
        else:
            filas_elementos = pd.DataFrame(columns=["Material", "Cantidad"])
            st.info("No hay materiales cargados en el catálogo. Podés guardar el presupuesto y registrar materiales luego.")

        if tipo_calculo == "PORCENTAJE":
            st.caption("El porcentaje se aplica sobre el subtotal de los materiales incluidos arriba.")
            porcentaje = st.number_input(
                "Porcentaje de mano de obra (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=5.0,
                key=f"{clave_fila}_percentage",
            )
            tarifa_hora = None
            horas = None
        else:
            porcentaje = None
            labor_col1, labor_col2 = st.columns(2)
            with labor_col1:
                tarifa_hora = st.number_input(
                    "Valor por hora de taller (ARS $)",
                    min_value=0.0,
                    value=0.0,
                    step=500.0,
                    key=f"{clave_fila}_hourly_rate",
                )
            with labor_col2:
                horas = st.number_input(
                    "Horas estimadas de trabajo",
                    min_value=0.0,
                    value=1.0,
                    step=0.5,
                    key=f"{clave_fila}_hours",
                )

        enviado = st.form_submit_button("💾 Guardar presupuesto", type="primary", width="stretch")

    if not enviado:
        return

    elementos_seleccionados = []
    for _, elemento in filas_elementos.iterrows():
        etiqueta = elemento.get("Material")
        if etiqueta in (None, "") or pd.isna(etiqueta):
            continue
        material_seleccionado = etiquetas_materiales.get(str(etiqueta))
        if material_seleccionado is None:
            st.error("Uno de los materiales seleccionados ya no está disponible. Actualizá la pantalla.")
            return
        elementos_seleccionados.append(
            {"material_id": material_seleccionado["id_material"], "cantidad": elemento.get("Cantidad", 0)}
        )

    try:
        id_presupuesto = create_budget(
            cuit_cliente=cliente["cuit_cliente"],
            id_contacto_cliente=contacto_seleccionado["id_contacto"] if contacto_seleccionado else None,
            direccion_contacto=direccion_contacto,
            ciudad_contacto=ciudad_contacto,
            telefono_contacto=telefono_contacto,
            direccion_trabajo=direccion_trabajo,
            ciudad_trabajo=ciudad_trabajo,
            tipo_trabajo=tipo_trabajo,
            descripcion=descripcion,
            fecha_presupuesto=fecha_presupuesto,
            fecha_vencimiento=fecha_vencimiento,
            tipo_calculo=tipo_calculo,
            porcentaje=porcentaje,
            tarifa_hora=tarifa_hora,
            horas=horas,
            materiales=elementos_seleccionados,
        )
        presupuesto_guardado = next(fila for fila in list_budgets() if fila["id_presupuesto"] == id_presupuesto)
        st.success(f"✅ Presupuesto #{id_presupuesto} registrado exitosamente.")
        st.metric("Total estimado · materiales + mano de obra", currency(presupuesto_guardado["total_estimado"]))
    except (ValueError, SQLAlchemyError) as error:
        handle_database_error(error)
