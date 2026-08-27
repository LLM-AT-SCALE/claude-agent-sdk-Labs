-- db/drop.sql
-- Tears the database down for a clean rebuild during development. The
-- application never invokes this itself. Order matters: sales references
-- customer and product.

DROP VIEW IF EXISTS sales_detail;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS customer;
