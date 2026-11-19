"""Pantalla de inicio de sesión para usuarios existentes de MySQL."""

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.config import settings
from src.core.session import start_user_session
from src.services.auth_service import AuthService


def render_login() -> None:
    """Muestra el formulario y crea la sesión de Streamlit al validar."""
    st.markdown(
        f"""<div class="hero-panel"><p class="panel-heading">ACCESO SEGURO</p>
        <h1>{settings.app_name}</h1><p>Iniciá sesión con tu usuario del sistema.</p></div>""",
        unsafe_allow_html=True,
    )

    if st.session_state.pop("_session_expired", False):
        st.info("Tu sesión venció por inactividad. Volvé a ingresar.")

    left, center, right = st.columns([1, 1.15, 1])
    with center:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Usuario", max_chars=45, autocomplete="username")
            password = st.text_input("Contraseña", type="password", autocomplete="current-password")
            submitted = st.form_submit_button("Ingresar", type="primary", width="stretch")

        if not submitted:
            st.caption("La autenticación se valida contra la tabla `usuarios` existente.")
            return

        try:
            user, error = AuthService().login(username, password)
        except SQLAlchemyError as error:
            detail = str(error).casefold()
            if "rol" in detail and ("unknown column" in detail or "1054" in detail):
                st.error("Falta aplicar la migración database/migrations/20261119_add_usuario_rol.sql en MySQL.")
            else:
                st.error("No se pudo validar el usuario en MySQL. Revisá la conexión configurada.")
            return
        except (ValueError, TypeError):
            st.error("No se pudo validar el usuario. Revisá la configuración de autenticación.")
            return

        if error or user is None:
            st.error(error or "Las credenciales no son válidas.")
            return

        start_user_session(user)
        st.rerun()
