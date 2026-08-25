"""Rubric loading and the weighted arithmetic.

Claude decides the 1-5 score for each C. This module does the arithmetic that
follows, in plain Python, so the maths is inspectable and identical every run.
Everything it uses comes from rubric.json.
"""

from __future__ import annotations

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

RUBRIC_PATH = Path(__file__).resolve().parent.parent / "rubric.json"


def load_rubric() -> dict:
    """Read rubric.json. It is the single source of truth for the scoring."""
    return json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))


def points_for(score: int, weight: float) -> float:
    """(score / 5) * weight — the formula declared in the rubric."""
    return (score / 5) * weight


def round_half_up(value: float) -> int:
    """Round .5 upwards.

    Python's built-in round() is banker's rounding: round(68.5) gives 68, not
    69. A credit decision should not turn on that quirk.
    """
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def band_for(total: int, rubric: dict) -> dict:
    """Find the decision band the total falls into."""
    for band in rubric["decision_bands"]:
        if band["min"] <= total <= band["max"]:
            return band
    return rubric["decision_bands"][-1]


def aggregate(scores: list[dict], rubric: dict) -> dict:
    """Turn per-C scores into a total, a band, and any hard-rule override.

    ``scores`` is the list Claude returned: one entry per C with ``id`` and
    ``score``. A score of None means the narrative gave no evidence, and that
    C's weight is left out of the total rather than counted as zero.
    """
    by_id = {r["id"]: r for r in rubric["rubrics"]}

    earned = 0.0
    evidenced_weight = 0.0
    rows = []

    for item in scores:
        section = by_id.get(item["id"])
        if section is None:
            continue

        weight = section["weight"]
        score = item.get("score")

        if score is None:
            rows.append({**item, "name": section["name"], "weight": weight, "points": None})
            continue

        earned_points = points_for(score, weight)
        earned += earned_points
        evidenced_weight += weight
        rows.append(
            {**item, "name": section["name"], "weight": weight, "points": earned_points}
        )

    if evidenced_weight == 0:
        raise ValueError("No C could be scored — the document has no usable evidence.")

    raw_total = earned / evidenced_weight * 100
    total = round_half_up(raw_total)
    band = band_for(total, rubric)

    decision = band["decision"]
    note = band["note"]
    overridden_by = None

    # Hard rules are applied after banding and override it.
    for rule in rubric.get("hard_rules", []):
        capacity = next((r for r in rows if r["id"] == "C2"), None)
        if capacity and capacity.get("score") == 1:
            decision = rule["action"]
            note = rule["reason"]
            overridden_by = rule["id"]

    return {
        "rows": rows,
        "earned": round(earned, 2),
        "evidenced_weight": evidenced_weight,
        "raw_total": round(raw_total, 2),
        "total": total,
        "decision": decision,
        "note": note,
        "banded_decision": band["decision"],
        "overridden_by": overridden_by,
        "is_incomplete": any(r["points"] is None for r in rows),
    }
