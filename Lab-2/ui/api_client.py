"""Every HTTP call the UI makes.

The UI reaches the database only through these functions. It never imports
repository/ or models/, and holds no connection string of its own — which is
what keeps the layer boundary real rather than merely stated.
"""

from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text
    detail = payload.get("detail", payload)
    if isinstance(detail, dict):
        reason = detail.get("reason")
        text = detail.get("detail")
        return f"{reason} — {text}" if reason else str(detail)
    return str(detail)


def post(path: str, **kwargs):
    return requests.post(f"{API_BASE_URL}{path}", timeout=30, **kwargs)


def get(path: str):
    return requests.get(f"{API_BASE_URL}{path}", timeout=30)


def money(text: str) -> str:
    """Validate a money field the same way the API will, so the error
    surfaces before the round trip. Returns the trimmed string as-is —
    the API still does the real parsing; this is a friendlier first pass.
    """
    try:
        Decimal(text.strip())
    except (InvalidOperation, AttributeError):
        return text
    return text.strip()
