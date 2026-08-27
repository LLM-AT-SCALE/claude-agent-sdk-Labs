"""Mirrors db/schema.sql's customer table column-for-column. No I/O."""

from __future__ import annotations

import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Customer(Base):
    __tablename__ = "customer"
    __table_args__ = (sa.UniqueConstraint("email", name="uq_customer_email"),)

    customer_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.Identity(always=True), primary_key=True
    )
    full_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    email: Mapped[str] = mapped_column(sa.Text, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    country_code: Mapped[str] = mapped_column(sa.CHAR(2), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")
    )
