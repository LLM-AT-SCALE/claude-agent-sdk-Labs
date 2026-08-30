"""Presentation helpers.

Streamlit's default chrome is generic, so the lab renders its own components
against the design system in style/final.css. Keeping the HTML here leaves
main.py to read as orchestration rather than markup.
"""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

STYLE_PATH = Path(__file__).resolve().parent.parent / "style" / "final.css"

# Colours are applied by class, never inline.
#
# Streamlit's markdown sanitiser keeps only a narrow whitelist of properties in
# inline style attributes — `width` survives, `background` and `color` are
# dropped, as are CSS custom properties. Class names always survive, so every
# colour that varies per row is a modifier class defined in final.css and these
# helpers just pick the suffix.
DECISION_SLUGS = {
    "APPROVE": "approve",
    "APPROVE WITH CONDITIONS": "conditions",
    "REFER TO CREDIT COMMITTEE": "refer",
    "DECLINE": "decline",
}


def decision_slug(decision: str) -> str:
    """Class suffix for a decision, e.g. "conditions"."""
    return DECISION_SLUGS.get(decision.upper(), "neutral")


def score_slug(score: int | None) -> str:
    """Class suffix for a score: "1".."5", or "ne" where there was no evidence."""
    if score is None:
        return "ne"
    return str(max(1, min(5, score)))


