import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import can_write
from src.core.session import current_user
from src.services.material_service import create_supplier, list_materials, list_suppliers
from src.ui import database_error, kpi_card, page_header, records_table, section_header

puede_editar = can_write(current_user())
page_header(
    "ABASTECIMIENTO",
    "Proveedores",
    "Administrá las empresas y comercios que abastecen el catálogo de materiales del taller.",
    insignia="Cartera de proveedores",
)

proveedores = []
materiales = []
try:
    proveedores = list_suppliers()
    materiales = list_materials()
except SQLAlchemyError:
    database_error()

ids_proveedores_asociados = {material["id_proveedor"] for material in materiales}
cantidad_rubros = len({(s.get("rubro") or "").strip().lower() for s in proveedores if (s.get("rubro") or "").strip()})

indicadores = st.columns(4)
with indicadores[0]:
    kpi_card("Proveedores totales", len(proveedores), "Registrados en el sistema", icono="🏭", tono="amber")
with indicadores[1]:
    kpi_card("Con insumos activos", len(ids_proveedores_asociados), "Presentes en el catálogo", icono="✅", tono="emerald")
with indicadores[2]:
    kpi_card("Rubros cubiertos", cantidad_rubros, "Especialidades registradas", icono="📦", tono="blue")
with indicadores[3]:
    kpi_card("Insumos provistos", len(materiales), "Total de materiales asociados", icono="🧱", tono="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if puede_editar:
    pestana_lista, pestana_nuevo = st.tabs(["📋 Directorio de proveedores", "➕ Registrar nuevo proveedor"])
else:
    st.info("👁️ Tu perfil puede consultar proveedores, pero no registrar nuevos.")
    pestana_lista = st.container()
    pestana_nuevo = None

if pestana_nuevo is not None:
    with pestana_nuevo:
        with st.container(border=True):
            section_header(
                "Registrar proveedor",
                "Cargá los datos comerciales y de contacto para poder vincularlo con los materiales del catálogo.",
                icono="🏭",
                insignia="Nuevo proveedor",
            )
            with st.form("supplier_form", clear_on_submit=True):
                st.markdown('<p class="panel-heading">IDENTIFICACIÓN COMERCIAL Y CONTACTO</p>', unsafe_allow_html=True)
                nombre_proveedor = st.text_input(
                    "Razón social o nombre comercial", placeholder="Ej. Aceros del Sur S.A."
                )
                col_rubro, col_telefono = st.columns(2)
                with col_rubro:
                    rubro_proveedor = st.text_input(
                        "Rubro / especialidad", placeholder="Ej. Perfiles, chapas y herrajes"
                    )
                with col_telefono:
                    telefono_proveedor = st.text_input(
                        "Teléfono de contacto", placeholder="Ej. 11-4555-8900"
                    )
                enviar_proveedor = st.form_submit_button(
                    "💾 Guardar proveedor", type="primary", width="stretch"
                )
            if enviar_proveedor:
                try:
                    create_supplier(nombre_proveedor, rubro_proveedor, telefono_proveedor)
                    st.success("✅ Proveedor registrado correctamente.")
                    st.rerun()
                except (ValueError, SQLAlchemyError) as error:
                    database_error() if isinstance(error, SQLAlchemyError) else st.error(str(error))

with pestana_lista:
    with st.container(border=True):
        section_header(
            "Directorio de proveedores",
            "Consultá los rubros, teléfonos de contacto y cantidad de materiales provistos por cada empresa.",
            icono="🏭",
            insignia=f"{len(proveedores)} proveedores",
        )
        cantidades_materiales = {}
        for material in materiales:
            id_proveedor = material["id_proveedor"]
            cantidades_materiales[id_proveedor] = cantidades_materiales.get(id_proveedor, 0) + 1
        filas_proveedores = [
            {
                "N.º": proveedor["id_proveedor"],
                "Proveedor": proveedor["nombre"],
                "Rubro / especialidad": proveedor["rubro"],
                "Teléfono": proveedor["telefono"],
                "Materiales asociados": cantidades_materiales.get(proveedor["id_proveedor"], 0),
            }
            for proveedor in proveedores
        ]
        records_table(
            filas_proveedores,
            "suppliers",
            "Todavía no hay proveedores registrados",
            "Abrí la pestaña «Registrar nuevo proveedor» para dar de alta el primero.",
        )
