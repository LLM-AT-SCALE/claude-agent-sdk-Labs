"""Mirrors db/schema.sql's sales table column-for-column. No I/O.

line_total is mapped as Computed(persisted=True) so the model documents
that the database owns it. It is never assigned in application code.
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        sa.UniqueConstraint(
            "customer_id", "product_id", "sold_at", name="uq_sales_natural_key"
        ),
    )

    sale_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.Identity(always=True), primary_key=True
    )
    customer_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        sa.ForeignKey("customer.customer_id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        sa.ForeignKey("product.product_id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2), nullable=False)
    sold_at: Mapped[datetime.datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False
    )
    line_total: Mapped[Decimal] = mapped_column(
        sa.Numeric(14, 2),
        sa.Computed("quantity * unit_price", persisted=True),
        nullable=False,
    )
