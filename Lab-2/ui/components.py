"""Reusable render pieces shared by the Manual views and the AI chat.

render_table() exists because Streamlit's built-in dataframe draws to a
canvas that cannot be styled — no control over padding, alignment or type
treatment. Emitting real HTML instead is what lets identifiers sit in
monospace and money sit right-aligned in tabular figures.
"""

from __future__ import annotations

import html

import streamlit as st

NUMERIC_COLUMNS = {"quantity", "unit_price", "line_total"}
MONO_COLUMNS = {"sku", "product_sku", "email", "customer_email", "sold_at", "customer_id", "product_id", "sale_id"}


def humanize(column: str) -> str:
    return column.replace("_", " ")


def render_table(rows: list[dict], empty_message: str) -> None:
    if not rows:
        st.markdown(f'<div class="empty-state">{html.escape(empty_message)}</div>', unsafe_allow_html=True)
        return

    columns = list(rows[0].keys())
    head_cells = "".join(
        f'<th class="{"num" if c in NUMERIC_COLUMNS else ""}">{html.escape(humanize(c))}</th>' for c in columns
    )
    body_rows = []
    for row in rows:
        cells = []
        for c in columns:
            classes = " ".join(
                cls for cls, cond in (("num", c in NUMERIC_COLUMNS), ("mono", c in MONO_COLUMNS)) if cond
            )
            value = html.escape(str(row[c]))
            cells.append(f'<td class="{classes}">{value}</td>')
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    st.markdown(
        f'<div class="claude-table-wrap"><table class="claude-table">'
        f"<thead><tr>{head_cells}</tr></thead><tbody>{''.join(body_rows)}</tbody>"
        f"</table></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="table-caption">{len(rows)} row{"s" if len(rows) != 1 else ""}</div>',
        unsafe_allow_html=True,
    )


def stat_card(column, label: str, value: str) -> None:
    with column:
        with st.container(border=True):
            st.markdown(f'<div class="stat-label">{html.escape(label)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{html.escape(value)}</div>', unsafe_allow_html=True)


def section_header(eyebrow: str, title: str, help_text: str = "") -> None:
    st.markdown(f'<div class="section-eyebrow">{html.escape(eyebrow)}</div>', unsafe_allow_html=True)
    st.markdown(f'<h3 class="section-title">{html.escape(title)}</h3>', unsafe_allow_html=True)
    if help_text:
        st.markdown(f'<div class="section-help">{html.escape(help_text)}</div>', unsafe_allow_html=True)
