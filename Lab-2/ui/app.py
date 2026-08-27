"""Streamlit UI — the shell: page setup, the connect screen, and navigation.

The screens themselves live in views.py (Manual) and chat.py (AI); the
stylesheet in theme.py; every HTTP call in api_client.py. This file only
decides what the user is looking at.

The UI reaches the database exclusively through the API. The connect screen
takes a Claude API key and a database connection string, hands the latter to
the API over POST /admin/connect, and keeps both only in session state —
this browser session's server-side memory. Neither is written to disk or
logged.

The Manual / AI toggle switches between the form-based screens and the chat.
Both are restricted to the same HTTP endpoints, so the chat can do nothing a
form could not.
"""

from __future__ import annotations

import anthropic
import requests
import streamlit as st

import api_client
import chat
import theme
import views

st.set_page_config(page_title="DB_Operations", page_icon="◆", layout="wide")


NAV_GROUPS = [
    ("Overview", [("overview", "Overview")]),
    ("Add", [
        ("add_customer", "Add customer"),
        ("add_product", "Add product"),
        ("record_sale", "Record sale"),
    ]),
    ("Browse", [
        ("customers", "Customers"),
        ("products", "Products"),
        ("sales", "Sales"),
        ("sales_detail", "Sales detail"),
    ]),
    ("Import", [("csv_load", "CSV load")]),
]



# ---------------------------------------------------------------------
# Login / connect
# ---------------------------------------------------------------------
def try_connect(api_key: str, database_url: str) -> tuple[bool, str]:
    api_key, database_url = api_key.strip(), database_url.strip()
    if not api_key:
        return False, "Enter your Claude API key."
    if not database_url:
        return False, "Enter a database connection string."

    try:
        anthropic.Anthropic(api_key=api_key).models.retrieve("claude-opus-5")
    except anthropic.AuthenticationError:
        return False, "That Claude API key was rejected."
    except anthropic.APIError as exc:
        return False, f"Couldn't verify the Claude API key: {exc}"

    try:
        response = requests.post(
            f"{api_client.API_BASE_URL}/admin/connect", json={"database_url": database_url}, timeout=15
        )
    except requests.RequestException:
        return False, f"Can't reach the API at {api_client.API_BASE_URL}. Is it running?"
    if response.status_code != 200:
        return False, api_client.error_detail(response)
    return True, ""


def render_login() -> None:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown(
            '<div style="text-align:center; margin-top: 3.5rem;">'
            '<div class="brand-mark" style="margin: 0 auto 1rem auto;">◆</div>'
            '<h1 style="margin-bottom:0.2rem;">DB_Operations</h1>'
            '<p style="color: var(--text-muted); margin-bottom: 1.6rem;">'
            "Connect a database and a Claude API key to get started.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            api_key = st.text_input("Claude API key", type="password", placeholder="sk-ant-...")
            database_url = st.text_input(
                "Database connection string", type="password",
                placeholder="postgresql://user:pass@host/db?sslmode=require",
            )
            st.caption(
                "Paste it exactly as your provider gives it — postgres:// and "
                "postgresql:// both work. Held only in this browser session's "
                "server-side memory — never written to disk, logged, or shown again."
            )
            if st.button("Connect", type="primary", use_container_width=True):
                with st.spinner("Connecting…"):
                    ok, message = try_connect(api_key, database_url)
                if ok:
                    st.session_state.connected = True
                    st.session_state.claude_api_key = api_key.strip()
                    st.rerun()
                else:
                    st.error(message)


# ---------------------------------------------------------------------
# Mode toggle + sidebar
# ---------------------------------------------------------------------
def render_mode_toggle() -> None:
    # Wide enough that "Manual" stays on one line — a narrow column wraps it
    # to one letter per row.
    _, manual_col, ai_col = st.columns([6, 1.5, 1])
    with manual_col:
        if st.button(
            "Manual", key="mode_manual", use_container_width=True,
            type="primary" if st.session_state.mode == "manual" else "secondary",
        ):
            st.session_state.mode = "manual"
            st.rerun()
    with ai_col:
        if st.button(
            "AI", key="mode_ai", use_container_width=True,
            type="primary" if st.session_state.mode == "ai" else "secondary",
        ):
            st.session_state.mode = "ai"
            st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="brand-wrap">'
            '<div class="brand-mark">◆</div>'
            '<p class="brand-title">DB_Operations</p>'
            '<p class="brand-subtitle">Customer · Product · Sales</p>'
            "</div>",
            unsafe_allow_html=True,
        )
        if st.session_state.mode == "manual":
            for group_label, items in NAV_GROUPS:
                st.markdown(f'<div class="nav-caption">{group_label}</div>', unsafe_allow_html=True)
                for key, label in items:
                    is_active = st.session_state.active_view == key
                    if st.button(
                        label, key=f"nav_{key}",
                        type="primary" if is_active else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state.active_view = key
                        st.rerun()
        else:
            chat.ensure_state()
            if st.button("＋  New chat", key="new_chat", use_container_width=True, type="secondary"):
                chat.start_new_conversation()
                st.rerun()

            st.markdown('<div class="nav-caption">Recent</div>', unsafe_allow_html=True)
            active_id = st.session_state.active_conversation_id
            for conversation in st.session_state.conversations:
                is_active = conversation["id"] == active_id
                if st.button(
                    conversation["title"], key=f"conv_{conversation['id']}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.active_conversation_id = conversation["id"]
                    st.rerun()

        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="nav-caption">Session</div>', unsafe_allow_html=True)
        if st.button("Disconnect", key="disconnect", use_container_width=True, type="secondary"):
            for k in ("connected", "claude_api_key", "conversations", "active_conversation_id"):
                st.session_state.pop(k, None)
            st.rerun()


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
def main() -> None:
    theme.inject()

    if "active_view" not in st.session_state:
        st.session_state.active_view = "overview"
    if "mode" not in st.session_state:
        st.session_state.mode = "manual"

    if not st.session_state.get("connected"):
        render_login()
        return

    render_sidebar()
    render_mode_toggle()

    if st.session_state.mode == "ai":
        chat.render(st.session_state.claude_api_key)
    else:
        views.VIEWS[st.session_state.active_view]()


if __name__ == "__main__":
    main()
