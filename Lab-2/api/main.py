"""FastAPI application: the only layer that reaches the database.

Wires HTTP requests to repository/ calls and translates between payloads and
repository inputs. Holds no SQL and no query-building logic of its own.

Two verbs only — POST to insert, GET to read. There is deliberately no PUT,
PATCH or DELETE route on any resource.
"""

from __future__ import annotations

import csv
import io
from typing import Iterator

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.schemas import (
    BatchResultOut,
    ConnectIn,
    ConnectOut,
    CustomerIn,
    CustomerOut,
    ProductIn,
    ProductOut,
    RejectedRowOut,
    SaleIn,
    SaleOut,
    SalesDetailOut,
    StatusOut,
)
from repository import customer_repository, product_repository, sales_repository
from repository.db import get_engine, new_session, reconfigure
from repository.errors import DuplicateNaturalKey, InvalidValue, SaleRejected

app = FastAPI(title="DB_Operations", version="1.0.0")


def get_session() -> Iterator[Session]:
    try:
        session = new_session()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    try:
        yield session
    finally:
        session.close()


@app.get("/admin/status", response_model=StatusOut)
def connection_status() -> StatusOut:
    try:
        get_engine()
    except RuntimeError:
        return StatusOut(connected=False)
    return StatusOut(connected=True)


@app.post("/admin/connect", response_model=ConnectOut)
def connect(payload: ConnectIn) -> ConnectOut:
    """The one place besides DATABASE_URL a connection string may arrive
    from — the UI's login screen. reconfigure() verifies the connection
    with a trivial query before swapping it in, so a bad string never
    disturbs a connection that was already working; the string itself is
    never echoed back, logged, or included in an error message
    (see repository/db.py).
    """
    try:
        reconfigure(payload.database_url)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not connect: {type(exc).__name__}. Check the connection "
            f"string and that db/schema.sql has been applied.",
        ) from exc
    return ConnectOut(connected=True)


@app.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(
    payload: CustomerIn, session: Session = Depends(get_session)
) -> CustomerOut:
    try:
        customer = customer_repository.insert_customer(
            session,
            full_name=payload.full_name,
            email=payload.email,
            country_code=payload.country_code,
            city=payload.city,
        )
        session.commit()
    except DuplicateNaturalKey as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidValue as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return CustomerOut.model_validate(customer)


@app.get("/customers", response_model=list[CustomerOut])
def list_customers(session: Session = Depends(get_session)) -> list[CustomerOut]:
    customers = customer_repository.list_customers(session)
    return [CustomerOut.model_validate(c) for c in customers]


@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductIn, session: Session = Depends(get_session)
) -> ProductOut:
    try:
        product = product_repository.insert_product(
            session,
            sku=payload.sku,
            name=payload.name,
            category=payload.category,
            unit_price=payload.unit_price,
            is_active=payload.is_active,
        )
        session.commit()
    except DuplicateNaturalKey as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidValue as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ProductOut.model_validate(product)


@app.get("/products", response_model=list[ProductOut])
def list_products(session: Session = Depends(get_session)) -> list[ProductOut]:
    products = product_repository.list_products(session)
    return [ProductOut.model_validate(p) for p in products]


@app.post("/sales", response_model=SaleOut, status_code=201)
def create_sale(payload: SaleIn, session: Session = Depends(get_session)) -> SaleOut:
    try:
        sale = sales_repository.insert_sale(
            session,
            customer_email=payload.customer_email,
            sku=payload.sku,
            quantity=payload.quantity,
            unit_price=payload.unit_price,
            sold_at=payload.sold_at,
        )
        session.commit()
    except SaleRejected as exc:
        raise HTTPException(
            status_code=422, detail={"reason": exc.reason.value, "detail": exc.detail}
        ) from exc
    return SaleOut.model_validate(sale)


@app.get("/sales", response_model=list[SaleOut])
def list_sales(session: Session = Depends(get_session)) -> list[SaleOut]:
    sales = sales_repository.list_sales(session)
    return [SaleOut.model_validate(s) for s in sales]


@app.get("/sales/detail", response_model=list[SalesDetailOut])
def sales_detail(session: Session = Depends(get_session)) -> list[SalesDetailOut]:
    rows = sales_repository.sales_detail(session)
    return [SalesDetailOut(**vars(row)) for row in rows]


@app.post("/sales/batch", response_model=BatchResultOut)
async def load_sales_batch(
    file: UploadFile, session: Session = Depends(get_session)
) -> BatchResultOut:
    raw = (await file.read()).decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(raw)))
    result = sales_repository.load_batch(session, rows)
    return BatchResultOut(
        rows_submitted=len(rows),
        accepted=[SaleOut.model_validate(s) for s in result.accepted],
        rejected=[
            RejectedRowOut(
                row_number=r.row_number, reason=r.reason.value, detail=r.detail
            )
            for r in result.rejected
        ],
        summed_line_total=result.summed_line_total,
    )
