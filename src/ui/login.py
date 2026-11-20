"""Pantalla de inicio de sesión rediseñada con estética ejecutiva industrial."""

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.config import configuracion
from src.core.session import start_user_session as iniciar_sesion_usuario
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
          box-sizing: border-box;
          min-height: calc(100dvh - 3rem);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0.75rem 1.2rem !important;
        }
        .main .block-container > div[data-testid="stVerticalBlock"] {
          width: 100%;
        }
        .login-showcase {
          display: grid;
          place-items: center;
          height: min(76vh, 600px);
          min-height: 360px;
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
          .main .block-container { min-height: calc(100dvh - 2rem); padding: 0.75rem !important; }
          .login-showcase { height: min(72vh, 520px); min-height: 320px; }
          .login-hero-logo { width: min(100%, 360px); max-height: 440px; }
        }
        @media (max-width: 600px) {
          .main .block-container { min-height: auto; }
          .login-showcase { height: min(36vh, 230px); min-height: 180px; padding: 1.1rem; }
          .login-hero-logo { width: min(100%, 220px); max-height: 215px; }
          .login-card-header h2 { font-size: 1.3rem; }
        }
        .login-card-header {
          margin-bottom: 1.1rem;
          text-align: center;
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
          margin: 0 auto 0.85rem;
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
        [data-testid="stTextInput"] button[aria-label="Show password"],
        [data-testid="stTextInput"] button[aria-label="Hide password"] {
          color: #475569 !important;
          border: 0 !important;
          border-radius: 7px !important;
          background: transparent !important;
          box-shadow: none !important;
        }
        [data-testid="stTextInput"] button[aria-label="Show password"]:hover,
        [data-testid="stTextInput"] button[aria-label="Hide password"]:hover {
          color: #0f172a !important;
          background: #f1f5f9 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.pop("_session_expired", False):
        st.warning("⏱️ Tu sesión venció por inactividad. Volvé a ingresar tus credenciales.")

    uri_logo = get_logo_data_uri()
    logo_hero_html = (
        f'<img class="login-hero-logo" src="{uri_logo}" alt="Emblema de Herrería Don Francisco" />'
        if uri_logo
        else '<div class="login-lock-badge">🔨</div>'
    )

    col_izquierda, col_derecha = st.columns([1.25, 1], gap="large", vertical_alignment="center")

    with col_izquierda:
        st.markdown(
            f"""
            <div class="login-showcase">
              {logo_hero_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_derecha:
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
                nombre_usuario = st.text_input(
                    "Usuario",
                    max_chars=45,
                    placeholder="Ej. admin",
                    autocomplete="username",
                )
                contrasena = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="••••••••",
                    autocomplete="current-password",
                )
                enviado = st.form_submit_button("Ingresar al sistema →", type="primary", width="stretch")

            st.markdown(
                '<div class="login-footer-note">🛡️ Acceso protegido por usuario y rol asignado.</div>',
                unsafe_allow_html=True,
            )

            if not enviado:
                return

            try:
                usuario, error = AuthService().login(nombre_usuario, contrasena)
            except SQLAlchemyError:
                st.error("No se pudo validar el acceso en este momento. Verificá la conexión del sistema.")
                return
            except (ValueError, TypeError):
                st.error("No se pudo validar el usuario. Revisá la configuración de autenticación.")
                return

            if error or usuario is None:
                st.error(error or "Las credenciales ingresadas no son válidas.")
                return

            iniciar_sesion_usuario(usuario)
            st.rerun()
