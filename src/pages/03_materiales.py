import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.material_service import create_material, list_materials, list_suppliers
from src.ui import (
    currency,
    database_error,
    kpi_card,
    page_header,
    records_table,
    section_header,
)

can_edit = can_write(current_user())
page_header(
    "ABASTECIMIENTO",
    "Materiales",
    "Mantené el catálogo de insumos metalúrgicos y sus precios unitarios de referencia para cotizar presupuestos.",
    badge="Catálogo de insumos",
)

suppliers = []
materials = []
try:
    suppliers = list_suppliers()
    materials = list_materials()
except SQLAlchemyError:
    database_error()

avg_price = (
    sum(float(material["precio_unitario"] or 0) for material in materials) / len(materials)
    if materials
    else 0.0
)
max_price = max((float(material["precio_unitario"] or 0) for material in materials), default=0.0)
linked_suppliers = len({material["id_proveedor"] for material in materials})

kpis = st.columns(4)
with kpis[0]:
    kpi_card("Materiales en catálogo", len(materials), "Insumos listos para cotizar", icon="🧱", tone="amber")
with kpis[1]:
    kpi_card("Precio promedio", currency(avg_price), "Referencia del catálogo actual", icon="🏷️", tone="emerald")
with kpis[2]:
    kpi_card("Mayor valor unitario", currency(max_price), "Insumo de mayor costo", icon="📈", tone="blue")
with kpis[3]:
    kpi_card("Proveedores vinculados", linked_suppliers, f"De {len(suppliers)} proveedores activos", icon="🏭", tone="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    tab_list, tab_new = st.tabs(["📋 Catálogo de materiales registrados", "➕ Registrar nuevo material"])
else:
    st.info("👁️ Tu perfil puede consultar el catálogo, pero no registrar materiales.")
    tab_list = st.container()
    tab_new = None

if tab_new is not None:
    with tab_new:
        with st.container(border=True):
            section_header(
                "Registrar material",
                "Definí la descripción técnica del insumo, su costo unitario y el proveedor habitual.",
                icon="🧱",
                badge="Nuevo insumo",
            )
            if suppliers:
                supplier_options = {
                    f"{supplier['nombre']} · {supplier['rubro']} (#{supplier['id_proveedor']})": supplier
                    for supplier in suppliers
                }
                with st.form("material_form", clear_on_submit=True):
                    st.markdown('<p class="panel-heading">ESPECIFICACIÓN Y COSTO DEL INSUMO</p>', unsafe_allow_html=True)
                    material_description = st.text_input(
                        "Descripción del material",
                        placeholder="Ej. Caño estructural 40x40x1.6 mm (barra 6 m)",
                    )
                    price_col, supplier_col = st.columns([1, 1.25])
                    with price_col:
                        material_price = st.number_input(
                            "Precio unitario (ARS $)", min_value=0.0, value=0.0, step=500.0
                        )
                    with supplier_col:
                        supplier_label = st.selectbox("Proveedor habitual", list(supplier_options))
                    material_submit = st.form_submit_button(
                        "💾 Guardar material", type="primary", width="stretch"
                    )
                if material_submit:
                    try:
                        create_material(
                            material_description,
                            material_price,
                            supplier_options[supplier_label]["id_proveedor"],
                        )
                        st.success("✅ Material registrado correctamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("Primero registrá un proveedor para poder asociarlo con el material.")
                st.page_link("src/pages/07_proveedores.py", label="Ir a Proveedores", icon="🏭")

with tab_list:
    with st.container(border=True):
        section_header(
            "Materiales registrados",
            "Precios unitarios utilizados automáticamente al confeccionar presupuestos.",
            icon="🧱",
            badge=f"{len(materials)} insumos",
        )
        material_rows = [
            {
                "N.º": row["id_material"],
                "Descripción": row["descripcion"],
                "Precio unitario": currency(row["precio_unitario"]),
                "Proveedor": row["proveedor"],
            }
            for row in materials
        ]
        records_table(
            material_rows,
            "materials",
            "Todavía no hay materiales cargados",
            "Abrí la pestaña «Registrar nuevo material» para cargar insumos al catálogo.",
        )
