"""Declarative base shared by every model. No I/O lives in models/."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
