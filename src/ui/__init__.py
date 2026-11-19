"""Presentación común, sistema de diseño visual y controles reutilizables de Streamlit."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

        :root {
          --bg-app: #f8fafc;
          --bg-subtle: #f1f5f9;
          --surface: #ffffff;
          --surface-elevated: #ffffff;
          --ink: #0f172a;
          --ink-secondary: #334155;
          --muted: #64748b;
          --line: #e2e8f0;
          --line-strong: #cbd5e1;
          --accent: #d97706;
          --accent-hover: #b45309;
          --accent-soft: #fef3c7;
          --accent-border: #fde68a;
          --primary-blue: #2563eb;
          --primary-blue-soft: #eff6ff;
          --emerald: #059669;
          --emerald-soft: #ecfdf5;
          --rose: #e11d48;
          --rose-soft: #fff1f2;
          --sidebar-bg: #0f172a;
          --sidebar-surface: #1e293b;
          --sidebar-active: linear-gradient(135deg, #d97706 0%, #b45309 100%);
          --radius-sm: 8px;
          --radius-md: 12px;
          --radius-lg: 16px;
          --radius-xl: 20px;
          --shadow-sm: 0 1px 2px 0 rgba(15, 23, 42, 0.04);
          --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.05), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
          --shadow-lg: 0 12px 24px -4px rgba(15, 23, 42, 0.07), 0 4px 8px -4px rgba(15, 23, 42, 0.04);
        }

        html, body, [class*="st-"], [data-testid="stAppViewContainer"] {
          font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
          color: var(--ink);
        }

        [data-testid="stAppViewContainer"] {
          background: radial-gradient(circle at 100% 0%, #fffbeb 0%, #f8fafc 38%, #f1f5f9 100%);
        }

        [data-testid="stHeader"] {
          background: rgba(248, 250, 252, 0.82);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(226, 232, 240, 0.6);
        }

        .main .block-container {
          max-width: 1440px;
          padding: 1.75rem 2.5rem 3.5rem;
        }

        /* ================= SIDEBAR ================= */
        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, #0f172a 0%, #131c31 100%);
          border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
          color: #cbd5e1;
        }

        .brand-lockup {
          display: flex;
          align-items: center;
          gap: 0.85rem;
          padding: 0.5rem 0.35rem 0.65rem;
        }

        .brand-mark {
          display: grid;
          width: 2.75rem;
          height: 2.75rem;
          place-items: center;
          border: 1px solid rgba(251, 191, 36, 0.35);
          border-radius: 12px;
          background: linear-gradient(135deg, rgba(217, 119, 6, 0.28) 0%, rgba(180, 83, 9, 0.14) 100%);
          box-shadow: 0 4px 12px rgba(217, 119, 6, 0.18);
          font-size: 1.35rem;
        }

        .brand-copy {
          display: flex;
          flex-direction: column;
          gap: 0.15rem;
        }

        .brand-copy strong {
          color: #ffffff;
          font-size: 1.12rem;
          font-weight: 800;
          letter-spacing: -0.025em;
        }

        .brand-copy small {
          color: #fbbf24;
          font-size: 0.62rem;
          font-weight: 700;
          letter-spacing: 0.14em;
          text-transform: uppercase;
        }

        .sidebar-user-card {
          margin: 0.35rem 0 0.75rem;
          padding: 0.85rem 0.95rem;
          border-radius: 12px;
          background: rgba(30, 41, 59, 0.85);
          border: 1px solid rgba(255, 255, 255, 0.08);
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .sidebar-user-avatar {
          width: 2.35rem;
          height: 2.35rem;
          border-radius: 10px;
          background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
          color: #ffffff;
          font-weight: 800;
          font-size: 0.95rem;
          display: grid;
          place-items: center;
          flex-shrink: 0;
          box-shadow: 0 2px 8px rgba(217, 119, 6, 0.3);
        }

        .sidebar-user-info {
          display: flex;
          flex-direction: column;
          min-width: 0;
        }

        .sidebar-user-name {
          color: #f8fafc;
          font-weight: 600;
          font-size: 0.88rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .sidebar-user-role {
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
          color: #94a3b8;
          font-size: 0.72rem;
          font-weight: 500;
          margin-top: 0.1rem;
        }

        .sidebar-role-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #10b981;
          box-shadow: 0 0 6px #10b981;
        }

        [data-testid="stSidebar"] hr {
          border-color: rgba(255, 255, 255, 0.08);
          margin: 0.75rem 0;
        }

        [data-testid="stSidebarNav"] {
          padding-top: 0.25rem;
        }

        [data-testid="stSidebarNav"] a {
          min-height: 42px;
          border-radius: 10px;
          margin: 4px 10px;
          padding: 0.45rem 0.75rem;
          color: #94a3b8 !important;
          font-weight: 500;
          transition: all 0.18s ease;
        }

        [data-testid="stSidebarNav"] a:hover {
          background: rgba(255, 255, 255, 0.06);
          color: #f8fafc !important;
          transform: translateX(2px);
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
          background: linear-gradient(135deg, rgba(217, 119, 6, 0.22) 0%, rgba(217, 119, 6, 0.1) 100%);
          border: 1px solid rgba(251, 191, 36, 0.3);
          color: #ffffff !important;
          font-weight: 650;
          box-shadow: 0 4px 12px rgba(15, 23, 42, 0.25);
        }

        [data-testid="stSidebar"] .stButton > button {
          border-color: rgba(255, 255, 255, 0.14);
          color: #e2e8f0;
          background: rgba(30, 41, 59, 0.75);
          border-radius: 10px;
          font-size: 0.85rem;
          font-weight: 600;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
          border-color: rgba(248, 113, 113, 0.45);
          background: rgba(225, 29, 72, 0.18);
          color: #fecdd3;
        }

        /* ================= PAGE HEADERS ================= */
        h1, h2, h3 {
          color: var(--ink);
          letter-spacing: -0.03em;
        }

        h2 {
          font-size: 1.28rem;
          font-weight: 700;
          margin-top: 1.5rem;
        }

        h3 {
          font-size: 1.05rem;
          font-weight: 650;
        }

        .page-heading {
          position: relative;
          padding: 1.5rem 1.75rem;
          margin: 0 0 1.5rem;
          border-radius: var(--radius-lg);
          background: linear-gradient(125deg, #ffffff 0%, #f8fafc 65%, #fffbeb 100%);
          border: 1px solid var(--line);
          box-shadow: var(--shadow-md);
          overflow: hidden;
        }

        .page-heading::before {
          content: "";
          position: absolute;
          top: 0;
          left: 0;
          width: 5px;
          height: 100%;
          background: linear-gradient(180deg, #d97706 0%, #f59e0b 100%);
        }

        .page-heading-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 0.35rem;
        }

        .page-heading .eyebrow {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          margin: 0;
          padding: 0.22rem 0.65rem;
          border-radius: 999px;
          background: var(--accent-soft);
          border: 1px solid var(--accent-border);
          color: var(--accent-hover);
          font-size: 0.68rem;
          font-weight: 750;
          letter-spacing: 0.11em;
          text-transform: uppercase;
        }

        .page-heading h1 {
          margin: 0.15rem 0 0;
          font-size: clamp(1.65rem, 2.4vw, 2.15rem);
          font-weight: 800;
          line-height: 1.15;
          color: var(--ink);
        }

        .page-heading p.page-desc {
          max-width: 820px;
          margin: 0.45rem 0 0;
          color: var(--muted);
          font-size: 0.94rem;
          line-height: 1.55;
        }

        /* ================= KPI CARDS ================= */
        .kpi-card {
          padding: 1.15rem 1.25rem;
          border-radius: var(--radius-md);
          background: var(--surface);
          border: 1px solid var(--line);
          box-shadow: var(--shadow-md);
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          min-height: 118px;
          transition: transform 0.16s ease, box-shadow 0.16s ease;
        }

        .kpi-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-lg);
        }

        .kpi-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.5rem;
          margin-bottom: 0.55rem;
        }

        .kpi-label {
          color: var(--muted);
          font-size: 0.78rem;
          font-weight: 600;
          letter-spacing: 0.02em;
          text-transform: uppercase;
        }

        .kpi-icon {
          width: 2.1rem;
          height: 2.1rem;
          border-radius: 9px;
          display: grid;
          place-items: center;
          font-size: 1rem;
          flex-shrink: 0;
        }

        .kpi-tone-amber .kpi-icon { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
        .kpi-tone-blue .kpi-icon { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
        .kpi-tone-emerald .kpi-icon { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
        .kpi-tone-slate .kpi-icon { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }

        .kpi-value {
          color: var(--ink);
          font-size: 1.65rem;
          font-weight: 800;
          letter-spacing: -0.035em;
          line-height: 1.15;
          font-variant-numeric: tabular-nums;
        }

        .kpi-sub {
          margin-top: 0.35rem;
          color: var(--muted);
          font-size: 0.76rem;
          font-weight: 500;
        }

        /* ================= SECTION CARDS & CONTAINERS ================= */
        .section-banner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
          margin: 0 0 0.85rem;
          padding-bottom: 0.65rem;
          border-bottom: 1px solid var(--line);
        }

        .section-banner-left {
          display: flex;
          align-items: center;
          gap: 0.65rem;
        }

        .section-banner-icon {
          width: 2rem;
          height: 2rem;
          border-radius: 8px;
          background: var(--bg-subtle);
          border: 1px solid var(--line);
          display: grid;
          place-items: center;
          font-size: 0.95rem;
        }

        .section-banner-title {
          margin: 0;
          font-size: 1.02rem;
          font-weight: 700;
          color: var(--ink);
        }

        .section-banner-sub {
          margin: 0.1rem 0 0;
          font-size: 0.8rem;
          color: var(--muted);
        }

        .section-badge {
          padding: 0.2rem 0.6rem;
          border-radius: 999px;
          font-size: 0.7rem;
          font-weight: 700;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          background: var(--bg-subtle);
          color: var(--ink-secondary);
          border: 1px solid var(--line);
        }

        .panel-heading {
          margin: 0 0 0.45rem;
          font-size: 0.72rem;
          font-weight: 750;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          color: var(--accent-hover);
        }

        /* Streamlit native bordered containers */
        [data-testid="stVerticalBlockBorderWrapper"] {
          border-radius: var(--radius-lg) !important;
          border: 1px solid var(--line) !important;
          background: var(--surface) !important;
          box-shadow: var(--shadow-md) !important;
          padding: 1.25rem 1.35rem !important;
        }

        [data-testid="stMetric"] {
          min-height: 112px;
          padding: 1.1rem 1.25rem;
          border: 1px solid var(--line);
          border-radius: var(--radius-md);
          background: var(--surface);
          box-shadow: var(--shadow-md);
        }

        [data-testid="stMetricLabel"] {
          color: var(--muted);
          font-size: 0.82rem;
          font-weight: 600;
        }

        [data-testid="stMetricValue"] {
          color: var(--ink);
          font-size: 1.7rem;
          font-weight: 800;
          letter-spacing: -0.035em;
        }

        /* ================= FORMS & INPUTS ================= */
        [data-testid="stForm"] {
          padding: 1.25rem;
          border: 1px solid var(--line);
          border-radius: var(--radius-md);
          background: #fcfcfd;
          box-shadow: var(--shadow-sm);
        }

        [data-testid="stTextInput"] label,
        [data-testid="stTextArea"] label,
        [data-testid="stNumberInput"] label,
        [data-testid="stDateInput"] label,
        [data-testid="stSelectbox"] label,
        [data-testid="stRadio"] label,
        [data-testid="stCheckbox"] label {
          color: var(--ink-secondary);
          font-weight: 600;
          font-size: 0.86rem;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="select"] > div {
          border-color: var(--line-strong);
          border-radius: 9px;
          background: #ffffff;
          transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }

        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {
          border-color: var(--accent);
          box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.16);
        }

        input, textarea {
          color: var(--ink) !important;
        }

        /* ================= BUTTONS ================= */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
          min-height: 2.7rem;
          border-radius: 9px;
          font-weight: 650;
          letter-spacing: -0.01em;
          transition: all 0.15s ease;
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
          transform: translateY(-1px);
          box-shadow: 0 6px 14px rgba(15, 23, 42, 0.1);
        }

        .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] > button[kind="primary"] {
          border: 1px solid #b45309;
          color: #ffffff;
          background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
          box-shadow: 0 2px 6px rgba(217, 119, 6, 0.25);
        }

        .stButton > button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
          border-color: #92400e;
          background: linear-gradient(135deg, #b45309 0%, #92400e 100%);
          box-shadow: 0 6px 16px rgba(180, 83, 9, 0.32);
        }

        /* ================= TABS ================= */
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
          gap: 0.5rem;
          background: var(--bg-subtle);
          padding: 0.35rem;
          border-radius: 12px;
          border: 1px solid var(--line);
        }

        [data-testid="stTabs"] [data-baseweb="tab"] {
          border-radius: 9px;
          padding: 0.5rem 1rem;
          font-weight: 600;
          font-size: 0.88rem;
          color: var(--muted);
          border: none !important;
        }

        [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
          background: var(--surface);
          color: var(--ink);
          box-shadow: var(--shadow-sm);
        }

        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
          display: none;
        }

        /* ================= TABLES & DATAFRAMES ================= */
        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"] {
          overflow: hidden;
          border: 1px solid var(--line);
          border-radius: 12px;
          background: #ffffff;
          box-shadow: var(--shadow-sm);
        }

        [data-testid="stAlert"] {
          border-radius: 11px;
          border: 1px solid var(--line);
        }

        [data-testid="stExpander"] {
          border: 1px solid var(--line);
          border-radius: 12px;
          background: var(--surface);
          box-shadow: var(--shadow-sm);
        }

        .empty-state {
          padding: 2rem 1.5rem;
          border: 1.5px dashed var(--line-strong);
          border-radius: 14px;
          background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
          text-align: center;
        }

        .empty-state-icon {
          font-size: 1.75rem;
          margin-bottom: 0.45rem;
        }

        .empty-state strong {
          display: block;
          color: var(--ink);
          font-size: 0.98rem;
          font-weight: 700;
        }

        .empty-state p {
          margin: 0.3rem auto 0;
          max-width: 440px;
          color: var(--muted);
          font-size: 0.86rem;
          line-height: 1.5;
        }

        .table-toolbar-meta {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          padding: 0.25rem 0.7rem;
          border-radius: 999px;
          background: var(--bg-subtle);
          border: 1px solid var(--line);
          color: var(--ink-secondary);
          font-size: 0.76rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
        }

        .row-status-pill {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 2rem;
          height: 2.35rem;
          border-radius: 8px;
          font-weight: 700;
          font-size: 0.85rem;
        }

        .row-status-saved {
          background: var(--emerald-soft);
          color: var(--emerald);
          border: 1px solid #a7f3d0;
        }

        .row-status-new {
          background: var(--accent-soft);
          color: var(--accent-hover);
          border: 1px solid var(--accent-border);
        }

        @media (max-width: 900px) {
          .main .block-container { padding: 1.25rem 1.25rem 2.5rem; }
        }

        @media (max-width: 600px) {
          .main .block-container { padding: 1rem 0.8rem 2rem; }
          .page-heading { padding: 1.15rem 1.2rem; }
          [data-testid="stForm"] { padding: 0.9rem; }
        }

        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            scroll-behavior: auto !important;
            transition: none !important;
            transform: none !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, description: str, badge: str | None = None) -> None:
    badge_html = f'<span class="section-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="page-heading">
          <div class="page-heading-top">
            <p class="eyebrow">⚡ {eyebrow}</p>
            {badge_html}
          </div>
          <h1>{title}</h1>
          <p class="page-desc">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(
    label: str,
    value: str | int,
    subtitle: str = "",
    icon: str = "📊",
    tone: str = "amber",
) -> None:
    sub_html = f'<div class="kpi-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="kpi-card kpi-tone-{tone}">
          <div class="kpi-top">
            <span class="kpi-label">{label}</span>
            <span class="kpi-icon">{icon}</span>
          </div>
          <div>
            <div class="kpi-value">{value}</div>
            {sub_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "", icon: str = "🗂️", badge: str = "") -> None:
    sub_html = f'<p class="section-banner-sub">{subtitle}</p>' if subtitle else ""
    badge_html = f'<span class="section-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="section-banner">
          <div class="section-banner-left">
            <div class="section-banner-icon">{icon}</div>
            <div>
              <h3 class="section-banner-title">{title}</h3>
              {sub_html}
            </div>
          </div>
          {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_user(user: dict) -> None:
    name = str(user.get("nombre") or user.get("usuario") or "Usuario").strip()
    parts = [p[0].upper() for p in name.split() if p][:2]
    initials = "".join(parts) or "U"
    role_label = user.get("role_label", "Operador")
    st.sidebar.markdown(
        f"""
        <div class="sidebar-user-card">
          <div class="sidebar-user-avatar">{initials}</div>
          <div class="sidebar-user-info">
            <span class="sidebar-user-name">{name}</span>
            <span class="sidebar-user-role">
              <span class="sidebar-role-dot"></span>
              {role_label}
            </span>
          </div>
        </div>
        """,
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


def empty_state(title: str, description: str, icon: str = "📭") -> None:
    st.markdown(
        f"""
        <div class="empty-state">
          <div class="empty-state-icon">{icon}</div>
          <strong>{title}</strong>
          <p>{description}</p>
        </div>
        """,
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
    search_col, count_col = st.columns([3, 1])
    with search_col:
        query = st.text_input(
            "Buscar",
            key=f"buscar_{key}",
            placeholder="🔍 Filtrar por nombre, código, estado, cliente o monto…",
            label_visibility="collapsed",
        )
    if query.strip():
        matches = frame.astype(str).apply(
            lambda column: column.str.contains(query.strip(), case=False, na=False, regex=False)
        )
        frame = frame[matches.any(axis=1)]
    with count_col:
        total_str = f"{len(frame):,}".replace(",", ".")
        st.markdown(
            f'<div style="text-align:right; padding-top:0.35rem;"><span class="table-toolbar-meta">📋 {total_str} registros</span></div>',
            unsafe_allow_html=True,
        )
    if frame.empty:
        empty_state("Sin coincidencias para tu búsqueda", "Probá con otro término o limpiá el filtro para ver todos los registros.", icon="🔎")
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
        st.session_state.client_feedback = ("success", "Cliente guardado automáticamente en la base de datos.")
        if rows[-1]["id"] == row_id:
            _append_client_row()


def client_entry_rows() -> None:
    from src.core.authorization import can_write
    from src.core.session import current_user

    if not can_write(current_user()):
        st.info("Tu perfil puede consultar clientes, pero no registrar ni modificar datos.")
        return
    if "client_draft_rows" not in st.session_state:
        st.session_state.client_draft_rows = []
        st.session_state.client_row_sequence = 0
        _append_client_row()

    st.caption(
        "Completá Nombre, Apellido y CUIT en una fila. Al completar los 3 campos se guarda automáticamente en MySQL y se habilita una nueva fila."
    )
    if "client_feedback" in st.session_state:
        kind, message = st.session_state.pop("client_feedback")
        getattr(st, kind)(message)

    heading = st.columns([1, 1, 1, 0.14])
    for column, label in zip(heading[:3], ("NOMBRE", "APELLIDO", "CUIT / CUIL")):
        column.markdown(f'<p class="panel-heading">{label}</p>', unsafe_allow_html=True)
    heading[3].markdown('<p class="panel-heading" style="text-align:center;">ESTADO</p>', unsafe_allow_html=True)

    for position, row in enumerate(st.session_state.client_draft_rows):
        row_id = row["id"]
        columns = st.columns([1, 1, 1, 0.14])
        for column, field, placeholder in zip(
            columns[:3],
            ("nombre", "apellido", "cuit"),
            ("Ej. Martín", "Ej. Rodríguez", "20-12345678-9"),
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
            columns[3].markdown(
                '<div style="display:flex;justify-content:center;"><span class="row-status-pill row-status-saved" title="Guardado">✓</span></div>',
                unsafe_allow_html=True,
            )
        elif position == len(st.session_state.client_draft_rows) - 1:
            columns[3].markdown(
                '<div style="display:flex;justify-content:center;"><span class="row-status-pill row-status-new" title="Fila activa">＋</span></div>',
                unsafe_allow_html=True,
            )
