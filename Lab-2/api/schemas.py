"""Pydantic request and response shapes. Translation only — validation
that matters lives in repository/ and in the database's own constraints.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CustomerIn(BaseModel):
    full_name: str
    email: str
    country_code: str
    city: Optional[str] = None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    full_name: str
    email: str
    city: Optional[str]
    country_code: str
    created_at: datetime.datetime


class ProductIn(BaseModel):
    sku: str
    name: str
    category: str
    unit_price: Decimal
    is_active: bool = True


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    sku: str
    name: str
    category: str
    unit_price: Decimal
    is_active: bool
    created_at: datetime.datetime


class SaleIn(BaseModel):
    customer_email: str
    sku: str
    quantity: int
    unit_price: Decimal
    sold_at: datetime.datetime


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sale_id: int
    customer_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    sold_at: datetime.datetime
    line_total: Decimal


class SalesDetailOut(BaseModel):
    sold_at: datetime.datetime
    customer_email: str
    customer_full_name: str
    product_sku: str
    product_name: str
    category: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class RejectedRowOut(BaseModel):
    row_number: int
    reason: str
    detail: str


class BatchResultOut(BaseModel):
    rows_submitted: int
    accepted: list[SaleOut]
    rejected: list[RejectedRowOut]
    summed_line_total: Decimal


class ConnectIn(BaseModel):
    database_url: str


class ConnectOut(BaseModel):
    connected: bool


class StatusOut(BaseModel):
    connected: bool
