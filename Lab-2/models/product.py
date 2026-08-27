"""Mirrors db/schema.sql's product table column-for-column. No I/O."""

from __future__ import annotations

import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (sa.UniqueConstraint("sku", name="uq_product_sku"),)

    product_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.Identity(always=True), primary_key=True
    )
    sku: Mapped[str] = mapped_column(sa.Text, nullable=False)
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    category: Mapped[str] = mapped_column(sa.Text, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("true")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")
    )
