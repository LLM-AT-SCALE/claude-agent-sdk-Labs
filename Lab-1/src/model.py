"""Part A — the direct Messages API.

One call, one structured answer. This is the right surface when the task is
well specified: read this narrative, score it against this rubric, return JSON.
No tools, no loop, no filesystem.

Contrast with agent.py, which does the same job the agentic way.
"""

from __future__ import annotations

import json

import anthropic

MODEL = "claude-opus-5"

# The schema Claude must fill in. Constraining the shape means the app can rely
# on the fields existing instead of parsing prose.
SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "borrower": {"type": "string", "description": "Business name, or 'Not stated'."},
        "loan_amount": {"type": "string", "description": "Amount requested, or 'Not stated'."},
        "purpose": {"type": "string", "description": "Use of proceeds, or 'Not stated'."},
        "metrics": {
            "type": "object",
            "properties": {
                "dscr": {"type": "string"},
                "ltv": {"type": "string"},
                "equity_injection": {"type": "string"},
            },
            "required": ["dscr", "ltv", "equity_injection"],
            "additionalProperties": False,
        },
        "scores": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "C1 through C5."},
                    "score": {
                        "type": ["integer", "null"],
                        "description": "1-5, or null when the narrative gives no evidence at all.",
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Why this level and not the one above it.",
                    },
                    "evidence": {
                        "type": "string",
                        "description": "A sentence quoted from the narrative. Empty if none.",
                    },
                },
                "required": ["id", "score", "rationale", "evidence"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["borrower", "loan_amount", "purpose", "metrics", "scores"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """You are a credit analyst scoring a commercial loan application \
narrative against the Five C's of Credit.

Rules you must follow:
- Score only what the narrative actually says. Never infer a figure it does not state.
- Where the narrative gives the inputs, compute the ratio rather than trusting a \
stated one. DSCR = Adjusted EBITDA / Total Annual Debt Service. \
LTV = Loan Amount / Appraised Value. Equity injection % = Equity / Total Project Cost.
- If a narrative states a ratio that its own figures contradict, use the computed \
value and say so in the rationale.
- A level descriptor is compound. If a borrower matches part of level 5 and part of \
level 3, score the lower one and say which criterion held it down.
- If the narrative gives no evidence at all for a C, return null for that score. \
Do not guess, and do not score it 1 — an absence of evidence is not a weakness.
- Every rationale must be traceable to the rubric level language.
"""


def build_client(api_key: str) -> anthropic.Anthropic:
    """The key comes from the run-time prompt, never from the environment."""
    return anthropic.Anthropic(api_key=api_key.strip())


def score_application(narrative: str, rubric: dict, api_key: str) -> dict:
    """Score one narrative in a single Messages API call.

    Returns the validated object described by SCORE_SCHEMA.
    """
    client = build_client(api_key)

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Here is the rubric:\n\n"
                    f"{json.dumps(rubric, indent=2)}\n\n"
                    "Here is the loan application narrative:\n\n"
                    f"{narrative}\n\n"
                    "Score each of the five C's."
                ),
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": SCORE_SCHEMA}},
    )

    # output_config guarantees the first text block is valid JSON.
    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)
