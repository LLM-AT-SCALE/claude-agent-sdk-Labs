"""CLI: load one sales CSV directly through repository/, without going
through the HTTP API. Used for local development and for the step-5
verification runs recorded in reference/expected-results.json.

Usage:
    python scripts/load_sales.py reference/sample-clean.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from repository import sales_repository
from repository.db import new_session


def load_file(path: Path) -> sales_repository.BatchResult:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    session = new_session()
    try:
        return sales_repository.load_batch(session, rows)
    finally:
        session.close()


def to_report(path: Path, result: sales_repository.BatchResult) -> dict:
    return {
        "file": path.name,
        "rows_accepted": len(result.accepted),
        "rejected": [
            {"row": r.row_number, "reason": r.reason.value, "detail": r.detail}
            for r in result.rejected
        ],
        "summed_line_total": str(result.summed_line_total),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python scripts/load_sales.py <csv-file> [<csv-file> ...]")
        return 2
    for name in argv[1:]:
        path = Path(name)
        result = load_file(path)
        print(json.dumps(to_report(path, result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
