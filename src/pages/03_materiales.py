import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.material_service import (
    create_material,
    create_supplier,
    list_materials,
    list_suppliers,
)
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
    "ABASTECIMIENTO E INSUMOS",
    "Materiales y Proveedores",
    "Administrá el catálogo de insumos metalúrgicos, sus precios unitarios de referencia y la cartera de proveedores.",
    badge="Módulo Catálogo",
)

suppliers = []
materials = []
try:
    suppliers = list_suppliers()
    materials = list_materials()
except SQLAlchemyError:
    database_error()

avg_price = (
    sum(float(m["precio_unitario"] or 0) for m in materials) / len(materials)
    if materials
    else 0.0
)

kpis = st.columns(3)
with kpis[0]:
    kpi_card("Proveedores activos", len(suppliers), "Empresas y comercios aliados", icon="🏭", tone="blue")
with kpis[1]:
    kpi_card("Materiales en catálogo", len(materials), "Insumos listos para cotizar", icon="🧱", tone="amber")
with kpis[2]:
    kpi_card("Precio unitario promedio", currency(avg_price), "Referencia del catálogo actual", icon="🏷️", tone="emerald")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if can_edit:
    supplier_col, material_col = st.columns(2, gap="large")
    with supplier_col:
        with st.container(border=True):
            section_header(
                "Registrar proveedor",
                "Agregá un nuevo proveedor de insumos o servicios.",
                icon="🏭",
                badge="Proveedores",
            )
            with st.form("supplier_form"):
                supplier_name = st.text_input("Razón social o nombre", placeholder="Ej. Aceros del Sur S.A.")
                col_r, col_t = st.columns(2)
                with col_r:
                    supplier_business = st.text_input("Rubro / Especialidad", placeholder="Ej. Perfiles y chapas")
                with col_t:
                    supplier_phone = st.text_input("Teléfono de contacto", placeholder="Ej. 11-4555-8900")
                supplier_submit = st.form_submit_button("💾 Guardar proveedor", type="primary", width="stretch")
            if supplier_submit:
                try:
                    create_supplier(supplier_name, supplier_business, supplier_phone)
                    st.success("✅ Proveedor guardado en la base de datos.")
                    st.rerun()
                except (ValueError, SQLAlchemyError) as error:
                    database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))

    with material_col:
        with st.container(border=True):
            section_header(
                "Registrar material",
                "Vinculá cada insumo con su proveedor y costo unitario.",
                icon="🧱",
                badge="Insumos",
            )
            if suppliers:
                supplier_options = {
                    f"{supplier['nombre']} · {supplier['rubro']} (#{supplier['id_proveedor']})": supplier
                    for supplier in suppliers
                }
                with st.form("material_form"):
                    material_description = st.text_input(
                        "Descripción del material",
                        placeholder="Ej. Caño estructural 40x40x1.6 mm (barra 6m)",
                    )
                    col_p, col_s = st.columns([1, 1.25])
                    with col_p:
                        material_price = st.number_input(
                            "Precio unitario (ARS $)",
                            min_value=0.0,
                            value=0.0,
                            step=500.0,
                        )
                    with col_s:
                        supplier_label = st.selectbox("Proveedor habitual", list(supplier_options))
                    material_submit = st.form_submit_button("💾 Guardar material", type="primary", width="stretch")
                if material_submit:
                    try:
                        create_material(
                            material_description,
                            material_price,
                            supplier_options[supplier_label]["id_proveedor"],
                        )
                        st.success("✅ Material guardado en la base de datos.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("👈 Primero registrá al menos un proveedor en la tarjeta izquierda para poder cargar materiales.")
else:
    st.info("👁️ Tu perfil puede consultar materiales y proveedores, pero no puede registrar nuevos ítems.")

tab_mat, tab_sup = st.tabs([f"🧱 Catálogo de Materiales ({len(materials)})", f"🏭 Directorio de Proveedores ({len(suppliers)})"])

with tab_mat:
    with st.container(border=True):
        section_header(
            "Materiales registrados",
            "Precios unitarios utilizados automáticamente en el cálculo de presupuestos.",
            icon="🧱",
            badge="Catálogo",
        )
        material_rows = [
            {
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
            "Utilizá el formulario superior para registrar materiales y asociarlos con su proveedor.",
        )

with tab_sup:
    with st.container(border=True):
        section_header(
            "Proveedores registrados",
            "Listado de proveedores vinculados al catálogo de insumos.",
            icon="🏭",
            badge="Proveedores",
        )
        records_table(
            suppliers,
            "suppliers",
            "Todavía no hay proveedores",
            "Agregá proveedores desde el formulario superior izquierdo.",
        )
