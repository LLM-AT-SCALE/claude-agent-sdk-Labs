"""Every statement the application issues against product. Every value is
bound through the SQLAlchemy expression API — nothing here is ever built
by string formatting.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Product
from repository.errors import DuplicateNaturalKey, InvalidValue

_UNIQUE_CONSTRAINT = "uq_product_sku"


def _constraint_name(exc: IntegrityError) -> Optional[str]:
    diag = getattr(exc.orig, "diag", None)
    return getattr(diag, "constraint_name", None) if diag is not None else None


def insert_product(
    session: Session,
    *,
    sku: str,
    name: str,
    category: str,
    unit_price: Decimal,
    is_active: bool = True,
) -> Product:
    product = Product(
        sku=sku.strip(),
        name=name,
        category=category,
        unit_price=unit_price,
        is_active=is_active,
    )
    session.add(product)
    try:
        with session.begin_nested():
            session.flush()
    except IntegrityError as exc:
        constraint = _constraint_name(exc)
        if constraint == _UNIQUE_CONSTRAINT:
            raise DuplicateNaturalKey(f"sku already on file: {product.sku}") from exc
        raise InvalidValue(str(exc.orig)) from exc
    session.refresh(product)
    return product


def list_products(session: Session) -> list[Product]:
    stmt = select(Product).order_by(Product.sku.asc())
    return list(session.scalars(stmt))


def find_by_sku(session: Session, sku: str) -> Optional[Product]:
    stmt = select(Product).where(Product.sku == sku.strip())
    return session.scalars(stmt).first()
