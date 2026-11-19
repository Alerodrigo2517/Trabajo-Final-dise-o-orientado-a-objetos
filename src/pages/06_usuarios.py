import pandas as pd
import streamlit as st
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.core.authorization import ROLE_CODES, ROLE_LABELS, is_admin
from src.core.session import current_user
from src.services.auth_service import AuthService
from src.ui import database_error, page_header

user = current_user()
if not is_admin(user):
    st.error("Esta sección está disponible solo para administradores.")
    st.stop()

page_header("ADMINISTRACIÓN", "Usuarios del sistema", "Administrá cuentas y roles en la tabla usuarios existente.")
service = AuthService()
with st.container(border=True):
    st.subheader("Crear cuenta")
    with st.form("create_app_user_form", clear_on_submit=True):
        name = st.text_input("Nombre completo", max_chars=45)
        username = st.text_input("Nombre de usuario", max_chars=45)
        password = st.text_input("Contraseña (mínimo 8 caracteres)", type="password")
        confirmation = st.text_input("Repetir contraseña", type="password")
        role = st.selectbox("Tipo de usuario", ROLE_CODES,
                            format_func=lambda value: ROLE_LABELS[value])
        submitted = st.form_submit_button("Crear usuario", type="primary")
    if submitted:
        if password != confirmation:
            st.error("Las contraseñas no coinciden.")
        else:
            try:
                service.create_account(name, username, password, role)
                st.success(f"Cuenta para {username.strip()} creada como {ROLE_LABELS[role]}.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
            except IntegrityError:
                st.error("Ese nombre de usuario ya está registrado.")
            except SQLAlchemyError:
                database_error()

st.subheader("Cuentas y roles")
try:
    accounts = service.list_users()
    if accounts:
        account_options = {
            f"{row['usuario']} · {row['nombre']} · {ROLE_LABELS.get(row['rol'], row['rol'])}": row
            for row in accounts
        }
        st.dataframe(pd.DataFrame([
            {"ID": row["id_usuario"], "Nombre": row["nombre"],
             "Usuario": row["usuario"], "Perfil": ROLE_LABELS.get(row["rol"], row["rol"])}
            for row in accounts
        ]), hide_index=True, width="stretch")
        selected_label = st.selectbox("Cuenta a modificar", list(account_options),
                                      key="role_user_selection")
        selected_user = account_options[selected_label]
        with st.form("update_user_role_form"):
            new_role = st.selectbox(
                "Nuevo tipo de usuario", ROLE_CODES,
                index=ROLE_CODES.index(selected_user["rol"]),
                format_func=lambda value: ROLE_LABELS[value],
            )
            update = st.form_submit_button("Guardar rol")
        if update:
            try:
                service.update_role(selected_user["id_usuario"], new_role,
                                    actor_user_id=user["id_usuario"])
                st.success("Rol actualizado en MySQL.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
            except SQLAlchemyError:
                database_error()
    else:
        st.info("Todavía no hay cuentas. Para registrar la primera cuenta, ejecutá python -m src.core.create_user.")
except SQLAlchemyError:
    database_error()
