"""A Decimal survives a round trip through NUMERIC exactly — no float
drift. 0.10 cannot be represented exactly in binary floating point, so
this is the test that would catch a `float` sneaking into the write path
in the write path.
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest
from sqlalchemy import text

from repository.sales_repository import submit_sale
from tests.conftest import requires_database


@requires_database
@pytest.mark.parametrize(
    "price", [Decimal("0.10"), Decimal("19.99"), Decimal("429.99"), Decimal("1000000.01")]
)
def test_product_unit_price_roundtrips_exactly(db_session, unique_suffix, price):
    sku = f"RT-{unique_suffix[:8].upper()}"
    db_session.execute(
        text(
            "INSERT INTO product (sku, name, category, unit_price) "
            "VALUES (:sku, :name, :category, :unit_price)"
        ),
        {"sku": sku, "name": "Roundtrip Product", "category": "Test", "unit_price": price},
    )
    fetched = db_session.execute(
        text("SELECT unit_price FROM product WHERE sku = :sku"), {"sku": sku}
    ).scalar_one()
    assert isinstance(fetched, Decimal)
    assert fetched == price


@requires_database
def test_sale_line_total_is_decimal_with_no_drift(db_session, unique_suffix):
    sold_at = datetime.datetime(2033, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(
        seconds=hash(unique_suffix) % 100000
    )
    sale = submit_sale(
        db_session,
        customer_email="sara.haddad@example.com",
        sku="ST-NVME-2TB",
        raw_quantity=3,
        raw_unit_price=Decimal("0.10"),
        raw_sold_at=sold_at,
    )
    assert isinstance(sale.unit_price, Decimal)
    assert isinstance(sale.line_total, Decimal)
    assert sale.unit_price == Decimal("0.10")
    assert sale.line_total == Decimal("0.30")
    # The float form of 0.10 is not exact; the Decimal form must be.
    assert float(Decimal("0.10")) != Decimal("0.10")
    assert sale.line_total == Decimal(3) * Decimal("0.10")
