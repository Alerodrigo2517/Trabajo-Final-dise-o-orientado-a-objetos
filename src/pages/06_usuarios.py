import streamlit as st
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.authorization import ROLE_CODES, ROLE_LABELS, is_admin
from src.core.session import current_user
from src.services.auth_service import AuthService
from src.ui import (
    database_error,
    kpi_card,
    page_header,
    records_table,
    section_header,
)

user = current_user()
if not is_admin(user):
    st.error("🔒 Esta sección está disponible únicamente para perfiles con rol Administrador.")
    st.stop()

page_header(
    "SEGURIDAD Y ACCESOS",
    "Usuarios del Sistema",
    "Administrá las cuentas de acceso del personal y asigná permisos operativos por rol (Administrador, Operador o Auditor).",
    badge="Solo Administradores",
)

service = AuthService()
accounts = []
try:
    accounts = service.list_users()
except SQLAlchemyError:
    database_error()

admins_count = sum(1 for a in accounts if a["rol"] == "ADMIN")
operators_count = sum(1 for a in accounts if a["rol"] == "OPERADOR")
auditors_count = sum(1 for a in accounts if a["rol"] == "AUDITOR")

kpis = st.columns(4)
with kpis[0]:
    kpi_card("Cuentas totales", len(accounts), "Usuarios activos en el sistema", icon="👥", tone="amber")
with kpis[1]:
    kpi_card("Administradores", admins_count, "Control total del sistema", icon="🛡️", tone="emerald")
with kpis[2]:
    kpi_card("Operadores", operators_count, "Gestión comercial y taller", icon="⚙️", tone="blue")
with kpis[3]:
    kpi_card("Auditores", auditors_count, "Acceso de solo lectura", icon="👁️", tone="slate")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

tab_list, tab_new = st.tabs(
    [
        "📋 Directorio de cuentas y roles",
        "➕ Crear nueva cuenta de usuario",
    ]
)

with tab_new:
    with st.container(border=True):
        section_header(
            "Registrar nueva cuenta de usuario",
            "Creá un perfil de acceso y asignale su nivel de permisos operativos en el sistema.",
            icon="👤",
            badge="Alta de usuario",
        )
        with st.form("create_app_user_form", clear_on_submit=True):
            st.markdown('<p class="panel-heading">IDENTIFICACIÓN Y NIVEL DE ACCESO</p>', unsafe_allow_html=True)
            col_name, col_user, col_role = st.columns([1.2, 1, 1])
            with col_name:
                name = st.text_input("Nombre y apellido", max_chars=45, placeholder="Ej. Lucas Fernández")
            with col_user:
                username = st.text_input("Nombre de usuario (login)", max_chars=45, placeholder="Ej. lfernandez")
            with col_role:
                role = st.selectbox(
                    "Rol asignado",
                    ROLE_CODES,
                    format_func=lambda value: ROLE_LABELS[value],
                )

            st.markdown('<p class="panel-heading" style="margin-top:0.65rem;">CREDENCIALES DE SEGURIDAD</p>', unsafe_allow_html=True)
            st.caption("Definí una contraseña de al menos 8 caracteres para el ingreso del usuario.")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                password = st.text_input(
                    "Contraseña (mínimo 8 caracteres)",
                    type="password",
                    placeholder="Ingresá una contraseña segura",
                )
            with p_col2:
                confirmation = st.text_input(
                    "Repetir contraseña",
                    type="password",
                    placeholder="Confirmá la contraseña",
                )

            submitted = st.form_submit_button("💾 Crear cuenta de usuario", type="primary", width="stretch")

        if submitted:
            if password != confirmation:
                st.error("Las contraseñas ingresadas no coinciden.")
            else:
                try:
                    service.create_account(name, username, password, role)
                    st.success(f"✅ Cuenta para «{username.strip()}» creada con perfil {ROLE_LABELS[role]}.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except IntegrityError:
                    st.error("Ese nombre de usuario ya está registrado.")
                except SQLAlchemyError:
                    database_error()

with tab_list:
    if accounts:
        with st.container(border=True):
            section_header(
                "Actualizar rol de una cuenta",
                "Seleccioná un usuario existente para modificar sus permisos operativos dentro del sistema.",
                icon="🔄",
                badge="Gestión de permisos",
            )
            account_options = {
                f"#{row['id_usuario']} · {row['nombre']} (@{row['usuario']}) · {ROLE_LABELS.get(row['rol'], row['rol'])}": row
                for row in accounts
            }
            col_sel, col_form = st.columns([1.3, 1], gap="large")
            with col_sel:
                selected_label = st.selectbox(
                    "Seleccionar cuenta de usuario",
                    list(account_options),
                    key="role_user_selection",
                )
                selected_user = account_options[selected_label]
                st.caption(
                    f"Usuario: **@{selected_user['usuario']}** · Nombre: **{selected_user['nombre']}** · "
                    f"Rol actual: **{ROLE_LABELS.get(selected_user['rol'], selected_user['rol'])}**"
                )
            with col_form:
                with st.form("update_user_role_form"):
                    new_role = st.selectbox(
                        "Nuevo rol de acceso",
                        ROLE_CODES,
                        index=ROLE_CODES.index(selected_user["rol"]),
                        format_func=lambda value: ROLE_LABELS[value],
                    )
                    update = st.form_submit_button("Guardar nuevo rol", type="primary", width="stretch")
                if update:
                    try:
                        service.update_role(
                            selected_user["id_usuario"],
                            new_role,
                            actor_user_id=user["id_usuario"],
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
                icon="🔐",
                badge=f"{len(accounts)} cuentas",
            )
            user_rows = [
                {
                    "ID": row["id_usuario"],
                    "Nombre completo": row["nombre"],
                    "Usuario": row["usuario"],
                    "Perfil / Rol": ROLE_LABELS.get(row["rol"], row["rol"]),
                }
                for row in accounts
            ]
            records_table(
                user_rows,
                "usuarios_db",
                "Todavía no hay cuentas registradas",
                "Abrí la pestaña «Crear nueva cuenta de usuario» para dar de alta un nuevo perfil.",
            )
    else:
        st.info("Todavía no hay cuentas registradas en el sistema.")
