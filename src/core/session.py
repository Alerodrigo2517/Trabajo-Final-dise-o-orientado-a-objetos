"""Gestión segura de la identidad autenticada en la sesión de Streamlit."""

from datetime import datetime, timedelta

import streamlit as st

from src.core.authorization import ETIQUETAS_ROL, normalize_role
from src.core.config import configuracion
from src.models.entities import Usuario

CLAVE_USUARIO = "authenticated_user"
CLAVE_ACTIVIDAD = "authenticated_user_last_activity"


def start_user_session(usuario: Usuario) -> None:
    """Guarda únicamente los datos públicos del usuario, nunca el hash."""
    st.session_state[CLAVE_USUARIO] = {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "usuario": usuario.usuario,
        "role": normalize_role(usuario.rol),
        "role_label": ETIQUETAS_ROL[normalize_role(usuario.rol)],
    }
    st.session_state[CLAVE_ACTIVIDAD] = datetime.now()


def current_user() -> dict | None:
    """Devuelve el usuario autenticado y aplica el vencimiento por inactividad."""
    usuario = st.session_state.get(CLAVE_USUARIO)
    if not usuario:
        return None

    ultima_actividad = st.session_state.get(CLAVE_ACTIVIDAD)
    tiempo_limite = max(1, configuracion.minutos_expiracion_sesion)
    if not isinstance(ultima_actividad, datetime) or datetime.now() - ultima_actividad > timedelta(minutes=tiempo_limite):
        logout_user(vencido=True)
        return None

    st.session_state[CLAVE_ACTIVIDAD] = datetime.now()
    return usuario


def logout_user(*, vencido: bool = False) -> None:
    st.session_state.pop(CLAVE_USUARIO, None)
    st.session_state.pop(CLAVE_ACTIVIDAD, None)
    if vencido:
        st.session_state["_session_expired"] = True
