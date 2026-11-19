"""Pantalla de inicio de sesión rediseñada con estética ejecutiva industrial."""

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.config import settings
from src.core.session import start_user_session
from src.services.auth_service import AuthService
from src.ui import get_logo_data_uri


def render_login() -> None:
    """Muestra la portada de acceso a pantalla completa y valida contra MySQL."""
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
          display: none !important;
        }
        .main .block-container {
          max-width: 1120px !important;
          padding-top: 3.2rem !important;
        }
        .login-showcase {
          display: grid;
          place-items: center;
          min-height: 620px;
          padding: 2rem;
          border-radius: 20px;
          background: radial-gradient(circle at 50% 48%, rgba(217, 119, 6, 0.15) 0%, transparent 48%),
                      linear-gradient(145deg, #0f172a 0%, #1e293b 65%, #27272a 100%);
          color: #f8fafc;
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.35);
          position: relative;
          overflow: hidden;
        }
        .login-hero-logo {
          position: relative;
          z-index: 1;
          display: block;
          width: min(100%, 500px);
          max-height: 560px;
          object-fit: contain;
          filter: drop-shadow(0 18px 26px rgba(0, 0, 0, 0.48));
        }
        .login-showcase::after {
          content: "";
          position: absolute;
          top: -60px;
          right: -60px;
          width: 220px;
          height: 220px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(217, 119, 6, 0.28) 0%, transparent 70%);
          pointer-events: none;
        }
        @media (max-width: 900px) {
          .main .block-container { padding-top: 1.5rem !important; }
          .login-showcase { min-height: 440px; }
          .login-hero-logo { width: min(100%, 390px); max-height: 390px; }
        }
        @media (max-width: 600px) {
          .login-showcase { min-height: 320px; padding: 1.25rem; }
          .login-hero-logo { width: min(100%, 300px); max-height: 300px; }
        }
        .login-card-header {
          margin-bottom: 1.1rem;
        }
        .login-lock-badge {
          width: 2.75rem;
          height: 2.75rem;
          border-radius: 12px;
          background: #fef3c7;
          border: 1px solid #fde68a;
          color: #b45309;
          display: grid;
          place-items: center;
          font-size: 1.25rem;
          margin-bottom: 0.85rem;
        }
        .login-card-header h2 {
          margin: 0;
          font-size: 1.45rem;
          font-weight: 800;
          color: #0f172a;
        }
        .login-card-header p {
          margin: 0.3rem 0 0;
          color: #64748b;
          font-size: 0.88rem;
        }
        .login-footer-note {
          margin-top: 0.85rem;
          padding: 0.65rem 0.85rem;
          border-radius: 10px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          color: #64748b;
          font-size: 0.78rem;
          text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.pop("_session_expired", False):
        st.warning("⏱️ Tu sesión venció por inactividad. Volvé a ingresar tus credenciales.")

    logo_uri = get_logo_data_uri()
    logo_hero_html = (
        f'<img class="login-hero-logo" src="{logo_uri}" alt="Emblema de Herrería Don Francisco" />'
        if logo_uri
        else '<div class="login-lock-badge">🔨</div>'
    )

    left_col, right_col = st.columns([1.25, 1], gap="large")

    with left_col:
        st.markdown(
            f"""
            <div class="login-showcase">
              {logo_hero_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="login-card-header">
                  <div class="login-lock-badge">🔐</div>
                  <h2>Iniciar sesión</h2>
                  <p>Ingresá con tu cuenta asignada para acceder al panel.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Usuario",
                    max_chars=45,
                    placeholder="Ej. admin",
                    autocomplete="username",
                )
                password = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="••••••••",
                    autocomplete="current-password",
                )
                submitted = st.form_submit_button("Ingresar al sistema →", type="primary", width="stretch")

            st.markdown(
                '<div class="login-footer-note">🛡️ Acceso protegido por usuario y rol asignado.</div>',
                unsafe_allow_html=True,
            )

            if not submitted:
                return

            try:
                user, error = AuthService().login(username, password)
            except SQLAlchemyError:
                st.error("No se pudo validar el acceso en este momento. Verificá la conexión del sistema.")
                return
            except (ValueError, TypeError):
                st.error("No se pudo validar el usuario. Revisá la configuración de autenticación.")
                return

            if error or user is None:
                st.error(error or "Las credenciales ingresadas no son válidas.")
                return

            start_user_session(user)
            st.rerun()
