"""line_total always equals quantity * unit_price, and cannot be written
directly — the database computes it; naming it in an INSERT is rejected
even when parameterized correctly.
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from repository.sales_repository import submit_sale
from tests.conftest import requires_database


@requires_database
@pytest.mark.parametrize(
    ("quantity", "unit_price"),
    [(2, Decimal("189.00")), (3, Decimal("0.10")), (7, Decimal("19.99"))],
)
def test_line_total_equals_quantity_times_unit_price(
    db_session, unique_suffix, quantity, unit_price
):
    sold_at = datetime.datetime(2031, 1, 1, tzinfo=datetime.timezone.utc)
    sale = submit_sale(
        db_session,
        customer_email="ava.mendez@example.com",
        sku="KB-ERGO-01",
        raw_quantity=quantity,
        raw_unit_price=unit_price,
        raw_sold_at=sold_at.replace(microsecond=hash(unique_suffix) % 1000 * 1000),
    )
    assert sale.line_total == quantity * unit_price


@requires_database
def test_line_total_cannot_be_written_directly(db_session, unique_suffix):
    customer_id = db_session.execute(
        text("SELECT customer_id FROM customer ORDER BY email ASC LIMIT 1")
    ).scalar_one()
    product_id = db_session.execute(
        text("SELECT product_id FROM product ORDER BY sku ASC LIMIT 1")
    ).scalar_one()
    sold_at = datetime.datetime(2031, 1, 2, tzinfo=datetime.timezone.utc) + datetime.timedelta(
        seconds=hash(unique_suffix) % 100000
    )
    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(
                text(
                    "INSERT INTO sales "
                    "(customer_id, product_id, quantity, unit_price, sold_at, line_total) "
                    "VALUES (:customer_id, :product_id, :quantity, :unit_price, :sold_at, :line_total)"
                ),
                {
                    "customer_id": customer_id,
                    "product_id": product_id,
                    "quantity": 1,
                    "unit_price": "10.00",
                    "sold_at": sold_at,
                    "line_total": "10.00",
                },
            )
