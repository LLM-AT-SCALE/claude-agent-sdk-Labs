"""Streamlit UI and orchestration.

The API key is prompted here, at run time, in a password field. It is validated
once, held in session state for the life of the browser session, and never
written to disk.

Markup lives in src/ui.py so this file reads as flow rather than HTML.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import streamlit as st

from src import ui
from src.agent import clear_api_key, run_agent, set_api_key
from src.ingestion import SUPPORTED_EXTENSIONS, UnreadableDocument, extract_text
from src.model import score_application
from src.scoring import aggregate, load_rubric
from src.validate import validate_anthropic_key

LAB_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = LAB_DIR / "data"


def sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.16em;
                        text-transform:uppercase;color:var(--ink-faint);">Lab 1</div>
            <div style="font-family:var(--font-display);font-size:26px;line-height:1.1;
                        margin:6px 0 2px;">Claude<br>Agentic SDK</div>
            <div style="font-size:12.5px;color:var(--ink-soft);">Loan Application Evaluation</div>
            <div style="height:1px;background:var(--rule-strong);margin:20px 0;"></div>

            <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:.14em;
                        text-transform:uppercase;color:var(--ink-faint);">Part A</div>
            <p style="font-size:13px;line-height:1.55;color:var(--ink-soft);margin:4px 0 16px;">
              One <strong>Messages API</strong> call. The task is fully specified, so Claude
              returns structured JSON and Python does the arithmetic.</p>

            <div style="font-family:var(--font-mono);font-size:9.5px;letter-spacing:.14em;
                        text-transform:uppercase;color:var(--ink-faint);">Part B</div>
            <p style="font-size:13px;line-height:1.55;color:var(--ink-soft);margin:4px 0 16px;">
              The <strong>Agent SDK</strong> gets a folder and tools. It decides its own
              steps and writes the memo itself.</p>

            <div style="height:1px;background:var(--rule);margin:18px 0;"></div>
            <p style="font-size:11.5px;line-height:1.55;color:var(--ink-faint);margin:0;">
              Your API key is requested at run time, used for this session only, and never
              stored.</p>
            """,
            unsafe_allow_html=True,
        )


def api_key_gate() -> str | None:
    """Prompt for the key and validate it. Returns the key once it is good."""
    ui.section("§ 01", "Authentication", "Prompted at run time — never stored in the repository.")

    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown(
            '<div style="font-size:14px;font-weight:600;margin-top:6px;">Anthropic API key</div>'
            '<div style="font-size:12.5px;color:var(--ink-faint);">'
            'Provided in your lab guide &mdash; otherwise '
            'console.anthropic.com &rarr; API keys</div>',
            unsafe_allow_html=True,
        )
    with col2:
        vAR_api_key = st.text_input(
            "Anthropic API key",
            type="password",
            label_visibility="collapsed",
            placeholder="sk-ant-...",
        )

    if not vAR_api_key:
        st.info("Enter your Anthropic API key to begin.")
        return None

    # Validate once per key, then remember the verdict for this session.
    if st.session_state.get("validated_key") != vAR_api_key:
        with st.spinner("Checking the key..."):
            message = validate_anthropic_key(vAR_api_key)
        st.session_state["validated_key"] = vAR_api_key
        st.session_state["validation_message"] = message
        st.session_state.pop("result", None)

    message = st.session_state.get("validation_message", "")
    if message != "Valid API Key!":
        st.warning(message)
        return None

    st.success(message)
    return vAR_api_key


