import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.authorization import puede_escribir
from src.core.session import obtener_usuario_actual
from src.services.material_service import crear_material, listar_materiales, listar_proveedores
from src.ui import (
    formatear_moneda,
    mostrar_error_bd,
    tarjeta_indicador,
    encabezado_pagina,
    mostrar_tabla_registros,
    encabezado_seccion,
)

puede_editar = puede_escribir(obtener_usuario_actual())
encabezado_pagina(
    "ABASTECIMIENTO",
    "Materiales",
    "Mantené el catálogo de insumos metalúrgicos y sus precios unitarios de referencia para cotizar presupuestos.",
    insignia="Catálogo de insumos",
)

proveedores = []
materiales = []
try:
    proveedores = listar_proveedores()
    materiales = listar_materiales()
except SQLAlchemyError:
    mostrar_error_bd()

precio_promedio = (
    sum(float(material["precio_unitario"] or 0) for material in materiales) / len(materiales)
    if materiales
    else 0.0
)
precio_maximo = max((float(material["precio_unitario"] or 0) for material in materiales), default=0.0)
proveedores_asociados = len({material["id_proveedor"] for material in materiales})

indicadores = st.columns(4)
with indicadores[0]:
    tarjeta_indicador("Materiales en catálogo", len(materiales), "Insumos listos para cotizar", icono="🧱", tono="amber")
with indicadores[1]:
    tarjeta_indicador("Precio promedio", formatear_moneda(precio_promedio), "Referencia del catálogo actual", icono="🏷️", tono="emerald")
with indicadores[2]:
    tarjeta_indicador("Mayor valor unitario", formatear_moneda(precio_maximo), "Insumo de mayor costo", icono="📈", tono="blue")
with indicadores[3]:
    tarjeta_indicador("Proveedores vinculados", proveedores_asociados, f"De {len(proveedores)} proveedores activos", icono="🏭", tono="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if puede_editar:
    pestana_lista, pestana_nuevo = st.tabs(["📋 Catálogo de materiales registrados", "➕ Registrar nuevo material"])
else:
    st.info("👁️ Tu perfil puede consultar el catálogo, pero no registrar materiales.")
    pestana_lista = st.container()
    pestana_nuevo = None

if pestana_nuevo is not None:
    with pestana_nuevo:
        with st.container(border=True):
            encabezado_seccion(
                "Registrar material",
                "Definí la descripción técnica del insumo, su costo unitario y el proveedor habitual.",
                icono="🧱",
                insignia="Nuevo insumo",
            )
            if proveedores:
                opciones_proveedores = {
                    f"{proveedor['nombre']} · {proveedor['rubro']} (#{proveedor['id_proveedor']})": proveedor
                    for proveedor in proveedores
                }
                with st.form("material_form", clear_on_submit=True):
                    st.markdown('<p class="panel-heading">ESPECIFICACIÓN Y COSTO DEL INSUMO</p>', unsafe_allow_html=True)
                    descripcion_material = st.text_input(
                        "Descripción del material",
                        placeholder="Ej. Caño estructural 40x40x1.6 mm (barra 6 m)",
                    )
                    col_precio, col_proveedor = st.columns([1, 1.25])
                    with col_precio:
                        precio_material = st.number_input(
                            "Precio unitario (ARS $)", min_value=0.0, value=0.0, step=500.0
                        )
                    with col_proveedor:
                        etiqueta_proveedor = st.selectbox("Proveedor habitual", list(opciones_proveedores))
                    material_submit = st.form_submit_button(
                        "💾 Guardar material", type="primary", width="stretch"
                    )
                if material_submit:
                    try:
                        crear_material(
                            descripcion_material,
                            precio_material,
                            opciones_proveedores[etiqueta_proveedor]["id_proveedor"],
                        )
                        st.success("✅ Material registrado correctamente.")
                        st.rerun()
                    except (ValueError, SQLAlchemyError) as error:
                        mostrar_error_bd() if isinstance(error, SQLAlchemyError) else st.error(str(error))
            else:
                st.info("Primero registrá un proveedor para poder asociarlo con el material.")
                st.page_link("src/pages/07_proveedores.py", label="Ir a Proveedores", icon="🏭")

with pestana_lista:
    with st.container(border=True):
        encabezado_seccion(
            "Materiales registrados",
            "Precios unitarios utilizados automáticamente al confeccionar presupuestos.",
            icono="🧱",
            insignia=f"{len(materiales)} insumos",
        )
        filas_materiales = [
            {
                "N.º": fila["id_material"],
                "Descripción": fila["descripcion"],
                "Precio unitario": formatear_moneda(fila["precio_unitario"]),
                "Proveedor": fila["proveedor"],
            }
            for fila in materiales
        ]
        mostrar_tabla_registros(
            filas_materiales,
            "materials",
            "Todavía no hay materiales cargados",
            "Abrí la pestaña «Registrar nuevo material» para cargar insumos al catálogo.",
        )
