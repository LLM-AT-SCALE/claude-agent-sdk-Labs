"""Every statement the application issues against customer. Every value is
bound through the SQLAlchemy expression API — nothing here is ever built
by string formatting.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Customer
from repository.errors import DuplicateNaturalKey, InvalidValue

_UNIQUE_CONSTRAINT = "uq_customer_email"


def _constraint_name(exc: IntegrityError) -> Optional[str]:
    diag = getattr(exc.orig, "diag", None)
    return getattr(diag, "constraint_name", None) if diag is not None else None


def insert_customer(
    session: Session,
    *,
    full_name: str,
    email: str,
    country_code: str,
    city: Optional[str] = None,
) -> Customer:
    customer = Customer(
        full_name=full_name,
        email=email.strip().lower(),
        city=city,
        country_code=country_code,
    )
    session.add(customer)
    try:
        with session.begin_nested():
            session.flush()
    except IntegrityError as exc:
        constraint = _constraint_name(exc)
        if constraint == _UNIQUE_CONSTRAINT:
            raise DuplicateNaturalKey(
                f"email already on file: {customer.email}"
            ) from exc
        raise InvalidValue(str(exc.orig)) from exc
    session.refresh(customer)
    return customer


def list_customers(session: Session) -> list[Customer]:
    stmt = select(Customer).order_by(Customer.email.asc())
    return list(session.scalars(stmt))


def find_by_email(session: Session, email: str) -> Optional[Customer]:
    stmt = select(Customer).where(Customer.email == email.strip().lower())
    return session.scalars(stmt).first()
