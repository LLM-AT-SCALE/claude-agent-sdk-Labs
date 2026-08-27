"""Every statement the application issues against sales, plus the
sales_detail join. Every value is bound through the SQLAlchemy expression
API — nothing here is ever built by string formatting.

submit_sale() is the one pipeline, checked in this exact
order: customer, product, sold_at, quantity, unit_price, insert. Both
insert_sale() (typed values, from the API) and load_batch() (raw strings,
from a CSV) funnel through it, so a row is classified into the same reject
reason regardless of which surface it arrived through. One row is one
transaction: a rejected row is rolled back to a savepoint and leaves
nothing behind.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Customer, Product, Sale
from repository.customer_repository import find_by_email
from repository.errors import RejectReason, SaleRejected
from repository.product_repository import find_by_sku

_UNIQUE_CONSTRAINT = "uq_sales_natural_key"
_QUANTITY_CHECK = "ck_sales_quantity_positive"
_PRICE_CHECK = "ck_sales_unit_price_nonneg"


def _constraint_name(exc: IntegrityError) -> Optional[str]:
    diag = getattr(exc.orig, "diag", None)
    return getattr(diag, "constraint_name", None) if diag is not None else None


def _parse_quantity(raw: Any) -> int:
    if isinstance(raw, bool) or not isinstance(raw, (int, str)):
        raise SaleRejected(RejectReason.BAD_QUANTITY, str(raw))
    if isinstance(raw, int):
        value = raw
    else:
        text = raw.strip()
        if not text or "." in text:
            raise SaleRejected(RejectReason.BAD_QUANTITY, str(raw))
        try:
            value = int(text)
        except ValueError as exc:
            raise SaleRejected(RejectReason.BAD_QUANTITY, str(raw)) from exc
    if value <= 0:
        raise SaleRejected(RejectReason.BAD_QUANTITY, str(raw))
    return value


def _parse_unit_price(raw: Any) -> Decimal:
    if isinstance(raw, Decimal):
        value = raw
    else:
        text = str(raw).strip() if raw is not None else ""
        if not text:
            raise SaleRejected(RejectReason.BAD_UNIT_PRICE, str(raw))
        try:
            value = Decimal(text)
        except InvalidOperation as exc:
            raise SaleRejected(RejectReason.BAD_UNIT_PRICE, str(raw)) from exc
    exponent = value.as_tuple().exponent
    if not isinstance(exponent, int) or exponent < -2:
        raise SaleRejected(RejectReason.BAD_UNIT_PRICE, str(raw))
    if value < 0 or value >= Decimal("10000000000.00"):
        raise SaleRejected(RejectReason.BAD_UNIT_PRICE, str(raw))
    return value.quantize(Decimal("0.01"))


def _parse_sold_at(raw: Any) -> datetime.datetime:
    if isinstance(raw, datetime.datetime):
        return raw
    text = str(raw).strip() if raw is not None else ""
    if not text:
        raise SaleRejected(RejectReason.MISSING_SOLD_AT, "")
    try:
        return datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SaleRejected(RejectReason.MISSING_SOLD_AT, str(raw)) from exc


def submit_sale(
    session: Session,
    *,
    customer_email: str,
    sku: str,
    raw_quantity: Any,
    raw_unit_price: Any,
    raw_sold_at: Any,
) -> Sale:
    """The one validation-and-insert pipeline. Raises SaleRejected on the
    first failing check, in the order above. Never leaves a partial write
    behind: the insert attempt runs inside a savepoint.
    """
    customer = find_by_email(session, customer_email)
    if customer is None:
        raise SaleRejected(RejectReason.UNKNOWN_CUSTOMER, customer_email)

    product = find_by_sku(session, sku)
    if product is None:
        raise SaleRejected(RejectReason.UNKNOWN_PRODUCT, sku)

    sold_at = _parse_sold_at(raw_sold_at)
    quantity = _parse_quantity(raw_quantity)
    unit_price = _parse_unit_price(raw_unit_price)

    sale = Sale(
        customer_id=customer.customer_id,
        product_id=product.product_id,
        quantity=quantity,
        unit_price=unit_price,
        sold_at=sold_at,
    )
    try:
        with session.begin_nested():
            session.add(sale)
            session.flush()
    except IntegrityError as exc:
        constraint = _constraint_name(exc)
        if constraint == _UNIQUE_CONSTRAINT:
            raise SaleRejected(
                RejectReason.DUPLICATE_SALE,
                f"{customer_email}, {sku}, {sold_at.isoformat()}",
            ) from exc
        if constraint == _QUANTITY_CHECK:
            raise SaleRejected(RejectReason.BAD_QUANTITY, str(quantity)) from exc
        if constraint == _PRICE_CHECK:
            raise SaleRejected(RejectReason.BAD_UNIT_PRICE, str(unit_price)) from exc
        raise
    session.refresh(sale)
    return sale


def insert_sale(
    session: Session,
    *,
    customer_email: str,
    sku: str,
    quantity: int,
    unit_price: Decimal,
    sold_at: datetime.datetime,
) -> Sale:
    """Typed entry point used by the API, where FastAPI has
    already parsed the request body. Runs the same pipeline as the loader.
    """
    return submit_sale(
        session,
        customer_email=customer_email,
        sku=sku,
        raw_quantity=quantity,
        raw_unit_price=unit_price,
        raw_sold_at=sold_at,
    )


def list_sales(session: Session) -> list[Sale]:
    stmt = select(Sale).order_by(Sale.sold_at.asc())
    return list(session.scalars(stmt))


@dataclass
class JoinRow:
    sold_at: datetime.datetime
    customer_email: str
    customer_full_name: str
    product_sku: str
    product_name: str
    category: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


def sales_detail(session: Session) -> list[JoinRow]:
    stmt = (
        select(
            Sale.sold_at,
            Customer.email,
            Customer.full_name,
            Product.sku,
            Product.name,
            Product.category,
            Sale.quantity,
            Sale.unit_price,
            Sale.line_total,
        )
        .join(Customer, Customer.customer_id == Sale.customer_id)
        .join(Product, Product.product_id == Sale.product_id)
        .order_by(Sale.sold_at.asc(), Customer.email.asc(), Product.sku.asc())
    )
    return [JoinRow(*row) for row in session.execute(stmt).all()]


@dataclass
class RejectedRow:
    row_number: int
    reason: RejectReason
    detail: str
    raw: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class BatchResult:
    accepted: list[Sale] = field(default_factory=list)
    rejected: list[RejectedRow] = field(default_factory=list)

    @property
    def summed_line_total(self) -> Decimal:
        total = Decimal("0.00")
        for sale in self.accepted:
            total += sale.line_total
        return total


def load_batch(session: Session, rows: Iterable[Mapping[str, Any]]) -> BatchResult:
    """Loads sales rows one at a time, in file order. A rejected row is
    reported and skipped; it never blocks the rows after it.
    """
    result = BatchResult()
    for row_number, row in enumerate(rows, start=1):
        try:
            sale = submit_sale(
                session,
                customer_email=str(row.get("customer_email", "")).strip(),
                sku=str(row.get("sku", "")).strip(),
                raw_quantity=row.get("quantity"),
                raw_unit_price=row.get("unit_price"),
                raw_sold_at=row.get("sold_at"),
            )
        except SaleRejected as exc:
            result.rejected.append(
                RejectedRow(
                    row_number=row_number,
                    reason=exc.reason,
                    detail=exc.detail,
                    raw=dict(row),
                )
            )
            continue
        result.accepted.append(sale)
    session.commit()
    return result
