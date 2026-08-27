"""Shared fixtures. DB-backed tests need TEST_DATABASE_URL pointing at a
disposable Postgres with db/schema.sql and db/seed.sql already applied —
they skip cleanly if it's unset, rather than faking a result.

No DELETE is ever issued to clean up between tests (that rule applies to
test code too): each test that writes data uses a fresh,
unique natural key via `unique_suffix`, so tests never collide with each
other, with the seed data, or with a previous run. Anything a test inserts
outside an explicit commit is undone by the fixture's rollback.
"""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy.orm import Session

from repository.db import _make_engine

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

requires_database = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason=(
        "TEST_DATABASE_URL not set; database-backed tests skipped. Point it "
        "at a disposable Postgres 15+ with db/schema.sql and db/seed.sql "
        "already applied."
    ),
)


@pytest.fixture(scope="session")
def engine():
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL not set")
    # Built through repository/db.py's own factory so the tests accept
    # exactly the connection-string shapes the application accepts —
    # including a bare postgresql:// as handed out by Neon and others.
    return _make_engine(TEST_DATABASE_URL)


@pytest.fixture
def db_session(engine):
    session = Session(bind=engine, expire_on_commit=False)
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def unique_suffix():
    return uuid.uuid4().hex[:10]
