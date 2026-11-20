"""Gestión segura de la identidad autenticada en la sesión de Streamlit."""

from datetime import datetime, timedelta

import streamlit as st

from src.core.authorization import ETIQUETAS_ROL, normalizar_rol
from src.core.config import configuracion
from src.models.entities import Usuario

CLAVE_USUARIO = "authenticated_user"
CLAVE_ACTIVIDAD = "authenticated_user_last_activity"


def iniciar_sesion_usuario(usuario: Usuario) -> None:
    """Guarda únicamente los datos públicos del usuario, nunca el hash."""
    st.session_state[CLAVE_USUARIO] = {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "usuario": usuario.usuario,
        "role": normalizar_rol(usuario.rol),
        "role_label": ETIQUETAS_ROL[normalizar_rol(usuario.rol)],
    }
    st.session_state[CLAVE_ACTIVIDAD] = datetime.now()


def obtener_usuario_actual() -> dict | None:
    """Devuelve el usuario autenticado y aplica el vencimiento por inactividad."""
    usuario = st.session_state.get(CLAVE_USUARIO)
    if not usuario:
        return None

    ultima_actividad = st.session_state.get(CLAVE_ACTIVIDAD)
    tiempo_limite = max(1, configuracion.minutos_expiracion_sesion)
    if not isinstance(ultima_actividad, datetime) or datetime.now() - ultima_actividad > timedelta(minutes=tiempo_limite):
        cerrar_sesion_usuario(vencido=True)
        return None

    st.session_state[CLAVE_ACTIVIDAD] = datetime.now()
    return usuario


def cerrar_sesion_usuario(*, vencido: bool = False) -> None:
    st.session_state.pop(CLAVE_USUARIO, None)
    st.session_state.pop(CLAVE_ACTIVIDAD, None)
    if vencido:
        st.session_state["_session_expired"] = True
