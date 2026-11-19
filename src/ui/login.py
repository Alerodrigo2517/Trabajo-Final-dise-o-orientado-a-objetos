"""Pantalla de inicio de sesión rediseñada con estética ejecutiva industrial."""

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.core.config import settings
from src.core.session import start_user_session
from src.services.auth_service import AuthService


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
          padding: 2.35rem 2.25rem;
          border-radius: 20px;
          background: linear-gradient(145deg, #0f172a 0%, #1e293b 65%, #27272a 100%);
          color: #f8fafc;
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.35);
          height: 100%;
          position: relative;
          overflow: hidden;
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
        .login-brand-pill {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.35rem 0.85rem;
          border-radius: 999px;
          background: rgba(217, 119, 6, 0.18);
          border: 1px solid rgba(251, 191, 36, 0.35);
          color: #fbbf24;
          font-size: 0.72rem;
          font-weight: 700;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          margin-bottom: 1.25rem;
        }
        .login-showcase h1 {
          color: #ffffff !important;
          font-size: clamp(1.85rem, 2.6vw, 2.35rem);
          font-weight: 800;
          line-height: 1.15;
          margin: 0 0 0.75rem;
          letter-spacing: -0.03em;
        }
        .login-showcase p.lead {
          color: #cbd5e1;
          font-size: 0.96rem;
          line-height: 1.6;
          margin: 0 0 1.65rem;
        }
        .login-feature-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 0.85rem;
          margin-top: 1.25rem;
        }
        .login-feature-item {
          padding: 0.9rem 1rem;
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .login-feature-item strong {
          display: block;
          color: #f8fafc;
          font-size: 0.84rem;
          font-weight: 700;
          margin-bottom: 0.2rem;
        }
        .login-feature-item span {
          color: #94a3b8;
          font-size: 0.76rem;
          line-height: 1.4;
          display: block;
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

    left_col, right_col = st.columns([1.25, 1], gap="large")

    with left_col:
        st.markdown(
            f"""
            <div class="login-showcase">
              <div class="login-brand-pill">🔨 PLATAFORMA DE GESTIÓN INDUSTRIAL</div>
              <h1>{settings.app_name}</h1>
              <p class="lead">
                Control integral del taller en tiempo real: desde la primera cotización y cálculo de materiales
                hasta la orden de producción y seguimiento de cobros.
              </p>
              <div class="login-feature-grid">
                <div class="login-feature-item">
                  <strong>📐 Presupuestos precisos</strong>
                  <span>Cálculo automático de materiales y mano de obra por hora o porcentaje.</span>
                </div>
                <div class="login-feature-item">
                  <strong>⚙️ Órdenes de trabajo</strong>
                  <span>Seguimiento de fabricación, estados de obra y fechas de entrega.</span>
                </div>
                <div class="login-feature-item">
                  <strong>💳 Caja y cobranzas</strong>
                  <span>Registro de pagos parciales o totales y control de saldos pendientes.</span>
                </div>
                <div class="login-feature-item">
                  <strong>🔐 Control por roles</strong>
                  <span>Permisos diferenciados para Administradores, Operadores y Auditores.</span>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        with st.container(border=True):
            st.markdown(
                """
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
                '<div class="login-footer-note">🛡️ Autenticación verificada contra la base de datos MySQL (tabla <code>usuarios</code>).</div>',
                unsafe_allow_html=True,
            )

            if not submitted:
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
                st.error(error or "Las credenciales ingresadas no son válidas.")
                return

            start_user_session(user)
            st.rerun()
