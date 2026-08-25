"""Lab 1 entry point.

Configures the page, loads the stylesheet, and hands off to src/main.py.
Run with:  streamlit run app.py
"""

from pathlib import Path

import streamlit as st

from src.main import main

LAB_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Lab 1 — Loan Application Evaluation",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_style() -> None:
    css = LAB_DIR / "style" / "final.css"
    if css.exists():
        st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


if __name__ == "__main__":
    load_style()
    main()
