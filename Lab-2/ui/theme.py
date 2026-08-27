"""The application's stylesheet, kept in one place.

Streamlit ships a default look that is instantly recognisable as a default.
This overrides it wholesale: warm paper, one terracotta accent used
sparingly, a serif for headings against a clean sans for everything else.

Colour is applied by CSS variable so a change lands everywhere at once, and
tables are styled as real HTML rather than the framework's canvas grid,
which cannot be styled at all.
"""

from __future__ import annotations

import streamlit as st


def inject() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Public+Sans:wght@400;500;600;700&display=swap');

        :root {
            --bg: #FAF9F5;
            --bg-sidebar: #F3F1E9;
            --surface: #FFFFFF;
            --border: #E8E5D8;
            --text: #211F1B;
            --text-muted: #7C7A70;
            --accent: #D97757;
            --accent-hover: #C2684A;
            --accent-soft: #F4E1D6;
            --danger: #AE4A32;
            --danger-soft: #F7E4DE;
            --success: #5E7A52;
            --success-soft: #E7EEDF;
            --radius-lg: 16px;
            --radius-md: 10px;
            --radius-sm: 8px;
            --mono: ui-monospace, 'SF Mono', 'Cascadia Code', Consolas, monospace;
        }

        html, body, [data-testid="stApp"] {
            background: var(--bg) !important;
            color: var(--text) !important;
        }
        [data-testid="stApp"] * { font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, sans-serif; }
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }
        [data-testid="stMainBlockContainer"] { padding-top: 2.75rem; max-width: 1000px; }
        [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] { gap: 0.9rem; }

        h1, h2, h3, h4, .brand-title {
            font-family: 'Fraunces', Georgia, serif !important;
            font-weight: 500 !important;
            letter-spacing: -0.015em;
            color: var(--text) !important;
        }
        p, span, label, div { letter-spacing: -0.005em; }

        /* ================= sidebar ================= */
        [data-testid="stSidebar"] { background: var(--bg-sidebar) !important; border-right: 1px solid var(--border); }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; }
        [data-testid="stSidebarUserContent"] { padding-top: 1.6rem; padding-left: 0.6rem; padding-right: 0.6rem; }

        .brand-wrap { padding: 0 0.35rem 1.2rem 0.35rem; border-bottom: 1px solid var(--border); margin-bottom: 0.5rem; }
        .brand-mark {
            display: inline-flex; align-items: center; justify-content: center;
            width: 32px; height: 32px; border-radius: 9px; background: var(--accent);
            color: #fff; font-size: 16px; font-weight: 700; margin-bottom: 0.55rem;
        }
        .brand-title { font-size: 1.2rem; margin: 0; line-height: 1.2; }
        .brand-subtitle { color: var(--text-muted); font-size: 0.8rem; margin-top: 0.1rem; }

        .nav-caption {
            font-size: 0.66rem; font-weight: 600; letter-spacing: 0.08em;
            color: var(--text-muted); text-transform: uppercase;
            margin: 1rem 0 0.15rem 0.4rem;
        }

        [data-testid="stSidebar"] [data-testid="stButton"] { margin: 1px 0; }
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            width: 100%; text-align: left; justify-content: flex-start;
            border: none !important; box-shadow: none !important;
            font-weight: 450 !important; font-size: 0.89rem !important;
            padding: 0.38rem 0.6rem !important; min-height: 0 !important; height: auto !important;
            border-radius: var(--radius-sm) !important; line-height: 1.4 !important;
        }
        [data-testid="stSidebar"] button[kind="secondary"] { background: transparent !important; color: var(--text) !important; opacity: 0.68; }
        [data-testid="stSidebar"] button[kind="secondary"]:hover { background: rgba(33,31,27,0.055) !important; opacity: 1; }
        [data-testid="stSidebar"] button[kind="primary"] { background: var(--accent-soft) !important; color: var(--accent-hover) !important; font-weight: 600 !important; }
        [data-testid="stSidebar"] button[kind="primary"]:hover { background: var(--accent-soft) !important; }

        /* ================= buttons, main area ================= */
        button[kind="primary"], [data-testid="stFormSubmitButton"] button {
            background: var(--accent) !important; border: 1px solid var(--accent) !important;
            color: #fff !important; border-radius: var(--radius-sm) !important; font-weight: 600 !important;
            box-shadow: none !important; padding: 0.4rem 1.1rem !important;
        }
        button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button:hover {
            background: var(--accent-hover) !important; border-color: var(--accent-hover) !important;
        }
        button[kind="primary"]:disabled { background: var(--border) !important; border-color: var(--border) !important; color: var(--text-muted) !important; }
        [data-testid="stMainBlockContainer"] button[kind="secondary"] {
            border-radius: var(--radius-sm) !important; border: 1px solid var(--border) !important;
            background: var(--surface) !important; color: var(--text-muted) !important; font-weight: 500 !important;
            box-shadow: none !important; font-size: 0.85rem !important; padding: 0.25rem 0.8rem !important;
        }
        [data-testid="stMainBlockContainer"] button[kind="secondary"]:hover { border-color: var(--accent) !important; color: var(--accent-hover) !important; }
        /* Mode toggle: never wrap the label, however narrow the column gets. */
        [data-testid="stMainBlockContainer"] button p { white-space: nowrap !important; }

        /* ================= cards (bordered containers) ================= */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid var(--border) !important; border-radius: var(--radius-lg) !important;
            background: var(--surface) !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] { gap: 0.75rem; }

        .stat-label { font-size: 0.76rem; color: var(--text-muted); font-weight: 500; margin-bottom: 0.2rem; }
        .stat-value { font-family: 'Fraunces', Georgia, serif; font-size: 1.7rem; font-weight: 500; color: var(--text); line-height: 1.1; }

        .section-eyebrow { color: var(--accent-hover); font-weight: 600; font-size: 0.74rem; letter-spacing: 0.07em; text-transform: uppercase; }
        h3.section-title { margin: 0.1rem 0 0.25rem 0 !important; font-size: 1.55rem !important; }
        .section-help { color: var(--text-muted); font-size: 0.89rem; margin: 0 0 0.15rem 0; line-height: 1.45; }

        /* ================= inputs ================= */
        [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, textarea {
            border-radius: var(--radius-sm) !important; border: 1px solid var(--border) !important;
            background: var(--surface) !important; color: var(--text) !important;
        }
        [data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus {
            border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(217,119,87,0.14) !important;
        }
        [data-testid="stWidgetLabel"] p { font-weight: 500 !important; font-size: 0.85rem !important; color: var(--text-muted) !important; }
        [data-testid="stForm"] { border: none !important; padding: 0 !important; }
        [data-testid="stForm"] [data-testid="stVerticalBlock"] { gap: 0.9rem; }

        /* ================= custom table ================= */
        .claude-table-wrap { border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden auto; max-height: 460px; }
        table.claude-table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
        .claude-table thead th {
            position: sticky; top: 0; z-index: 1;
            text-align: left; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.06em;
            text-transform: uppercase; color: var(--text-muted); background: var(--bg-sidebar);
            padding: 0.6rem 0.85rem; border-bottom: 1px solid var(--border); white-space: nowrap;
        }
        .claude-table thead th.num { text-align: right; }
        .claude-table tbody td {
            padding: 0.55rem 0.85rem; border-bottom: 1px solid var(--border);
            color: var(--text); white-space: nowrap;
        }
        .claude-table tbody tr:last-child td { border-bottom: none; }
        .claude-table tbody tr:hover td { background: rgba(217,119,87,0.05); }
        .claude-table td.num { text-align: right; font-variant-numeric: tabular-nums; }
        .claude-table td.mono { font-family: var(--mono); font-size: 0.81rem; color: var(--text-muted); }
        .table-caption { color: var(--text-muted); font-size: 0.8rem; margin-top: 0.5rem; }

        .empty-state {
            text-align: center; padding: 2.2rem 0; color: var(--text-muted);
            border: 1px dashed var(--border); border-radius: var(--radius-md); font-size: 0.92rem;
        }

        /* ================= alerts ================= */
        [data-testid="stAlertContainer"] { border-radius: var(--radius-md) !important; border: none !important; }

        /* ================= file uploader ================= */
        [data-testid="stFileUploaderDropzone"] {
            border-radius: var(--radius-md) !important; border: 1.5px dashed var(--border) !important;
            background: var(--bg) !important;
        }

        [data-testid="stCaptionContainer"] p { color: var(--text-muted) !important; }
        hr { border-color: var(--border) !important; margin: 0.5rem 0 !important; }

        /* ================= chat ================= */
        [data-testid="stChatMessage"] {
            background: var(--surface) !important; border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important; padding: 0.85rem 1rem !important;
        }
        [data-testid="stChatInput"] textarea, [data-testid="stChatInput"] {
            border-radius: var(--radius-lg) !important; border: 1px solid var(--border) !important;
            background: var(--surface) !important;
        }
        [data-testid="stChatInputSubmitButton"] {
            background: var(--accent) !important; border-radius: 8px !important;
        }
        [data-testid="stChatMessage"] [data-testid="stCaptionContainer"] p {
            color: var(--accent-hover) !important; font-weight: 500 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
