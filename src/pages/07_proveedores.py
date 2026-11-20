import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import puede_escribir
from src.core.session import obtener_usuario_actual
from src.services.material_service import crear_proveedor, listar_materiales, listar_proveedores
from src.ui import mostrar_error_bd, tarjeta_indicador, encabezado_pagina, mostrar_tabla_registros, encabezado_seccion

puede_editar = puede_escribir(obtener_usuario_actual())
encabezado_pagina(
    "ABASTECIMIENTO",
    "Proveedores",
    "Administrá las empresas y comercios que abastecen el catálogo de materiales del taller.",
    insignia="Cartera de proveedores",
)

proveedores = []
materiales = []
try:
    proveedores = listar_proveedores()
    materiales = listar_materiales()
except SQLAlchemyError:
    mostrar_error_bd()

ids_proveedores_asociados = {material["id_proveedor"] for material in materiales}
cantidad_rubros = len({(s.get("rubro") or "").strip().lower() for s in proveedores if (s.get("rubro") or "").strip()})

indicadores = st.columns(4)
with indicadores[0]:
    tarjeta_indicador("Proveedores totales", len(proveedores), "Registrados en el sistema", icono="🏭", tono="amber")
with indicadores[1]:
    tarjeta_indicador("Con insumos activos", len(ids_proveedores_asociados), "Presentes en el catálogo", icono="✅", tono="emerald")
with indicadores[2]:
    tarjeta_indicador("Rubros cubiertos", cantidad_rubros, "Especialidades registradas", icono="📦", tono="blue")
with indicadores[3]:
    tarjeta_indicador("Insumos provistos", len(materiales), "Total de materiales asociados", icono="🧱", tono="slate")

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
            encabezado_seccion(
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
                    crear_proveedor(nombre_proveedor, rubro_proveedor, telefono_proveedor)
                    st.success("✅ Proveedor registrado correctamente.")
                    st.rerun()
                except (ValueError, SQLAlchemyError) as error:
                    mostrar_error_bd() if isinstance(error, SQLAlchemyError) else st.error(str(error))

with pestana_lista:
    with st.container(border=True):
        encabezado_seccion(
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
        mostrar_tabla_registros(
            filas_proveedores,
            "suppliers",
            "Todavía no hay proveedores registrados",
            "Abrí la pestaña «Registrar nuevo proveedor» para dar de alta el primero.",
        )
