import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.material_service import create_supplier, list_materials, list_suppliers
from src.ui import database_error, kpi_card, page_header, records_table, section_header

can_edit = can_write(current_user())
page_header(
    "ABASTECIMIENTO",
    "Proveedores",
    "Administrá los contactos comerciales que abastecen el catálogo del taller.",
    badge="Cartera de proveedores",
)

suppliers = []
materials = []
try:
    suppliers = list_suppliers()
    materials = list_materials()
except SQLAlchemyError:
    database_error()

linked_supplier_ids = {material["id_proveedor"] for material in materials}
kpis = st.columns(2)
with kpis[0]:
    kpi_card("Proveedores registrados", len(suppliers), "Contactos comerciales en el sistema", icon="🏭", tone="blue")
with kpis[1]:
    kpi_card("Con materiales asociados", len(linked_supplier_ids), "Proveedores presentes en el catálogo", icon="📦", tone="emerald")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    with st.container(border=True):
        section_header(
            "Registrar proveedor",
            "Cargá los datos de contacto para poder asociarlo a los materiales.",
            icon="🏭",
            badge="Nueva cuenta",
        )
        with st.form("supplier_form"):
            supplier_name = st.text_input(
                "Razón social o nombre", placeholder="Ej. Aceros del Sur S.A."
            )
            rubro_col, phone_col = st.columns(2)
            with rubro_col:
                supplier_business = st.text_input(
                    "Rubro / especialidad", placeholder="Ej. Perfiles y chapas"
                )
            with phone_col:
                supplier_phone = st.text_input(
                    "Teléfono de contacto", placeholder="Ej. 11-4555-8900"
                )
            supplier_submit = st.form_submit_button(
                "Guardar proveedor", type="primary", width="stretch"
            )
        if supplier_submit:
            try:
                create_supplier(supplier_name, supplier_business, supplier_phone)
                st.success("Proveedor guardado en la base de datos.")
                st.rerun()
            except (ValueError, SQLAlchemyError) as error:
                database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
else:
    st.info("Tu perfil puede consultar proveedores, pero no registrar nuevos.")

with st.container(border=True):
    section_header(
        "Directorio de proveedores",
        "Consultá los rubros y el teléfono de cada proveedor.",
        icon="🏭",
        badge=f"{len(suppliers)} proveedores",
    )
    material_counts = {}
    for material in materials:
        supplier_id = material["id_proveedor"]
        material_counts[supplier_id] = material_counts.get(supplier_id, 0) + 1
    supplier_rows = [
        {
            "Proveedor": supplier["nombre"],
            "Rubro / especialidad": supplier["rubro"],
            "Teléfono": supplier["telefono"],
            "Materiales asociados": material_counts.get(supplier["id_proveedor"], 0),
        }
        for supplier in suppliers
    ]
    records_table(
        supplier_rows,
        "suppliers",
        "Todavía no hay proveedores",
        "Registrá el primer proveedor desde el formulario de arriba.",
    )
