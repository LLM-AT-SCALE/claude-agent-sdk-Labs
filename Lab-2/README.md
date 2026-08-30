# Lab 2 — DB Operations

An **insert-only** database application over three tables — `customer`,
`product` and `sales` — on PostgreSQL (Neon), driven two ways: forms, and a
chat that reaches the same API through tools.

> **SELECT and INSERT only. No UPDATE, no DELETE, anywhere.**
> A sale is a historical fact. Once recorded, its price and its time never
> change — not when the product's price changes, not ever.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LLM-AT-SCALE/claude-agent-sdk-Labs/blob/main/Lab-2/Lab_2.ipynb)

## What it does

| Mode | How you use it |
|---|---|
| **Manual** | Insert forms, list views, a joined `sales_detail` view, and a CSV loader that reports accepted and rejected rows separately |
| **AI** | Ask in plain language. Claude calls the API's own endpoints as tools — it has no way to write SQL |

Both modes reach the database through the same validated HTTP API, so every
guarantee below holds identically whichever one you use.

## Architecture

```
Streamlit (ui/)  →  FastAPI (api/)  →  SQLAlchemy (models/ + repository/)  →  Neon Postgres
```

| Layer | Rule |
|---|---|
| `db/` | `schema.sql` is the single source of truth. The only place a `CREATE TABLE` exists. |
| `models/` | SQLAlchemy mirrors of `schema.sql`. No I/O — a test fails if the two drift. |
| `repository/` | Every statement the application issues. All parameterized; no SQL is ever built by string formatting. |
| `api/` | Wires HTTP to `repository/`. Holds no SQL. |
| `ui/` | Streamlit. Talks to `api/` over HTTP only — never imports `repository/`. |

Inside `ui/`, each module has one job:

| Module | Job |
|---|---|
| `app.py` | The shell — page setup, connect screen, navigation |
| `views.py` | The Manual screens: forms, list views, the join view, CSV load |
| `chat.py` | AI mode: tool definitions and the agentic loop |
| `components.py` | Shared render pieces — tables, stat cards, section headers |
| `theme.py` | The stylesheet |
| `api_client.py` | Every HTTP call the UI makes |

## What the schema enforces

Not the application — the database:

- `line_total` is `GENERATED ALWAYS AS (quantity * unit_price) STORED`, so the
  application cannot disagree with it, and cannot write it at all
- `UNIQUE (customer_id, product_id, sold_at)` makes loading idempotent —
  re-running a file conflicts instead of doubling revenue
- `quantity > 0` and `unit_price >= 0` as CHECK constraints, refused by the
  database even if application validation is bypassed
- Money is `NUMERIC(12,2)` and `decimal.Decimal` — never a float
- `sold_at` comes from the input row. A sale with no timestamp is **rejected**,
  never defaulted to the current time

## The six reject reasons

`UNKNOWN_CUSTOMER` · `UNKNOWN_PRODUCT` · `MISSING_SOLD_AT` · `BAD_QUANTITY` ·
`BAD_UNIT_PRICE` · `DUPLICATE_SALE`

A rejected row is reported, never repaired. One row is one transaction, so a
rejection leaves nothing behind but a line in the report.

## Running it

In Colab, open the notebook badge above and run the cells in order.

Locally:

```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
python db/run.py                 # applies db/schema.sql then db/seed.sql
streamlit run app.py             # starts the API, then the UI
```

`app.py` starts the FastAPI backend as a child process so one command runs the
whole thing. To run the two separately in development:

```bash
uvicorn api.main:app --reload
streamlit run ui/app.py
```

The connection string is read from `DATABASE_URL`, or entered on the app's own
connect screen. It is never written to disk, never logged, and never echoed
back.

## Running the tests

```bash
export TEST_DATABASE_URL="$DATABASE_URL"
pytest
```

34 tests, covering schema fidelity, database-level constraint enforcement,
`line_total` correctness and unwritability, natural-key idempotence, `Decimal`
round-tripping, and a static check that nothing in `repository/` builds SQL by
string formatting.

## Sample data

`reference/` holds five CSVs. `sample-sales.csv` is the headline one: 24 rows,
16 that load and 8 built to be rejected, between them covering all six reject
reasons. `expected-results.json` holds the hand-verified figures each file
should produce — the known-good rows the validation steps check against.

## How it was built

This application was produced by the nine-prompt DB_Operations prompt pack —
define the problem, lock the scope, write the contract, write the build
prompt, build it, run it, validate it, measure it, accept it. The pack and
its design documents live with the pack, not here; this folder holds the
application that came out of it.

`doc/` builds the step-by-step guide to running the lab:

```bash
python doc/build_lab_pdf.py
```

## Disclaimer

For education. Not a production system — there is no authentication, and it
makes no promises about personal data.
