import pandas as pd
import streamlit as st
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.authorization import ROLE_CODES, ROLE_LABELS, is_admin
from src.core.session import current_user
from src.services.auth_service import AuthService
from src.ui import database_error, kpi_card, page_header, section_header

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
    kpi_card("Cuentas totales", len(accounts), "Usuarios en MySQL", icon="👥", tone="slate")
with kpis[1]:
    kpi_card("Administradores", admins_count, "Control total del sistema", icon="🛡️", tone="amber")
with kpis[2]:
    kpi_card("Operadores", operators_count, "Gestión comercial y taller", icon="⚙️", tone="blue")
with kpis[3]:
    kpi_card("Auditores", auditors_count, "Acceso de solo lectura", icon="👁️", tone="emerald")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

col_create, col_manage = st.columns([1, 1.25], gap="large")

with col_create:
    with st.container(border=True):
        section_header(
            "Crear nueva cuenta",
            "Registrá un nuevo usuario con contraseña cifrada.",
            icon="➕",
            badge="Alta de usuario",
        )
        with st.form("create_app_user_form", clear_on_submit=True):
            name = st.text_input("Nombre y apellido", max_chars=45, placeholder="Ej. Lucas Fernández")
            username = st.text_input("Nombre de usuario (login)", max_chars=45, placeholder="Ej. lfernandez")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                password = st.text_input("Contraseña (mín. 8 caract.)", type="password")
            with p_col2:
                confirmation = st.text_input("Confirmar contraseña", type="password")
            role = st.selectbox(
                "Rol asignado",
                ROLE_CODES,
                format_func=lambda value: ROLE_LABELS[value],
            )
            submitted = st.form_submit_button("👤 Crear usuario", type="primary", width="stretch")
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

with col_manage:
    with st.container(border=True):
        section_header(
            "Directorio de cuentas y roles",
            "Consultá los perfiles activos y modificá sus permisos de acceso.",
            icon="🔐",
            badge=f"{len(accounts)} cuentas",
        )
        if accounts:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "ID": row["id_usuario"],
                            "Nombre completo": row["nombre"],
                            "Usuario": row["usuario"],
                            "Perfil / Rol": ROLE_LABELS.get(row["rol"], row["rol"]),
                        }
                        for row in accounts
                    ]
                ),
                hide_index=True,
                width="stretch",
            )

            st.markdown('<p class="panel-heading" style="margin-top:0.85rem;">MODIFICAR ROL DE UNA CUENTA</p>', unsafe_allow_html=True)
            account_options = {
                f"{row['usuario']} · {row['nombre']} ({ROLE_LABELS.get(row['rol'], row['rol'])})": row
                for row in accounts
            }
            selected_label = st.selectbox(
                "Cuenta a modificar",
                list(account_options),
                key="role_user_selection",
            )
            selected_user = account_options[selected_label]
            with st.form("update_user_role_form"):
                new_role = st.selectbox(
                    "Nuevo rol de acceso",
                    ROLE_CODES,
                    index=ROLE_CODES.index(selected_user["rol"]),
                    format_func=lambda value: ROLE_LABELS[value],
                )
                update = st.form_submit_button("💾 Actualizar rol", type="primary", width="stretch")
            if update:
                try:
                    service.update_role(
                        selected_user["id_usuario"],
                        new_role,
                        actor_user_id=user["id_usuario"],
                    )
                    st.success("✅ Rol actualizado en MySQL.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except SQLAlchemyError:
                    database_error()
        else:
            st.info(
                "Todavía no hay cuentas registradas. Para registrar la primera cuenta, ejecutá `python -m src.core.create_user`."
            )
