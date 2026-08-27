"""The same natural key (customer_id, product_id, sold_at) inserted twice
raises rather than duplicating — whether through submit_sale() directly or
through a CSV batch that repeats a row.
"""

from __future__ import annotations

import csv
import datetime
import io
from decimal import Decimal

import pytest
from sqlalchemy import text

from repository.errors import RejectReason, SaleRejected
from repository.sales_repository import load_batch, submit_sale
from repository.db import new_session
from tests.conftest import requires_database


@requires_database
def test_second_insert_of_same_natural_key_raises(db_session, unique_suffix):
    sold_at = datetime.datetime(2032, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(
        seconds=hash(unique_suffix) % 100000
    )
    with db_session.begin_nested():
        submit_sale(
            db_session,
            customer_email="priya.raman@example.com",
            sku="MS-TRACK-02",
            raw_quantity=1,
            raw_unit_price=Decimal("79.50"),
            raw_sold_at=sold_at,
        )

    with pytest.raises(SaleRejected) as excinfo:
        with db_session.begin_nested():
            submit_sale(
                db_session,
                customer_email="priya.raman@example.com",
                sku="MS-TRACK-02",
                raw_quantity=99,
                raw_unit_price=Decimal("1.00"),
                raw_sold_at=sold_at,
            )
    assert excinfo.value.reason == RejectReason.DUPLICATE_SALE

    count = db_session.execute(
        text(
            "SELECT count(*) FROM sales WHERE customer_id = "
            "(SELECT customer_id FROM customer WHERE email = 'priya.raman@example.com') "
            "AND sold_at = :sold_at"
        ),
        {"sold_at": sold_at},
    ).scalar_one()
    assert count == 1


@requires_database
def test_replaying_the_same_batch_inserts_nothing_new(unique_suffix):
    sold_at = f"2032-06-01T10:00:{(hash(unique_suffix) % 60):02d}Z"
    csv_text = (
        "customer_email,sku,quantity,unit_price,sold_at\n"
        f"jonas.berg@example.com,ST-NVME-2TB,1,158.40,{sold_at}\n"
    )
    rows = list(csv.DictReader(io.StringIO(csv_text)))

    session_one = new_session()
    try:
        first = load_batch(session_one, rows)
    finally:
        session_one.close()
    assert len(first.accepted) == 1
    assert first.rejected == []

    session_two = new_session()
    try:
        second = load_batch(session_two, rows)
    finally:
        session_two.rollback()
        session_two.close()
    assert second.accepted == []
    assert len(second.rejected) == 1
    assert second.rejected[0].reason == RejectReason.DUPLICATE_SALE