def load_css() -> None:
    """Inject the stylesheet once per run."""
    st.markdown(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def _esc(value) -> str:
    return html.escape(str(value)) if value is not None else ""


def escape_dollars(text: str) -> str:
    """Stop Streamlit reading dollar amounts as LaTeX.

    Streamlit's markdown treats ``$...$`` as inline maths. A credit memo is full
    of figures like "$1,280,000 / $1,000,000", so every second dollar sign opens
    a maths span and the numbers render as stacked LaTeX instead of text.
    Escaping the sign keeps them as currency.
    """
    return text.replace("$", r"\$")


def masthead() -> None:
    st.markdown(
        """
        <div class="masthead">
          <div>
            <h1 class="masthead-title">Loan Application<br><em>Evaluation</em></h1>
            <p class="masthead-tagline">
              Score a commercial loan application against the Five C&rsquo;s of Credit &mdash;
              first with a single Messages API call, then with the Claude Agent SDK.
            </p>
          </div>
          <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;">
            <span class="badge"><span class="badge-dot"></span>Lab 1</span>
            <span class="badge">Agent SDK &middot; Messages API</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(mark: str, title: str, note: str | None = None) -> None:
    note_html = f'<p class="sec-note">{_esc(note)}</p>' if note else ""
    st.markdown(
        f"""
        <div class="sec"><span class="sec-mark">{_esc(mark)}</span>
          <h2 class="sec-title">{_esc(title)}</h2></div>
        {note_html}
        <div class="sec-rule"></div>
        """,
        unsafe_allow_html=True,
    )


def decision_panel(summary: dict) -> None:
    """The verdict, the score, and the arithmetic that produced it."""
    slug = decision_slug(summary["decision"])

    flags = ['<span class="eyebrow">Decision</span>']
    if summary["is_incomplete"]:
        flags.append('<span class="flag flag-incomplete">Incomplete</span>')
    if summary["overridden_by"]:
        flags.append(
            f'<span class="flag flag-override">{_esc(summary["overridden_by"])} override</span>'
        )

    renormalised = summary["evidenced_weight"] != 100
    working = (
        f'{summary["earned"]:g} &divide; {summary["evidenced_weight"]:g} &times; 100'
        + (
            f'<br>= {summary["raw_total"]:g} &rarr; {summary["total"]}'
            if renormalised
            else ""
        )
    )

    st.markdown(
        f"""
        <div class="decision">
          <div class="decision-spine spine-{slug}"></div>
          <div class="decision-verdict">
            <div class="flags">{"".join(flags)}</div>
            <p class="decision-word word-{slug}">{_esc(summary["decision"])}</p>
            <p class="decision-note">{_esc(summary["note"])}</p>
          </div>
          <div class="score-block">
            <span class="eyebrow">Weighted score</span>
            <span class="score-value">{summary["total"]}</span>
            <span class="score-outof">out of 100</span>
            <div class="score-working">{working}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if summary["overridden_by"]:
        st.markdown(
            f"""<div class="callout callout-decline">
              <strong>Hard rule {_esc(summary["overridden_by"])} set this decision.</strong>
              The weighted score of {summary["total"]}
              {"banded to the same outcome independently."
               if summary["banded_decision"] == summary["decision"]
               else f'would otherwise have banded as {_esc(summary["banded_decision"])}.'}
            </div>""",
            unsafe_allow_html=True,
        )

    if summary["is_incomplete"]:
        missing = ", ".join(r["name"] for r in summary["rows"] if r["points"] is None)
        st.markdown(
            f"""<div class="callout callout-refer">
              <strong>Decided on partial evidence.</strong> The narrative said nothing about
              {_esc(missing)}, so that weight was removed from the denominator rather than
              counted as zero. Silence is not the same as weakness.
            </div>""",
            unsafe_allow_html=True,
        )


def split_metric(value: str) -> tuple[str, str]:
    """Separate the headline figure from the working that produced it.

    Claude returns metrics like "1.28x (computed: $1,280,000 Adjusted EBITDA /
    $1,000,000 total annual debt service)". Rendering that whole string at
    display size wraps it over five lines and throws the card grid out of
    alignment, so the figure and its working are shown at different weights.
    """
    head, sep, rest = value.partition("(")
    if not sep:
        return value.strip(), ""
    return head.strip(), rest.rstrip(")").strip()


def metrics_row(metrics: dict) -> None:
    """DSCR, LTV and equity injection as Claude read or computed them."""
    cards = []
    for label, key in (
        ("Debt Service Coverage", "dscr"),
        ("Loan-to-Value", "ltv"),
        ("Equity injection", "equity_injection"),
    ):
        value = (metrics or {}).get(key) or "Not stated"
        absent = value.strip().lower().startswith(("not stated", "not computable", "n/e", "none")) or not value.strip()
        head, detail = split_metric(value)
        detail_html = f'<div class="metric-detail">{_esc(detail)}</div>' if detail else ""
        # One line, no indentation: a blank or indented line inside this HTML
        # makes Streamlit's markdown render the rest of it as a code block.
        cards.append(
            f'<div class="metric">'
            f'<div class="metric-label">{_esc(label)}</div>'
            f'<div class="metric-value {"metric-absent" if absent else ""}">{_esc(head)}</div>'
            f'{detail_html}'
            f'<div class="metric-sub">{"no evidence" if absent else "from the narrative"}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="metrics">{"".join(cards)}</div>', unsafe_allow_html=True)


def score_ledger(summary: dict, rubric: dict) -> None:
    """The five C's as a ledger: score chip, weight, points, proportion bar."""
    questions = {r["id"]: r.get("question", "") for r in rubric["rubrics"]}

    rows = []
    for row in summary["rows"]:
        score = row.get("score")
        sslug = score_slug(score)
        fill = 0 if score is None else score / 5
        points = "&mdash;" if row["points"] is None else f"{row['points']:g}"
        label = "N/E" if score is None else str(score)

        rows.append(
            f"""<tr>
              <td class="led-mark">{_esc(row["id"])}</td>
              <td class="led-name">{_esc(row["name"])}
                <span class="led-q">{_esc(questions.get(row["id"], ""))}</span></td>
              <td style="text-align:right;">
                <span class="chip chip-{sslug}">{label}</span></td>
              <td class="led-fig">{row["weight"]:g}</td>
              <td class="led-fig {"led-muted" if row["points"] is None else ""}">{points}</td>
              <td><div class="bar"><div class="bar-fill bar-{sslug}"
                style="width:{fill * 100:.0f}%;"></div></div></td>
            </tr>"""
        )

    arrow = (
        f' &rarr; {summary["total"]}'
        if summary["raw_total"] != summary["total"]
        else ""
    )

    st.markdown(
        f"""
        <table class="ledger">
          <thead><tr>
            <th></th><th>Criterion</th>
            <th style="text-align:right;">Score</th>
            <th style="text-align:right;">Weight</th>
            <th style="text-align:right;">Points</th><th></th>
          </tr></thead>
          <tbody>{"".join(rows)}</tbody>
          <tfoot><tr class="totals">
            <td></td>
            <td class="total-label">{"Total over evidenced weight"
              if summary["evidenced_weight"] != 100 else "Total"}</td>
            <td></td>
            <td class="led-fig">{summary["evidenced_weight"]:g}</td>
            <td class="led-fig">{summary["earned"]:g}</td>
            <td>= {summary["raw_total"]:g}{arrow} / 100</td>
          </tr></tfoot>
        </table>
        """,
        unsafe_allow_html=True,
    )


def criterion_detail(result: dict, rubric: dict) -> None:
    """Per-C rationale and the sentence Claude quoted for it."""
    by_id = {r["id"]: r for r in rubric["rubrics"]}

    for row in result.get("scores", []):
        section_ = by_id.get(row["id"])
        name = section_["name"] if section_ else row["id"]
        score = row.get("score")
        label = "N/E" if score is None else f"{score} / 5"

        with st.expander(f"{row['id']}  ·  {name}  —  {label}"):
            st.markdown(
                f'<p class="rationale">{_esc(row.get("rationale", ""))}</p>',
                unsafe_allow_html=True,
            )

            if section_ and score is not None:
                descriptor = section_["levels"].get(str(score), "")
                if descriptor:
                    st.markdown(
                        f'<blockquote class="quote">'
                        f'<span class="quote-label">Rubric level {score} reads</span>'
                        f"{_esc(descriptor)}</blockquote>",
                        unsafe_allow_html=True,
                    )

            if row.get("evidence"):
                st.markdown(
                    f'<blockquote class="quote">'
                    f'<span class="quote-label">Evidence from the narrative</span>'
                    f"&ldquo;{_esc(row['evidence'])}&rdquo;</blockquote>",
                    unsafe_allow_html=True,
                )


def application_header(result: dict, filename: str) -> None:
    """Borrower, amount and purpose — context, never scored."""
    rows = [
        ("Borrower", result.get("borrower")),
        ("Amount requested", result.get("loan_amount")),
        ("Purpose", result.get("purpose")),
        ("Source document", filename),
    ]
    cells = "".join(
        f"""<tr>
              <td class="total-label" style="padding:9px 18px 9px 0;white-space:nowrap;
                  border-bottom:1px solid var(--rule);">{_esc(k)}</td>
              <td style="padding:9px 0;font-size:14.5px;
                  border-bottom:1px solid var(--rule);">{_esc(v or "Not stated")}</td>
            </tr>"""
        for k, v in rows
    )
    st.markdown(
        f'<table style="width:100%;border-collapse:collapse;">{cells}</table>',
        unsafe_allow_html=True,
    )


def agent_log(lines: list[str]) -> str:
    """Render the agent's progress as a monospace transcript.

    Dollar signs are escaped for the same reason as in ``escape_dollars``: the
    agent narrates figures as it works, and unescaped they turn into LaTeX.
    """
    body = "".join(
        f'<span class="agent-tool">{escape_dollars(_esc(line))}</span>\n'
        if line.startswith("→") or line.startswith("->")
        else f"{escape_dollars(_esc(line))}\n"
        for line in lines
    )
    return f'<div class="agent-log">{body}</div>'
