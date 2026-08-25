"""Streamlit UI and orchestration.

The API key is prompted here, at run time, in a password field. It is validated
once, held in session state for the life of the browser session, and never
written to disk.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import streamlit as st

from src.agent import clear_api_key, run_agent, set_api_key
from src.ingestion import SUPPORTED_EXTENSIONS, UnreadableDocument, extract_text
from src.model import score_application
from src.scoring import aggregate, load_rubric
from src.validate import validate_anthropic_key

LAB_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = LAB_DIR / "data"

DECISION_COLOURS = {
    "APPROVE": "#1E7B44",
    "APPROVE WITH CONDITIONS": "#2F6F8F",
    "REFER TO CREDIT COMMITTEE": "#A8690E",
    "DECLINE": "#A32A2A",
}


def sidebar() -> None:
    with st.sidebar:
        st.markdown("### Lab 1")
        st.markdown("**Loan Application Evaluation**")
        st.markdown("Claude Agent SDK + Messages API")
        st.markdown("---")
        st.markdown(
            "**Part A** scores the application in one Messages API call.\n\n"
            "**Part B** hands the same application to an agent that reads the "
            "files, works through the rubric and writes a memo itself."
        )
        st.markdown("---")
        st.caption(
            "Your API key is requested at run time, used for this session only, "
            "and never stored."
        )


def api_key_gate() -> str | None:
    """Prompt for the key and validate it. Returns the key once it is good."""
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Anthropic API key")
        st.caption("Prompted at run time — never stored in the repository.")

    with col2:
        vAR_api_key = st.text_input(
            "Anthropic API key",
            type="password",
            label_visibility="collapsed",
            placeholder="sk-ant-...",
        )

    if not vAR_api_key:
        st.info("Enter your Anthropic API key above to begin.")
        return None

    # Validate once per key, then remember the verdict for this session.
    if st.session_state.get("validated_key") != vAR_api_key:
        with st.spinner("Checking the key..."):
            message = validate_anthropic_key(vAR_api_key)
        st.session_state["validated_key"] = vAR_api_key
        st.session_state["validation_message"] = message

    message = st.session_state.get("validation_message", "")

    if message != "Valid API Key!":
        st.warning(message)
        return None

    st.success(message)
    return vAR_api_key


def sample_files() -> list[str]:
    """Every sample shipped with the lab, in a stable order."""
    names = [
        p.name
        for p in DATA_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(names)


def choose_narrative() -> tuple[str, str] | None:
    """Let the user upload an application or pick one of the samples.

    A real application arrives as a PDF or a Word document, so both are read
    here; .txt is accepted too because it makes the samples easy to inspect.
    """
    col1, col2 = st.columns(2)

    with col1:
        uploaded = st.file_uploader(
            "Upload a loan application (PDF or DOCX)",
            type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
        )
    with col2:
        chosen = st.selectbox("...or use a sample application", ["—"] + sample_files())

    source: tuple[str, bytes] | None = None
    if uploaded is not None:
        source = (uploaded.name, uploaded.read())
    elif chosen and chosen != "—":
        source = (chosen, (DATA_DIR / chosen).read_bytes())

    if source is None:
        return None

    filename, data = source
    try:
        return filename, extract_text(filename, data)
    except UnreadableDocument as exc:
        st.error(str(exc))
        return None


def render_result(result: dict, rubric: dict) -> None:
    """Show the decision, the arithmetic, and the per-C detail."""
    summary = aggregate(result["scores"], rubric)
    colour = DECISION_COLOURS.get(summary["decision"], "#3E4C59")

    st.markdown(
        f"<div style='padding:18px 22px;border-radius:4px;background:{colour};"
        f"color:#fff;margin-bottom:18px;'>"
        f"<div style='font-size:11px;letter-spacing:.14em;opacity:.85;'>DECISION</div>"
        f"<div style='font-size:30px;font-weight:700;'>{summary['decision']}</div>"
        f"<div style='font-size:14px;opacity:.9;margin-top:6px;'>"
        f"Weighted score {summary['total']} / 100</div></div>",
        unsafe_allow_html=True,
    )

    if summary["overridden_by"]:
        st.error(
            f"Hard rule {summary['overridden_by']} set this decision. "
            f"The weighted score of {summary['total']} would otherwise have banded as "
            f"{summary['banded_decision']}. {summary['note']}"
        )
    else:
        st.caption(summary["note"])

    if summary["is_incomplete"]:
        st.warning(
            "INCOMPLETE — one or more C's had no supporting evidence. Their weight was "
            "left out of the total rather than counted as zero."
        )

    st.markdown("#### Application")
    left, middle, right = st.columns(3)
    left.metric("Borrower", result.get("borrower", "Not stated"))
    middle.metric("Amount", result.get("loan_amount", "Not stated"))
    right.metric("DSCR", result.get("metrics", {}).get("dscr", "Not stated"))

    st.markdown("#### The five C's")
    st.caption(
        f"{summary['earned']} ÷ {summary['evidenced_weight']} × 100 = "
        f"{summary['raw_total']} → {summary['total']}"
    )

    table = [
        {
            "C": row["id"],
            "Criterion": row["name"],
            "Score": "N/E" if row.get("score") is None else row["score"],
            "Weight": row["weight"],
            "Points": "—" if row["points"] is None else round(row["points"], 1),
        }
        for row in summary["rows"]
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown("#### Why each score")
    for row in result["scores"]:
        section = next((r for r in rubric["rubrics"] if r["id"] == row["id"]), None)
        label = section["name"] if section else row["id"]
        score = "N/E" if row.get("score") is None else f"{row['score']} / 5"
        with st.expander(f"{row['id']} · {label} — {score}"):
            st.write(row.get("rationale", ""))
            if row.get("evidence"):
                st.markdown(f"> _{row['evidence']}_")


def part_a(narrative: str, rubric: dict, api_key: str) -> None:
    st.markdown("### Part A — one Messages API call")
    st.caption(
        "The task is fully specified, so a single call is the right tool. "
        "Claude returns structured JSON; the weighted arithmetic is done in Python."
    )

    if st.button("Score the application", type="primary", key="score_btn"):
        with st.spinner("Scoring against the rubric..."):
            try:
                result = score_application(narrative, rubric, api_key)
            except Exception as exc:  # noqa: BLE001 - surfaced to the student
                st.error(f"The call failed: {exc}")
                return
        st.session_state["result"] = result

    if st.session_state.get("result"):
        render_result(st.session_state["result"], rubric)


def part_b(filename: str, narrative: str, api_key: str) -> None:
    st.markdown("### Part B — the Claude Agent SDK")
    st.caption(
        "The same application, handed to an agent with a folder and tools. "
        "It decides its own steps and writes the memo itself."
    )

    workspace = LAB_DIR / "outputs"
    workspace.mkdir(exist_ok=True)
    (workspace / "rubric.json").write_text(
        (LAB_DIR / "rubric.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    # The agent reads text, so hand it the extracted narrative rather than the
    # original binary — a .pdf holding plain text would only confuse it.
    narrative_path = workspace / f"{Path(filename).stem}.txt"
    narrative_path.write_text(narrative, encoding="utf-8")

    if st.button("Run the agent", type="primary", key="agent_btn"):
        log = st.empty()
        lines: list[str] = []

        async def drive() -> None:
            async for kind, text in run_agent(narrative_path, workspace):
                prefix = {"tool": "→ ", "result": "✓ ", "text": ""}[kind]
                lines.append(prefix + text)
                log.markdown("\n\n".join(lines[-40:]))

        set_api_key(api_key)
        try:
            asyncio.run(drive())
        except Exception as exc:  # noqa: BLE001 - surfaced to the student
            st.error(f"The agent stopped: {exc}")
        finally:
            clear_api_key()

        memo = workspace / "credit_memo.md"
        if memo.exists():
            st.success("The agent wrote credit_memo.md.")
            st.markdown("#### Credit memo")
            st.markdown(memo.read_text(encoding="utf-8"))
            st.download_button(
                "Download the memo",
                memo.read_text(encoding="utf-8"),
                file_name="credit_memo.md",
            )


def main() -> None:
    sidebar()

    st.markdown("## Loan Application Evaluation")
    st.caption(
        "Score a commercial loan application against the Five C's of Credit — "
        "first with a single Messages API call, then with the Claude Agent SDK."
    )
    st.markdown("---")

    api_key = api_key_gate()
    if not api_key:
        return

    st.markdown("---")
    selection = choose_narrative()
    if selection is None:
        st.info("Upload a narrative or choose a sample to continue.")
        return

    filename, narrative = selection
    with st.expander(f"Narrative — {filename}"):
        st.text(narrative)

    rubric = load_rubric()
    st.markdown("---")

    tab_a, tab_b = st.tabs(["Part A — Messages API", "Part B — Agent SDK"])
    with tab_a:
        part_a(narrative, rubric, api_key)
    with tab_b:
        part_b(filename, narrative, api_key)
