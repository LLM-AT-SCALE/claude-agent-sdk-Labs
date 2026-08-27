"""No statement in repository/ is ever built by string formatting: no
f-string, no %-formatting, and no .format() builds SQL, and no UPDATE or
DELETE appears anywhere in the code base. Static,
no database required.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_DIR = REPO_ROOT / "repository"

_FSTRING_SQL = re.compile(
    r"f[\"'].*\b(SELECT|INSERT|UPDATE|DELETE)\b", re.IGNORECASE
)
_PERCENT_FORMAT = re.compile(r"[\"']\s*%\s*[\"']|%\s*\(")
_DOT_FORMAT = re.compile(r"\.format\(")

# repository/ never uses raw text() at all (it's pure ORM), but if that
# ever changes, this still guards against building the *SQL string itself*
# via formatting. Binding parameters through :name / .params() is fine;
# this only flags string construction of the statement text.
_SQL_KEYWORDS = re.compile(r"\b(SELECT|INSERT INTO|UPDATE|DELETE FROM)\b", re.IGNORECASE)


def _source_files():
    return sorted(REPOSITORY_DIR.glob("*.py"))


def test_repository_files_exist():
    files = _source_files()
    assert files, "repository/ has no .py files to check"


def test_no_fstring_or_percent_or_format_builds_sql():
    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if _FSTRING_SQL.search(line):
                raise AssertionError(
                    f"{path.relative_to(REPO_ROOT)}:{lineno}: f-string appears "
                    f"to build SQL: {line.strip()!r}"
                )
            if _SQL_KEYWORDS.search(line) and (
                _PERCENT_FORMAT.search(line) or _DOT_FORMAT.search(line)
            ):
                raise AssertionError(
                    f"{path.relative_to(REPO_ROOT)}:{lineno}: SQL keyword "
                    f"combined with %-formatting or .format(): {line.strip()!r}"
                )


def test_no_update_or_delete_statement_anywhere_in_repository():
    forbidden = re.compile(r"\bUPDATE\s+\w+\s+SET\b|\bDELETE\s+FROM\b", re.IGNORECASE)
    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if forbidden.search(line):
                raise AssertionError(
                    f"{path.relative_to(REPO_ROOT)}:{lineno}: looks like an "
                    f"UPDATE or DELETE statement: {line.strip()!r}"
                )
