import streamlit as st
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.authorization import CODIGOS_ROL, ETIQUETAS_ROL, is_admin
from src.core.session import current_user
from src.services.auth_service import AuthService
from src.ui import (
    database_error,
    kpi_card,
    page_header,
    records_table,
    section_header,
)

usuario = current_user()
if not is_admin(usuario):
    st.error("🔒 Esta sección está disponible únicamente para perfiles con rol Administrador.")
    st.stop()

page_header(
    "SEGURIDAD Y ACCESOS",
    "Usuarios del Sistema",
    "Administrá las cuentas de acceso del personal y asigná permisos operativos por rol (Administrador, Operador o Auditor).",
    insignia="Solo Administradores",
)

servicio = AuthService()
cuentas = []
try:
    cuentas = servicio.list_users()
except SQLAlchemyError:
    database_error()

cantidad_administradores = sum(1 for a in cuentas if a["rol"] == "ADMIN")
cantidad_operadores = sum(1 for a in cuentas if a["rol"] == "OPERADOR")
cantidad_auditores = sum(1 for a in cuentas if a["rol"] == "AUDITOR")

indicadores = st.columns(4)
with indicadores[0]:
    kpi_card("Cuentas totales", len(cuentas), "Usuarios activos en el sistema", icono="👥", tono="amber")
with indicadores[1]:
    kpi_card("Administradores", cantidad_administradores, "Control total del sistema", icono="🛡️", tono="emerald")
with indicadores[2]:
    kpi_card("Operadores", cantidad_operadores, "Gestión comercial y taller", icono="⚙️", tono="blue")
with indicadores[3]:
    kpi_card("Auditores", cantidad_auditores, "Acceso de solo lectura", icono="👁️", tono="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

pestana_lista, pestana_nuevo = st.tabs(
    [
        "📋 Directorio de cuentas y roles",
        "➕ Crear nueva cuenta de usuario",
    ]
)

with pestana_nuevo:
    with st.container(border=True):
        section_header(
            "Registrar nueva cuenta de usuario",
            "Creá un perfil de acceso y asignale su nivel de permisos operativos en el sistema.",
            icono="👤",
            insignia="Alta de usuario",
        )
        with st.form("create_app_user_form", clear_on_submit=True):
            st.markdown('<p class="panel-heading">IDENTIFICACIÓN Y NIVEL DE ACCESO</p>', unsafe_allow_html=True)
            col_nombre, col_usuario, col_rol = st.columns([1.2, 1, 1])
            with col_nombre:
                nombre = st.text_input("Nombre y apellido", max_chars=45, placeholder="Ej. Lucas Fernández")
            with col_usuario:
                nombre_usuario = st.text_input("Nombre de usuario (login)", max_chars=45, placeholder="Ej. lfernandez")
            with col_rol:
                rol = st.selectbox(
                    "Rol asignado",
                    CODIGOS_ROL,
                    format_func=lambda valor: ETIQUETAS_ROL[valor],
                )

            st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">CREDENCIALES DE SEGURIDAD</p>', unsafe_allow_html=True)
            st.caption("Definí una contraseña de al menos 8 caracteres para el ingreso del usuario.")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                contrasena = st.text_input(
                    "Contraseña (mínimo 8 caracteres)",
                    type="password",
                    placeholder="Ingresá una contraseña segura",
                )
            with p_col2:
                confirmacion = st.text_input(
                    "Repetir contraseña",
                    type="password",
                    placeholder="Confirmá la contraseña",
                )

            enviado = st.form_submit_button("💾 Crear cuenta de usuario", type="primary", width="stretch")

        if enviado:
            if contrasena != confirmacion:
                st.error("Las contraseñas ingresadas no coinciden.")
            else:
                try:
                    servicio.create_account(nombre, nombre_usuario, contrasena, rol)
                    st.success(f"✅ Cuenta para «{nombre_usuario.strip()}» creada con perfil {ETIQUETAS_ROL[rol]}.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except IntegrityError:
                    st.error("Ese nombre de usuario ya está registrado.")
                except SQLAlchemyError:
                    database_error()

with pestana_lista:
    if cuentas:
        with st.container(border=True):
            section_header(
                "Actualizar rol de una cuenta",
                "Seleccioná un usuario existente para modificar sus permisos operativos dentro del sistema.",
                icono="🔄",
                insignia="Gestión de permisos",
            )
            opciones_cuentas = {
                f"#{fila['id_usuario']} · {fila['nombre']} (@{fila['usuario']}) · {ETIQUETAS_ROL.get(fila['rol'], fila['rol'])}": fila
                for fila in cuentas
            }
            col_selector, col_formulario = st.columns([1.3, 1], gap="large")
            with col_selector:
                etiqueta_seleccionada = st.selectbox(
                    "Seleccionar cuenta de usuario",
                    list(opciones_cuentas),
                    key="role_user_selection",
                )
                usuario_seleccionado = opciones_cuentas[etiqueta_seleccionada]
                st.caption(
                    f"Usuario: **@{usuario_seleccionado['usuario']}** · Nombre: **{usuario_seleccionado['nombre']}** · "
                    f"Rol actual: **{ETIQUETAS_ROL.get(usuario_seleccionado['rol'], usuario_seleccionado['rol'])}**"
                )
            with col_formulario:
                with st.form("update_user_role_form"):
                    rol_nuevo = st.selectbox(
                        "Nuevo rol de acceso",
                        CODIGOS_ROL,
                        index=CODIGOS_ROL.index(usuario_seleccionado["rol"]),
                        format_func=lambda valor: ETIQUETAS_ROL[valor],
                    )
                    update = st.form_submit_button("Guardar nuevo rol", type="primary", width="stretch")
                if update:
                    try:
                        servicio.update_role(
                            usuario_seleccionado["id_usuario"],
                            rol_nuevo,
                            actor_user_id=usuario["id_usuario"],
                        )
                        st.success("✅ Rol actualizado correctamente.")
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))
                    except SQLAlchemyError:
                        database_error()

        with st.container(border=True):
            section_header(
                "Directorio de cuentas registradas",
                "Listado completo de usuarios habilitados con su identificador, nombre de acceso y perfil asignado.",
                icono="🔐",
                insignia=f"{len(cuentas)} cuentas",
            )
            filas_usuarios = [
                {
                    "ID": fila["id_usuario"],
                    "Nombre completo": fila["nombre"],
                    "Usuario": fila["usuario"],
                    "Perfil / Rol": ETIQUETAS_ROL.get(fila["rol"], fila["rol"]),
                }
                for fila in cuentas
            ]
            records_table(
                filas_usuarios,
                "usuarios_db",
                "Todavía no hay cuentas registradas",
                "Abrí la pestaña «Crear nueva cuenta de usuario» para dar de alta un nuevo perfil.",
            )
    else:
        st.info("Todavía no hay cuentas registradas en el sistema.")
