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
    "Administrá las empresas y comercios que abastecen el catálogo de materiales del taller.",
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
rubros_count = len({(s.get("rubro") or "").strip().lower() for s in suppliers if (s.get("rubro") or "").strip()})

kpis = st.columns(4)
with kpis[0]:
    kpi_card("Proveedores totales", len(suppliers), "Registrados en el sistema", icon="🏭", tone="amber")
with kpis[1]:
    kpi_card("Con insumos activos", len(linked_supplier_ids), "Presentes en el catálogo", icon="✅", tone="emerald")
with kpis[2]:
    kpi_card("Rubros cubiertos", rubros_count, "Especialidades registradas", icon="📦", tone="blue")
with kpis[3]:
    kpi_card("Insumos provistos", len(materials), "Total de materiales asociados", icon="🧱", tone="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    tab_list, tab_new = st.tabs(["📋 Directorio de proveedores", "➕ Registrar nuevo proveedor"])
else:
    st.info("👁️ Tu perfil puede consultar proveedores, pero no registrar nuevos.")
    tab_list = st.container()
    tab_new = None

if tab_new is not None:
    with tab_new:
        with st.container(border=True):
            section_header(
                "Registrar proveedor",
                "Cargá los datos comerciales y de contacto para poder vincularlo con los materiales del catálogo.",
                icon="🏭",
                badge="Nuevo proveedor",
            )
            with st.form("supplier_form", clear_on_submit=True):
                st.markdown('<p class="panel-heading">IDENTIFICACIÓN COMERCIAL Y CONTACTO</p>', unsafe_allow_html=True)
                supplier_name = st.text_input(
                    "Razón social o nombre comercial", placeholder="Ej. Aceros del Sur S.A."
                )
                rubro_col, phone_col = st.columns(2)
                with rubro_col:
                    supplier_business = st.text_input(
                        "Rubro / especialidad", placeholder="Ej. Perfiles, chapas y herrajes"
                    )
                with phone_col:
                    supplier_phone = st.text_input(
                        "Teléfono de contacto", placeholder="Ej. 11-4555-8900"
                    )
                supplier_submit = st.form_submit_button(
                    "💾 Guardar proveedor", type="primary", width="stretch"
                )
            if supplier_submit:
                try:
                    create_supplier(supplier_name, supplier_business, supplier_phone)
                    st.success("✅ Proveedor registrado correctamente.")
                    st.rerun()
                except (ValueError, SQLAlchemyError) as error:
                    database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))

with tab_list:
    with st.container(border=True):
        section_header(
            "Directorio de proveedores",
            "Consultá los rubros, teléfonos de contacto y cantidad de materiales provistos por cada empresa.",
            icon="🏭",
            badge=f"{len(suppliers)} proveedores",
        )
        material_counts = {}
        for material in materials:
            supplier_id = material["id_proveedor"]
            material_counts[supplier_id] = material_counts.get(supplier_id, 0) + 1
        supplier_rows = [
            {
                "N.º": supplier["id_proveedor"],
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
            "Todavía no hay proveedores registrados",
            "Abrí la pestaña «Registrar nuevo proveedor» para dar de alta el primero.",
        )
