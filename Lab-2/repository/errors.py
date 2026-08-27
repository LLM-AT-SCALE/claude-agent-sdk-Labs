"""The six reject reasons a sales row can be refused for, and the
exceptions that carry them. No other reject reason exists.
"""

from __future__ import annotations

from enum import Enum


class RejectReason(str, Enum):
    UNKNOWN_CUSTOMER = "UNKNOWN_CUSTOMER"
    UNKNOWN_PRODUCT = "UNKNOWN_PRODUCT"
    MISSING_SOLD_AT = "MISSING_SOLD_AT"
    BAD_QUANTITY = "BAD_QUANTITY"
    BAD_UNIT_PRICE = "BAD_UNIT_PRICE"
    DUPLICATE_SALE = "DUPLICATE_SALE"


class SaleRejected(Exception):
    """Raised for any row that fails validation or a database constraint.

    One row is one transaction: raising this never leaves a partial write
    behind (repository/sales_repository.py rolls back to a savepoint taken
    before the row was attempted).
    """

    def __init__(self, reason: RejectReason, detail: str = ""):
        self.reason = reason
        self.detail = detail
        message = reason.value if not detail else f"{reason.value}: {detail}"
        super().__init__(message)


class DuplicateNaturalKey(Exception):
    """Raised by customer/product inserts on a duplicate email/sku.

    Not one of the six sales reject reasons — those apply only to sales
    rows — but the same 'reject, don't repair' rule applies.
    """


class InvalidValue(Exception):
    """Raised by customer/product inserts when a CHECK constraint fires —
    a blank name, a malformed email/SKU/country code, or a negative price.
    Caught at the database level, not only by application validation.
    """
