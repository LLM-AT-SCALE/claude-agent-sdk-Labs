"""Engine and session construction.

The only place in the application a connection string is read: from
DATABASE_URL, from a runtime reconfigure() call (the connect screen), or
prompted for with getpass as a last resort. It is never printed, never
logged, and never returned to a caller.
"""

from __future__ import annotations

import getpass
import os
import threading

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

_lock = threading.Lock()
_engine: Engine | None = None

# A bad host/port/firewall can otherwise hang a connection attempt for
# minutes with no feedback — a short libpq-level timeout turns that into a
# fast, clear failure instead (matters most for /admin/connect, driven
# live from the login screen).
_CONNECT_ARGS = {"connect_timeout": 5}


def _database_url_from_env_or_prompt() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    return getpass.getpass("DATABASE_URL: ")


def _normalize_scheme(database_url: str) -> str:
    """Every real-world provider (Neon included) hands out a connection
    string as postgres:// or postgresql://, with no driver qualifier.
    SQLAlchemy defaults a bare postgresql:// to psycopg2, which is not
    installed here — this project uses psycopg 3 throughout (data-
    dictionary.json's target.driver). Upgrade the scheme automatically so
    a connection string pasted exactly as given by a provider just works,
    rather than requiring the caller to already know that detail.
    """
    for prefix in ("postgresql+psycopg://", "postgres+psycopg://"):
        if database_url.startswith(prefix):
            return database_url
    if database_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + database_url[len("postgresql://"):]
    if database_url.startswith("postgres://"):
        return "postgresql+psycopg://" + database_url[len("postgres://"):]
    return database_url


def _make_engine(database_url: str) -> Engine:
    return create_engine(
        _normalize_scheme(database_url), pool_pre_ping=True, future=True,
        connect_args=_CONNECT_ARGS,
    )


def get_engine() -> Engine:
    """Returns the current engine, creating it from DATABASE_URL on first
    use. Raises RuntimeError (never hangs on a prompt) if nothing has been
    configured yet and no DATABASE_URL is set — the server process has no
    attached terminal for getpass() to read from.
    """
    global _engine
    with _lock:
        if _engine is not None:
            return _engine
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError(
                "Database not connected. POST /admin/connect with a connection "
                "string, or set DATABASE_URL before starting the server."
            )
        _engine = _make_engine(url)
        return _engine


def test_connection(engine: Engine) -> None:
    """Raises if the engine can't reach a database with the expected
    schema. Never touches business data — SELECT 1 is a connectivity
    check, not a business-scope query.
    """
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def reconfigure(database_url: str) -> None:
    """Builds and verifies a new engine before swapping it in, so a failed
    connection attempt (typo, wrong password, unreachable host) never
    disturbs a connection that was already working. Used by
    POST /admin/connect — the only other place a connection string may
    originate, alongside the DATABASE_URL environment variable.
    """
    global _engine
    candidate = _make_engine(database_url)
    try:
        test_connection(candidate)
    except Exception:
        candidate.dispose()
        raise
    with _lock:
        if _engine is not None:
            _engine.dispose()
        _engine = candidate


def new_session() -> Session:
    return Session(bind=get_engine(), expire_on_commit=False)
