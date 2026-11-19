import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.material_service import create_material, create_supplier, list_materials, list_suppliers
from src.ui import currency, database_error, page_header, records_table

can_edit = can_write(current_user())
page_header("ABASTECIMIENTO", "Materiales y proveedores", "Consultá precios y proveedores desde las tablas existentes de la base de datos.")

suppliers = []
materials = []
try:
    suppliers = list_suppliers()
    materials = list_materials()
except SQLAlchemyError:
    database_error()

if can_edit:
    supplier_col, material_col = st.columns(2, gap="large")
    with supplier_col:
        with st.container(border=True):
            st.subheader("Nuevo proveedor")
            with st.form("supplier_form"):
                supplier_name = st.text_input("Nombre")
                supplier_business = st.text_input("Rubro")
                supplier_phone = st.text_input("Teléfono")
                supplier_submit = st.form_submit_button("Guardar proveedor", type="primary", width="stretch")
            if supplier_submit:
                try:
                    create_supplier(supplier_name, supplier_business, supplier_phone)
                    st.success("Proveedor guardado en la base de datos.")
                    st.rerun()
                except (ValueError, SQLAlchemyError) as error:
                    database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))

    with material_col:
        with st.container(border=True):
            st.subheader("Nuevo material")
            if suppliers:
                supplier_options = {
                    f"{supplier['nombre']} · {supplier['rubro']} · #{supplier['id_proveedor']}": supplier
                    for supplier in suppliers
                }
                with st.form("material_form"):
                    material_description = st.text_input("Descripción")
                    material_price = st.number_input("Precio unitario (ARS $)", min_value=0.0, value=0.0, step=100.0)
                    supplier_label = st.selectbox("Proveedor", list(supplier_options))
                    material_submit = st.form_submit_button("Guardar material", type="primary", width="stretch")
                if material_submit:
                    try:
                        create_material(material_description, material_price, supplier_options[supplier_label]["id_proveedor"])
                        st.success("Material guardado en la base de datos.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("Registrá un proveedor antes de cargar un material.")
else:
    st.info("Tu perfil puede consultar materiales y proveedores, pero no puede registrarlos.")

st.info("El esquema actual registra descripción, precio unitario y proveedor. No tiene columnas de unidad, cantidad en stock ni stock mínimo.")
st.subheader("Proveedores registrados")
records_table(suppliers, "suppliers", "Todavía no hay proveedores", "Agregá proveedores desde el formulario de arriba.")
st.subheader("Materiales registrados")
material_rows = [
    {"Descripción": row["descripcion"], "Precio unitario": currency(row["precio_unitario"]), "Proveedor": row["proveedor"]}
    for row in materials
]
records_table(material_rows, "materials", "Todavía no hay materiales", "Agregá materiales y asocialos con un proveedor.")
