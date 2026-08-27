"""Every model column matches db/schema.sql in name, type, nullability,
and default. If the two ever drift, this test is the one that fails
the suite exists to catch.
"""

from __future__ import annotations

import pytest
from sqlalchemy import inspect

from models import Customer, Product, Sale
from tests.conftest import requires_database

MODELS = [Customer, Product, Sale]


def _model_columns_by_name(model):
    return {col.name: col for col in model.__table__.columns}


@requires_database
@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__tablename__)
def test_column_names_match(engine, model):
    inspector = inspect(engine)
    reflected = {c["name"] for c in inspector.get_columns(model.__tablename__)}
    modeled = set(_model_columns_by_name(model).keys())
    assert reflected == modeled, (
        f"{model.__tablename__}: schema.sql has {reflected}, "
        f"model has {modeled}"
    )


@requires_database
@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__tablename__)
def test_column_nullability_matches(engine, model):
    inspector = inspect(engine)
    reflected = {c["name"]: c["nullable"] for c in inspector.get_columns(model.__tablename__)}
    for name, column in _model_columns_by_name(model).items():
        assert reflected[name] == column.nullable, (
            f"{model.__tablename__}.{name}: schema.sql nullable="
            f"{reflected[name]}, model nullable={column.nullable}"
        )


@requires_database
@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__tablename__)
def test_column_types_match(engine, model):
    inspector = inspect(engine)
    reflected = {c["name"]: c["type"] for c in inspector.get_columns(model.__tablename__)}
    for name, column in _model_columns_by_name(model).items():
        reflected_ddl = reflected[name].compile(dialect=engine.dialect)
        model_ddl = column.type.compile(dialect=engine.dialect)
        assert reflected_ddl == model_ddl, (
            f"{model.__tablename__}.{name}: schema.sql type={reflected_ddl}, "
            f"model type={model_ddl}"
        )


@requires_database
def test_identity_columns_match(engine):
    inspector = inspect(engine)
    for model, pk_name in (
        (Customer, "customer_id"),
        (Product, "product_id"),
        (Sale, "sale_id"),
    ):
        reflected = {c["name"]: c for c in inspector.get_columns(model.__tablename__)}
        assert "identity" in reflected[pk_name], (
            f"{model.__tablename__}.{pk_name} is not an IDENTITY column in "
            "schema.sql, but the model declares one"
        )


@requires_database
def test_sales_line_total_is_generated(engine):
    inspector = inspect(engine)
    columns = {c["name"]: c for c in inspector.get_columns("sales")}
    assert "computed" in columns["line_total"], (
        "sales.line_total must be a GENERATED ALWAYS AS ... STORED column "
        "in schema.sql, matching the model's Computed() mapping"
    )


@requires_database
def test_server_defaults_present_where_modeled(engine):
    inspector = inspect(engine)
    for model, name in (
        (Customer, "created_at"),
        (Product, "created_at"),
        (Product, "is_active"),
    ):
        reflected = {c["name"]: c for c in inspector.get_columns(model.__tablename__)}
        assert reflected[name]["default"] is not None, (
            f"{model.__tablename__}.{name} has a server_default in the "
            "model but no default in schema.sql"
        )
