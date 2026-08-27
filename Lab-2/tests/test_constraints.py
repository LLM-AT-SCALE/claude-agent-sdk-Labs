"""quantity 0 and -1 are refused by the database itself, not merely by
Python — proven here by inserting with raw parameterized SQL that bypasses
every application-level check. Also covers the other CHECK
constraints in db/schema.sql.
"""

from __future__ import annotations

import datetime

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from tests.conftest import requires_database


@pytest.fixture
def seed_ids(db_session):
    customer_id = db_session.execute(
        text("SELECT customer_id FROM customer ORDER BY email ASC LIMIT 1")
    ).scalar_one()
    product_id = db_session.execute(
        text("SELECT product_id FROM product ORDER BY sku ASC LIMIT 1")
    ).scalar_one()
    return customer_id, product_id


def _insert_sale_raw(session, *, customer_id, product_id, quantity, unit_price, sold_at):
    session.execute(
        text(
            "INSERT INTO sales (customer_id, product_id, quantity, unit_price, sold_at) "
            "VALUES (:customer_id, :product_id, :quantity, :unit_price, :sold_at)"
        ),
        {
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "sold_at": sold_at,
        },
    )


@requires_database
@pytest.mark.parametrize("bad_quantity", [0, -1])
def test_quantity_rejected_by_database_directly(db_session, seed_ids, unique_suffix, bad_quantity):
    customer_id, product_id = seed_ids
    sold_at = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(
        seconds=hash(unique_suffix) % 100000
    )
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            _insert_sale_raw(
                db_session,
                customer_id=customer_id,
                product_id=product_id,
                quantity=bad_quantity,
                unit_price="10.00",
                sold_at=sold_at,
            )


@requires_database
def test_negative_unit_price_rejected_by_database_directly(db_session, seed_ids, unique_suffix):
    customer_id, product_id = seed_ids
    sold_at = datetime.datetime(2030, 1, 2, tzinfo=datetime.timezone.utc) + datetime.timedelta(
        seconds=hash(unique_suffix) % 100000
    )
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            _insert_sale_raw(
                db_session,
                customer_id=customer_id,
                product_id=product_id,
                quantity=1,
                unit_price="-1.00",
                sold_at=sold_at,
            )


@requires_database
def test_blank_customer_name_rejected_by_database(db_session, unique_suffix):
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            db_session.execute(
                text(
                    "INSERT INTO customer (full_name, email, country_code) "
                    "VALUES (:full_name, :email, :country_code)"
                ),
                {
                    "full_name": "   ",
                    "email": f"blank-{unique_suffix}@example.com",
                    "country_code": "US",
                },
            )


@requires_database
def test_bad_email_format_rejected_by_database(db_session, unique_suffix):
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            db_session.execute(
                text(
                    "INSERT INTO customer (full_name, email, country_code) "
                    "VALUES (:full_name, :email, :country_code)"
                ),
                {
                    "full_name": "Test User",
                    "email": f"not-an-email-{unique_suffix}",
                    "country_code": "US",
                },
            )


@requires_database
def test_bad_country_code_rejected_by_database(db_session, unique_suffix):
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            db_session.execute(
                text(
                    "INSERT INTO customer (full_name, email, country_code) "
                    "VALUES (:full_name, :email, :country_code)"
                ),
                {
                    "full_name": "Test User",
                    "email": f"cc-{unique_suffix}@example.com",
                    # Same length as a valid code (2 chars), so this trips
                    # the ck_customer_country_code_format CHECK specifically
                    # rather than the CHAR(2) length truncation error.
                    "country_code": "us",
                },
            )


@requires_database
def test_bad_sku_format_rejected_by_database(db_session, unique_suffix):
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            db_session.execute(
                text(
                    "INSERT INTO product (sku, name, category, unit_price) "
                    "VALUES (:sku, :name, :category, :unit_price)"
                ),
                {
                    "sku": "no",
                    "name": "Test Product",
                    "category": "Test",
                    "unit_price": "1.00",
                },
            )


@requires_database
def test_negative_product_price_rejected_by_database(db_session, unique_suffix):
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            db_session.execute(
                text(
                    "INSERT INTO product (sku, name, category, unit_price) "
                    "VALUES (:sku, :name, :category, :unit_price)"
                ),
                {
                    "sku": f"NEG-{unique_suffix[:8].upper()}",
                    "name": "Test Product",
                    "category": "Test",
                    "unit_price": "-1.00",
                },
            )
