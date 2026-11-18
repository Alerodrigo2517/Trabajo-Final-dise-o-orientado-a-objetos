"""Presentación común y controles reutilizables de Streamlit."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --forge-ink:#202923; --forge-muted:#68736b; --forge-orange:#c56532; --forge-orange-dark:#94461f; --forge-paper:#f4f3ef; --forge-line:#deded8; }
        [data-testid="stAppViewContainer"] { background:var(--forge-paper); }
        [data-testid="stHeader"] { background:transparent; }
        .main .block-container { max-width:1340px; padding:2rem 2.3rem 3rem; }
        [data-testid="stSidebar"] { background:#202923; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"], [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#edf0eb; }
        [data-testid="stSidebarNav"] a { border-radius:9px; margin:2px 0; }
        [data-testid="stSidebarNav"] a[aria-current="page"] { background:#34443a; }
        h1,h2,h3 { color:var(--forge-ink); letter-spacing:-.02em; }
        .page-heading { margin:.25rem 0 1.5rem; }
        .page-heading .eyebrow { margin:0 0 .35rem; color:var(--forge-orange-dark); font-size:.72rem; font-weight:750; letter-spacing:.13em; text-transform:uppercase; }
        .page-heading h1 { margin:0; font-size:clamp(2rem,3vw,2.65rem); line-height:1.1; }
        .page-heading p:last-child { max-width:800px; margin:.55rem 0 0; color:var(--forge-muted); }
        .panel-heading { margin:0 0 .25rem; font-size:.78rem; font-weight:750; letter-spacing:.12em; color:#46534a; }
        .hero-panel { padding:1.7rem 1.9rem; margin:0 0 1.25rem; border:1px solid #d8d8d1; border-radius:16px; background:linear-gradient(120deg,#fff,#ebece8); }
        [data-testid="stMetric"] { min-height:105px; padding:1rem 1.1rem; border:1px solid var(--forge-line); border-radius:13px; background:#fff; }
        [data-testid="stMetricLabel"] { color:var(--forge-muted); }
        [data-testid="stForm"] { padding:1rem; border:1px solid var(--forge-line); border-radius:12px; background:#fff; }
        .stButton>button,[data-testid="stFormSubmitButton"]>button { min-height:2.65rem; border-radius:8px; font-weight:650; }
        .stButton>button[kind="primary"],[data-testid="stFormSubmitButton"]>button[kind="primary"] { border-color:var(--forge-orange-dark); background:var(--forge-orange); }
        [data-testid="stDataFrame"] { overflow:hidden; border:1px solid var(--forge-line); border-radius:10px; background:white; }
        .empty-state { padding:1.2rem; border:1px dashed #c9cbc3; border-radius:12px; background:#fbfbf9; }
        .empty-state strong { color:var(--forge-ink); }
        .empty-state p { margin:.3rem 0 0; color:var(--forge-muted); }
        .row-caption { color:var(--forge-muted); font-size:.85rem; }
        @media(max-width:760px) { .main .block-container { padding:1.25rem .9rem 2rem; } .hero-panel { padding:1.3rem; } }
        @media(prefers-reduced-motion:reduce) { *,*::before,*::after { scroll-behavior:auto!important; transition:none!important; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, description: str) -> None:
    st.markdown(
        f'<div class="page-heading"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{description}</p></div>',
        unsafe_allow_html=True,
    )


def database_error() -> None:
    if st.session_state.get("_database_error_shown", False):
        return
    st.session_state["_database_error_shown"] = True
    st.error(
        "No se pudo consultar la base de datos. Verificá que MySQL esté encendido, que exista "
        "el esquema presupuesto_herreria_poo y que las variables de conexión de .env sean correctas."
    )


def handle_database_error(error: Exception) -> None:
    if isinstance(error, SQLAlchemyError):
        database_error()
    elif isinstance(error, ValueError):
        st.error(str(error))
    else:
        database_error()


def empty_state(title: str, description: str) -> None:
    st.markdown(
        f'<div class="empty-state"><strong>{title}</strong><p>{description}</p></div>',
        unsafe_allow_html=True,
    )


def currency(value) -> str:
    amount = f"{float(value or 0):,.2f}"
    return "$ " + amount.replace(",", "_").replace(".", ",").replace("_", ".")


def records_table(records: list[dict], key: str, empty_title: str, empty_description: str) -> None:
    if not records:
        empty_state(empty_title, empty_description)
        return
    frame = pd.DataFrame(records)
    query = st.text_input("Buscar", key=f"buscar_{key}", placeholder="Filtrar registros por nombre, estado o dato…")
    if query.strip():
        matches = frame.astype(str).apply(
            lambda column: column.str.contains(query.strip(), case=False, na=False, regex=False)
        )
        frame = frame[matches.any(axis=1)]
    if frame.empty:
        empty_state("Sin coincidencias", "Probá con otro término de búsqueda.")
        return
    st.dataframe(frame, hide_index=True, width="stretch")


def _append_client_row() -> None:
    row_id = int(st.session_state.get("client_row_sequence", 0))
    st.session_state.client_draft_rows.append({"id": row_id, "saved": False})
    st.session_state.client_row_sequence = row_id + 1


def _client_field_changed(row_id: int) -> None:
    rows = st.session_state.client_draft_rows
    row = next((item for item in rows if item["id"] == row_id), None)
    if row is None or row["saved"]:
        return

    values = {
        field: str(st.session_state.get(f"client_{row_id}_{field}", "")).strip()
        for field in ("nombre", "apellido", "cuit")
    }
    has_content = any(values.values())
    if has_content and rows[-1]["id"] == row_id:
        _append_client_row()

    if not all(values.values()):
        return

    try:
        from src.services.client_service import create_client

        create_client(values["cuit"], values["nombre"], values["apellido"])
    except ValueError as error:
        st.session_state.client_feedback = ("error", str(error))
    except SQLAlchemyError:
        st.session_state.client_feedback = (
            "error",
            "No se pudo guardar el cliente en la base de datos. Revisá la conexión e intentá de nuevo.",
        )
    else:
        row["saved"] = True
        st.session_state.client_feedback = ("success", "Cliente guardado en la base de datos.")
        if rows[-1]["id"] == row_id:
            _append_client_row()


def client_entry_rows() -> None:
    if "client_draft_rows" not in st.session_state:
        st.session_state.client_draft_rows = []
        st.session_state.client_row_sequence = 0
        _append_client_row()

    st.caption("Completá nombre, apellido y CUIT. Al empezar una fila nueva, aparece otra debajo; cada fila completa se guarda en clientes.")
    if "client_feedback" in st.session_state:
        kind, message = st.session_state.pop("client_feedback")
        getattr(st, kind)(message)

    heading = st.columns([1, 1, 1, .08])
    for column, label in zip(heading[:3], ("NOMBRE", "APELLIDO", "CUIT")):
        column.markdown(f'<p class="panel-heading">{label}</p>', unsafe_allow_html=True)
    heading[3].markdown(" ")

    for position, row in enumerate(st.session_state.client_draft_rows):
        row_id = row["id"]
        columns = st.columns([1, 1, 1, .08])
        for column, field, placeholder in zip(
            columns[:3],
            ("nombre", "apellido", "cuit"),
            ("Nombre", "Apellido", "20-12345678-9"),
        ):
            column.text_input(
                f"{field.title()} {position + 1}",
                key=f"client_{row_id}_{field}",
                placeholder=placeholder,
                label_visibility="collapsed",
                disabled=row["saved"],
                on_change=_client_field_changed,
                args=(row_id,),
            )
        if row["saved"]:
            columns[3].markdown("✓")
        elif position == len(st.session_state.client_draft_rows) - 1:
            columns[3].markdown("＋")
