"""Applies db/*.sql files against DATABASE_URL, in order.

Usage:
    python db/run.py                       # applies schema.sql then seed.sql
    python db/run.py drop.sql               # tears everything down
    python db/run.py drop.sql schema.sql seed.sql   # full rebuild

The connection string is read from DATABASE_URL, or prompted for at run
time if unset. It is never printed or logged.
"""

from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

import psycopg

DB_DIR = Path(__file__).resolve().parent


def _for_psycopg(url: str) -> str:
    """DATABASE_URL follows the SQLAlchemy scheme postgresql+psycopg://
    (data-dictionary.json's target block) everywhere else in this codebase,
    but this script talks to psycopg directly rather than through
    SQLAlchemy, and psycopg's own connect() does not understand the
    '+psycopg' driver qualifier — only SQLAlchemy's create_engine() strips
    it. Normalize it here so one DATABASE_URL value works for both.
    """
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        url = getpass.getpass("DATABASE_URL: ")
    return _for_psycopg(url)


def apply_file(conn: psycopg.Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"applied {path.name}")


def main(argv: list[str]) -> int:
    filenames = argv[1:] or ["schema.sql", "seed.sql"]
    database_url = get_database_url()
    with psycopg.connect(database_url) as conn:
        for name in filenames:
            apply_file(conn, DB_DIR / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
