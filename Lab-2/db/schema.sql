-- db/schema.sql
-- The single source of truth for this database, and the only place a
-- CREATE TABLE exists anywhere in this codebase. The SQLAlchemy models in
-- models/ mirror this file; they never generate or alter it, and a test
-- fails if the two drift apart.

CREATE TABLE customer (
    customer_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name    TEXT NOT NULL,
    email        TEXT NOT NULL,
    city         TEXT,
    country_code CHAR(2) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_customer_email UNIQUE (email),
    CONSTRAINT ck_customer_full_name_not_blank
        CHECK (length(btrim(full_name)) > 0),
    CONSTRAINT ck_customer_email_lower
        CHECK (email = lower(email)),
    CONSTRAINT ck_customer_email_format
        CHECK (email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'),
    CONSTRAINT ck_customer_country_code_format
        CHECK (country_code ~ '^[A-Z]{2}$')
);

CREATE TABLE product (
    product_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku         TEXT NOT NULL,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    unit_price  NUMERIC(12, 2) NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_product_sku UNIQUE (sku),
    CONSTRAINT ck_product_sku_format
        CHECK (sku ~ '^[A-Z0-9-]{4,32}$'),
    CONSTRAINT ck_product_name_not_blank
        CHECK (length(btrim(name)) > 0),
    CONSTRAINT ck_product_category_not_blank
        CHECK (length(btrim(category)) > 0),
    CONSTRAINT ck_product_unit_price_nonneg
        CHECK (unit_price >= 0)
);

CREATE INDEX ix_product_category ON product (category);

CREATE TABLE sales (
    sale_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customer (customer_id) ON DELETE RESTRICT,
    product_id  BIGINT NOT NULL REFERENCES product (product_id) ON DELETE RESTRICT,
    quantity    INTEGER NOT NULL,
    unit_price  NUMERIC(12, 2) NOT NULL,
    sold_at     TIMESTAMPTZ NOT NULL,
    line_total  NUMERIC(14, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED NOT NULL,
    CONSTRAINT ck_sales_quantity_positive
        CHECK (quantity > 0),
    CONSTRAINT ck_sales_unit_price_nonneg
        CHECK (unit_price >= 0),
    CONSTRAINT uq_sales_natural_key
        UNIQUE (customer_id, product_id, sold_at)
);

CREATE INDEX ix_sales_customer_id ON sales (customer_id);
CREATE INDEX ix_sales_product_id ON sales (product_id);
CREATE INDEX ix_sales_sold_at ON sales (sold_at);

-- The one read that spans all three tables. Ordered on
-- natural keys only; sale_id/customer_id/product_id never appear here.
CREATE VIEW sales_detail AS
SELECT
    s.sold_at,
    c.email     AS customer_email,
    c.full_name AS customer_full_name,
    p.sku       AS product_sku,
    p.name      AS product_name,
    p.category,
    s.quantity,
    s.unit_price,
    s.line_total
FROM sales s
JOIN customer c ON c.customer_id = s.customer_id
JOIN product p ON p.product_id = s.product_id
ORDER BY s.sold_at ASC, c.email ASC, p.sku ASC;
