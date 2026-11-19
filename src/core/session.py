"""Gestión segura de la identidad autenticada en la sesión de Streamlit."""

from datetime import datetime, timedelta

import streamlit as st

from src.core.authorization import ROLE_LABELS, normalize_role
from src.core.config import settings
from src.models.entities import Usuario

_USER_KEY = "authenticated_user"
_ACTIVITY_KEY = "authenticated_user_last_activity"


def start_user_session(user: Usuario) -> None:
    """Guarda únicamente los datos públicos del usuario, nunca el hash."""
    st.session_state[_USER_KEY] = {
        "id_usuario": user.id_usuario,
        "nombre": user.nombre,
        "usuario": user.usuario,
        "role": normalize_role(user.rol),
        "role_label": ROLE_LABELS[normalize_role(user.rol)],
    }
    st.session_state[_ACTIVITY_KEY] = datetime.now()


def current_user() -> dict | None:
    """Devuelve el usuario autenticado y aplica el vencimiento por inactividad."""
    user = st.session_state.get(_USER_KEY)
    if not user:
        return None

    last_activity = st.session_state.get(_ACTIVITY_KEY)
    timeout = max(1, settings.session_timeout_minutes)
    if not isinstance(last_activity, datetime) or datetime.now() - last_activity > timedelta(minutes=timeout):
        logout_user(expired=True)
        return None

    st.session_state[_ACTIVITY_KEY] = datetime.now()
    return user


def logout_user(*, expired: bool = False) -> None:
    st.session_state.pop(_USER_KEY, None)
    st.session_state.pop(_ACTIVITY_KEY, None)
    if expired:
        st.session_state["_session_expired"] = True