def sample_files() -> list[str]:
    names = [
        p.name
        for p in DATA_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(names)


def choose_application() -> tuple[str, str] | None:
    """Upload an application or pick a sample. PDF, DOCX and TXT are all read."""
    ui.section(
        "§ 02",
        "The application",
        "A loan application arrives as a PDF or a Word document, so both are read here. "
        "There is no OCR — a scanned PDF has no text layer and is rejected rather than guessed at.",
    )

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


def render_result(result: dict, rubric: dict, filename: str) -> None:
    summary = aggregate(result["scores"], rubric)

    ui.decision_panel(summary)

    ui.section("§ 04", "Application", "Read from the narrative for context. None of it is scored.")
    ui.application_header(result, filename)

    ui.section("§ 05", "Financial metrics",
               "DSCR, LTV and equity injection as Claude read them out of the narrative.")
    ui.metrics_row(result.get("metrics", {}))

    ui.section("§ 06", "The five C's",
               "Each C earns (score ÷ 5) × weight. Claude chose the level; the arithmetic is Python.")
    ui.score_ledger(summary, rubric)

    ui.section("§ 07", "Why each score",
               "Open a C to see the rubric level it matched and the sentence that supports it.")
    ui.criterion_detail(result, rubric)


def part_a(narrative: str, rubric: dict, api_key: str, filename: str) -> None:
    st.markdown(
        '<p class="sec-note" style="margin-top:6px;">The task is fully specified, so one '
        'call is the right tool. Claude returns structured JSON; the weighted arithmetic '
        'runs in Python so the maths is identical every time.</p>',
        unsafe_allow_html=True,
    )

    if st.button("Score the application", key="score_btn"):
        with st.spinner("Scoring against the rubric..."):
            try:
                st.session_state["result"] = score_application(narrative, rubric, api_key)
            except Exception as exc:  # noqa: BLE001 - surfaced to the student
                st.error(f"The call failed: {exc}")
                return

    if st.session_state.get("result"):
        render_result(st.session_state["result"], rubric, filename)


def part_b(filename: str, narrative: str, api_key: str) -> None:
    st.markdown(
        '<p class="sec-note" style="margin-top:6px;">The same application, handed to an '
        'agent with a folder and tools. Watch the tool calls — that is the agent loop, '
        'made visible.</p>',
        unsafe_allow_html=True,
    )

    workspace = LAB_DIR / "outputs"
    workspace.mkdir(exist_ok=True)
    (workspace / "rubric.json").write_text(
        (LAB_DIR / "rubric.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    # The agent's tools read text, so hand it the extracted narrative rather
    # than the original binary.
    narrative_path = workspace / f"{Path(filename).stem}.txt"
    narrative_path.write_text(narrative, encoding="utf-8")

    st.markdown(
        '<p class="sec-note">The agent may use four tools — <code>Read</code>, '
        '<code>Write</code>, <code>Glob</code> and <code>Grep</code>. Anything else is '
        'refused. If you see it try <code>Bash</code> and get turned down, that is the '
        'permission boundary working, not an error: it simply does the arithmetic by '
        'hand instead.</p>',
        unsafe_allow_html=True,
    )

    if st.button("Run the agent", key="agent_btn"):
        # The transcript streams live while the agent works, then collapses into
        # an expander so the memo below is what you actually read. Without this
        # the agent's closing message and the memo file appear twice, one after
        # the other, which reads like the app repeated itself.
        log = st.empty()
        lines: list[str] = []

        async def drive() -> None:
            async for kind, text in run_agent(narrative_path, workspace):
                prefix = {"tool": "→ ", "result": "✓ ", "text": ""}[kind]
                lines.append(prefix + text)
                log.markdown(ui.agent_log(lines[-40:]), unsafe_allow_html=True)

        set_api_key(api_key)
        failed = False
        try:
            asyncio.run(drive())
        except Exception as exc:  # noqa: BLE001 - surfaced to the student
            failed = True
            st.error(f"The agent stopped: {exc}")
        finally:
            clear_api_key()

        log.empty()
        tool_calls = sum(1 for line in lines if line.startswith("→"))
        with st.expander(
            f"Agent transcript — {tool_calls} tool calls, "
            f"every step the agent chose for itself",
            expanded=failed,
        ):
            st.markdown(ui.agent_log(lines), unsafe_allow_html=True)

        memo = workspace / "credit_memo.md"
        if memo.exists():
            text = memo.read_text(encoding="utf-8")
            ui.section(
                "§ 04",
                "Credit memo",
                "Written by the agent, not by this application. Nobody gave it this "
                "layout — it chose its own headings, computed the ratios itself, and "
                "quoted the sentences it scored on.",
            )
            # Streamlit reads $...$ as LaTeX, and a credit memo is full of dollar
            # figures. Escape them or the numbers render as stacked maths.
            st.markdown(ui.escape_dollars(text))
            st.download_button("Download the memo", text, file_name="credit_memo.md")
        elif not failed:
            st.warning(
                "The agent finished without writing credit_memo.md. Run it again — "
                "the transcript above shows how far it got."
            )


def main() -> None:
    ui.load_css()
    sidebar()
    ui.masthead()

    api_key = api_key_gate()
    if not api_key:
        return

    selection = choose_application()
    if selection is None:
        st.info("Upload an application or choose a sample to continue.")
        return

    filename, narrative = selection
    with st.expander(f"Narrative — {filename}  ({len(narrative):,} characters read)"):
        st.text(narrative)

    rubric = load_rubric()

    ui.section("§ 03", "Score it",
               "The same application, scored two ways. Part A specifies the task; Part B "
               "hands it to an agent.")

    tab_a, tab_b = st.tabs(["Part A — Messages API", "Part B — Agent SDK"])
    with tab_a:
        part_a(narrative, rubric, api_key, filename)
    with tab_b:
        part_b(filename, narrative, api_key)
