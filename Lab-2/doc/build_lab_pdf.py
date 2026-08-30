"""Build the Lab 2 step-by-step guide as a PDF.

    python doc/build_lab_pdf.py

Follows the structure of the Lab 1 guide: cover, disclaimer and objective,
source-code organization, a summary of steps, a click-by-click Colab
walkthrough, a file-by-file code teardown, then how it all fits together and
what to take away.

Every code listing is read from the real source file at build time rather
than pasted here, so the guide cannot drift from the application it
documents. Screenshots are optional — until an image lands in doc/assets/,
each figure renders as a labelled placeholder naming what belongs there.
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import HexColor

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from codeshot import render_code  # noqa: E402
import layout  # noqa: E402
from layout import (  # noqa: E402
    CONTENT_W,
    INK,
    INK_SOFT,
    MARGIN_L,
    MARGIN_R,
    PAGE_H,
    PAGE_W,
    Doc,
)

ASSETS = HERE / "assets"
CODE_DIR = HERE / "code"
LAB = HERE.parent
REPO = "https://github.com/LLM-AT-SCALE/claude-agent-sdk-Labs"
NOTEBOOK = f"{REPO}/blob/main/Lab-2/Lab_2.ipynb"


# ------------------------------------------------------------ source access

def source(rel: str, first: int | None = None,
           between: tuple[str, str] | None = None,
           dedent: bool = False) -> str:
    """Return a listing read from the real file in the lab.

    Reading rather than pasting is deliberate: a listing copied into this
    script would drift the moment the code changed, and a guide that
    misquotes the code it documents is worse than no guide.
    """
    text = (LAB / rel).read_text(encoding="utf-8")
    lines = text.split("\n")

    if between is not None:
        start_marker, end_marker = between
        try:
            start = next(i for i, ln in enumerate(lines) if start_marker in ln)
        except StopIteration:
            raise LookupError(f"{rel}: start marker {start_marker!r} not found")
        rest = lines[start + 1:]
        if end_marker:
            try:
                offset = next(i for i, ln in enumerate(rest) if end_marker in ln)
            except StopIteration:
                raise LookupError(f"{rel}: end marker {end_marker!r} not found")
        else:
            # No end marker means "to the end of the file".
            offset = len(rest)
        lines = lines[start:start + 1 + offset]

    if first is not None:
        lines = lines[:first]

    if dedent:
        indents = [len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()]
        cut = min(indents) if indents else 0
        lines = [ln[cut:] if ln.strip() else ln for ln in lines]

    return "\n".join(lines).strip("\n")


# ---------------------------------------------------------------- figures

def figure(doc: Doc, name: str, caption: str, max_w: float | None = None) -> None:
    """Place a screenshot, or a labelled placeholder if it is not there yet.

    The placeholder keeps the page rhythm honest while the captures are
    still being taken, and names the file that belongs in the slot so the
    gap is obvious rather than silent.
    """
    for suffix in (".png", ".jpg", ".jpeg"):
        candidate = ASSETS / f"{name}{suffix}"
        if candidate.exists():
            doc.picture(candidate, caption=caption, max_w=max_w)
            return

    width = min(max_w or CONTENT_W, CONTENT_W)
    height = width * 0.44
    doc.need(height + 70)
    c = doc.c
    x = MARGIN_L + (CONTENT_W - width) / 2
    y = doc.y - height

    c.setFillColor(layout.CALLOUT_BG)
    c.rect(x, y, width, height, stroke=0, fill=1)
    c.setStrokeColor(layout.GREEN_DEEP)
    c.setLineWidth(1.2)
    c.setDash(6, 5)
    c.rect(x, y, width, height, stroke=1, fill=0)
    c.setDash()

    c.setFillColor(layout.GREEN_DEEP)
    c.setFont("Segoe-Bold", 15)
    c.drawCentredString(x + width / 2, y + height / 2 + 8, "SCREENSHOT")
    c.setFillColor(INK_SOFT)
    c.setFont("Mono", 13)
    c.drawCentredString(x + width / 2, y + height / 2 - 16, f"doc/assets/{name}.png")

    doc.y = y - 20
    doc.body(caption, size=13, colour=INK_SOFT, leading=20)


# ------------------------------------------------------------------- cover

def cover(doc: Doc) -> None:
    doc.new_page(chrome=False)
    c = doc.c

    paper = HexColor("#FAF9F5")
    ink = HexColor("#211F1B")
    accent = HexColor("#D97757")

    c.setFillColor(paper)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    field_top, field_h = PAGE_H - 300, 470
    c.setFillColor(ink)
    c.rect(0, field_top - field_h, PAGE_W, field_h, stroke=0, fill=1)

    # Three bands down the left edge, one per table the lab creates.
    for i, colour in enumerate(("#D97757", "#5E7A52", "#2C6480")):
        c.setFillColor(HexColor(colour))
        c.rect(0, field_top - field_h + i * (field_h / 3), 12, field_h / 3,
               stroke=0, fill=1)

    c.setFillColor(HexColor("#B9B2A2"))
    c.setFont("Segoe-Bold", 15)
    c.drawString(MARGIN_L, field_top - 74, "LAB TWO")

    c.setFillColor(HexColor("#FAF9F5"))
    c.setFont("Cambria-Bold", 74)
    c.drawString(MARGIN_L, field_top - 168, "DB Operations")
    c.setFont("Cambria-Bold", 44)
    c.drawString(MARGIN_L, field_top - 246, "An insert-only database")

    c.setFillColor(HexColor("#C9C2B2"))
    c.setFont("Segoe", 26)
    c.drawString(MARGIN_L, field_top - 372,
                 "Recording facts that never change, on Postgres")

    c.setFillColor(ink)
    c.setFont("Cambria-Bold", 30)
    c.drawString(MARGIN_L, 300, "Chetan Kumar M K")
    c.setFillColor(HexColor("#4A463C"))
    c.setFont("Segoe", 18)
    c.drawString(MARGIN_L, 262, "github.com/LLM-AT-SCALE/claude-agent-sdk-Labs")

    c.setStrokeColor(HexColor("#C2BAA5"))
    c.setLineWidth(1.2)
    c.line(MARGIN_L, 226, PAGE_W - MARGIN_R, 226)

    c.setFillColor(HexColor("#4A463C"))
    c.setFont("Segoe", 17)
    c.drawString(MARGIN_L, 186,
                 "PostgreSQL  ·  Neon  ·  FastAPI  ·  SQLAlchemy  ·  Streamlit  ·  Claude tool use")

    c.setFillColor(accent)
    c.rect(0, 0, PAGE_W / 3, 22, stroke=0, fill=1)
    c.setFillColor(HexColor("#5E7A52"))
    c.rect(PAGE_W / 3, 0, PAGE_W / 3, 22, stroke=0, fill=1)
    c.setFillColor(HexColor("#2C6480"))
    c.rect(2 * PAGE_W / 3, 0, PAGE_W / 3 + 1, 22, stroke=0, fill=1)


# ------------------------------------------- disclaimer and objective

def front_matter(doc: Doc) -> None:
    doc.new_page()
    doc.banner("Disclaimer", width=330)
    doc.body(
        "This document is intended only for internal use. The information contained in this "
        "document is confidential and should not be shared without prior authorization. As this "
        "document is shared for educational purposes only, there is a possibility that the steps "
        "in this document will not work in the user environment, and it is not a production-ready "
        "solution."
    )
    doc.space(14)

    doc.banner("Objective", width=330)
    doc.body(
        "Build and run an insert-only database application over three tables — customer, product "
        "and sales — hosted on Neon Postgres, and then use it two ways: through forms, and "
        "through a chat that reaches the same API as tools."
    )
    doc.space(8)
    doc.body(
        "One rule shapes everything: the application performs SELECT and INSERT only. Nothing in "
        "it may ever UPDATE or DELETE a row. A sale is a historical fact — once recorded, its "
        "price and its time never change, even when the product's price changes later."
    )
    doc.space(8)
    doc.body(
        "That constraint is what makes the lab checkable. An append-only table can be rebuilt "
        "from empty and compared against a previous run without ambiguity, which is exactly what "
        "the validation steps do — ten rebuilds, one expected result."
    )
    doc.space(14)

    doc.callout(
        "The guarantees live in the schema, not the application. A CHECK constraint holds against "
        "every client, including the ones nobody has written yet."
    )


# ------------------------------------------- source code organization

def source_organization(doc: Doc) -> None:
    doc.new_page()
    doc.heading("Source Code Organization")
    doc.space(6)

    doc.card_row([
        ("app.py",
         "The entry point. Starts the FastAPI backend as a child process, then hands over to the "
         "Streamlit UI, so one command runs the whole application behind a single tunnel."),
        ("db/",
         "schema.sql is the single source of truth for the database, and the only place a CREATE "
         "TABLE exists. seed.sql adds the reference rows, drop.sql tears it all down, and run.py "
         "applies them in order."),
    ])
    doc.card_row([
        ("models/",
         "SQLAlchemy mirrors of schema.sql — column definitions only, no I/O. A test fails if the "
         "models and the DDL ever drift apart."),
        ("repository/",
         "Every statement the application issues, and the only place any of them are issued. All "
         "parameterized through the SQLAlchemy expression API; no SQL is ever built by string "
         "formatting."),
    ])
    doc.card_row([
        ("api/",
         "FastAPI. Wires HTTP requests to repository/ calls and translates payloads. Holds no SQL "
         "and no query-building logic of its own."),
        ("ui/",
         "Streamlit, split by job: app.py is the shell, views.py the Manual screens, chat.py the "
         "AI one, components.py the shared render pieces, theme.py the stylesheet, and "
         "api_client.py every HTTP call. Nothing here imports repository/."),
    ])

    doc.space(10)
    doc.outlined_box("GitHub link:", REPO)


# ------------------------------------------------------ summary of steps

SUMMARY_STEPS = [
    ("OPEN THE NOTEBOOK IN COLAB",
     "Open the IPython notebook needed for this project.",
     "Start the deployment process by opening the provided notebook.",
     "Open Lab_2.ipynb on GitHub and load it in Google Colab through your browser."),
    ("CLONE THE LAB AND INSTALL DEPENDENCIES",
     "Bring the lab code into the Colab session.",
     "Fetch only the Lab-2 folder and install everything the lab needs.",
     "Run the first cell. It clones the repository and installs the Python packages."),
    ("PROVIDE YOUR NEON CONNECTION STRING",
     "Point the lab at a database.",
     "Give the lab somewhere to write, without putting the credential in a file.",
     "Create a free Neon project, copy the connection string, and paste it into the getpass "
     "prompt."),
    ("CREATE THE SCHEMA AND SEED IT",
     "Build the three tables the lab writes to.",
     "Apply the DDL that every guarantee in this lab rests on.",
     "Run the cell. It drops anything already there, applies schema.sql, then seeds the "
     "reference rows."),
    ("PROVE THE CONSTRAINTS ARE REAL",
     "Show that the database refuses bad data by itself.",
     "Confirm the rules hold even when the application is bypassed.",
     "Run the test suite. 34 tests, covering schema drift, CHECK enforcement, generated "
     "columns and Decimal precision."),
    ("LOAD A REAL FILE, TWICE",
     "Run a genuine CSV through the loader end to end.",
     "See the six reject reasons fire, then see the load prove itself idempotent.",
     "Run the loader cell, then run it again. The second pass adds zero rows."),
    ("RUN THE WEB APPLICATION",
     "Put both modes behind a browser.",
     "Open the application through an ngrok tunnel from Colab.",
     "Run the final cell, enter your ngrok authtoken, and open the printed URL."),
    ("USE THE APPLICATION",
     "Record and read data, by form and by chat.",
     "See the same guarantees hold whichever mode you use.",
     "Connect with your Neon string and Claude key, then work through Manual and AI mode."),
]


def summary_of_steps(doc: Doc) -> None:
    doc.new_page()
    doc.chevron("Summary of Steps Performed in the Document")
    doc.space(10)

    for n, (title, purpose, objective, action) in enumerate(SUMMARY_STEPS, start=1):
        doc.need(150)
        doc.heading(f"STEP {n}: {title}", size=19)
        doc.rich([("Purpose: ", True), (purpose, False)], size=14.5)
        doc.rich([("Objective: ", True), (objective, False)], size=14.5)
        doc.rich([("Action: ", True), (action, False)], size=14.5)
        doc.space(12)


# --------------------------------------------------------------- deployment

def deployment(doc: Doc) -> None:
    # Step 1
    doc.new_page()
    doc.grey_head("Step 1: Open the Notebook in Colab", size=24)
    doc.body(
        "Open the GitHub repository for this lab, go into the Lab-2 folder and click "
        "Lab_2.ipynb. Then click the Open in Colab badge at the top of the notebook."
    )
    doc.rich([("Repository: ", True), (REPO, False)], size=14.5)
    doc.space(8)
    doc.numbered([
        "Open the repository link in Chrome.",
        "Navigate to the Lab-2 folder.",
        "Click Lab_2.ipynb to preview it.",
        "Click the Open in Colab badge, as shown in the image below.",
    ])
    figure(doc, "colab_open", "The notebook on GitHub, with the Open in Colab badge.")

    # Step 2
    doc.new_page()
    doc.grey_head("Step 2: Clone the Lab and Install Dependencies", size=24)
    doc.body(
        "Run the first cell of the notebook. It removes any earlier copy of the lab, clones only "
        "the Lab-2 folder, and installs the Python packages — SQLAlchemy and psycopg 3 for the "
        "database, FastAPI and Streamlit for the application, anthropic for AI mode."
    )
    doc.space(6)
    doc.numbered([
        "Click the play button on the first cell to execute it.",
        "If you see a Restart session dialog, select Restart session, then run the cell again.",
        "The cell prints the commit it fetched, the three tables it will create, and the six "
        "reject reasons the loader can report. If those look right, you are running current code.",
    ])
    figure(doc, "colab_clone", "The first cell, after a successful run.")
    doc.callout(
        "The cell is safe to run again at any time. It starts by deleting the previous clone, "
        "which is what stops a second run from quietly working against stale code."
    )

    # Step 3
    doc.new_page()
    doc.grey_head("Step 3: Provide Your Neon Connection String", size=24)
    doc.body(
        "The database lives on Neon. Create a free project, open Connect, and copy the "
        "connection string. Paste it into the prompt the next cell raises."
    )
    doc.space(6)
    doc.body(
        "getpass hides what you type, so the connection string never appears in the notebook "
        "output and is never saved with the file. It is a credential — it carries the password "
        "for the database — and it is treated as one everywhere in this lab."
    )
    doc.space(6)
    doc.body(
        "Paste it exactly as Neon gives it. Providers hand out a plain postgres:// or "
        "postgresql:// string with no driver qualifier; the application normalises it to the "
        "psycopg 3 scheme itself rather than expecting you to know that detail."
    )
    figure(doc, "neon_connect", "The Connect dialog in the Neon console.", max_w=760)

    # Step 4
    doc.new_page()
    doc.grey_head("Step 4: Create the Schema and Seed It", size=24)
    doc.body(
        "db/schema.sql is the single source of truth for this database: the three tables, every "
        "CHECK constraint, both foreign keys, the unique natural key on sales, the generated "
        "line_total column and the four indexes."
    )
    doc.space(6)
    doc.body(
        "Nothing in the application issues DDL. There is no metadata.create_all(), no "
        "autogenerate and no migration framework — the SQLAlchemy models only mirror this file, "
        "and a test fails if the two drift apart."
    )
    doc.space(6)
    doc.body(
        "db/drop.sql runs first, so the cell is safe to re-run. On a fresh Neon project there is "
        "nothing to drop and it is a no-op."
    )
    figure(doc, "colab_schema", "The schema and seed applied, printed cell by cell.")

    # Step 5
    doc.new_page()
    doc.grey_head("Step 5: Prove the Constraints Are Real", size=24)
    doc.body(
        "This is the step that matters most, and the easiest one to skip. The suite does not "
        "check that the application refuses bad data — it checks that the database does, by "
        "writing straight past the application with raw parameterized SQL."
    )
    doc.space(6)
    doc.bullets([
        "Every model column matches schema.sql in name, type, nullability and default.",
        "quantity 0 and -1 are refused by the database, not merely by Python.",
        "line_total always equals quantity * unit_price, and cannot be written directly at all.",
        "The same natural key inserted twice raises rather than duplicating.",
        "A Decimal survives a round trip through NUMERIC with no drift.",
        "No statement in repository/ is built by string formatting.",
    ])
    figure(doc, "colab_tests", "34 passed. The constraints hold at the database level.")
    doc.callout(
        "If validation lived only in the application, anything reaching the database another way "
        "could still corrupt it. A CHECK constraint is a rule; a Python if-statement is a "
        "convention."
    )

    # Step 6
    doc.new_page()
    doc.grey_head("Step 6: Load a Real File, Twice", size=24)
    doc.body(
        "reference/sample-sales.csv holds 24 rows: 16 that must load and 8 built to be rejected, "
        "between them covering all six reject reasons. Run the loader and read which rows come "
        "back rejected, and why."
    )
    doc.space(6)
    doc.body(
        "Two of the rejections are duplicates of rows earlier in the same file. The natural key "
        "— customer_id, product_id and sold_at together — is what catches them."
    )
    figure(doc, "colab_load", "16 accepted, 8 rejected, each rejection naming its reason.")

    doc.space(4)
    doc.heading("Then run it again", size=22)
    doc.body(
        "The same file, a second time. Every row accepted before is now reported DUPLICATE_SALE. "
        "Rows rejected for another reason keep that reason, because they were never inserted and "
        "so cannot be duplicates of anything."
    )
    doc.space(6)
    doc.body(
        "Zero rows are added. That is idempotence, and it is a property of the schema rather than "
        "of the loader being careful — which is why it holds no matter what calls it."
    )
    figure(doc, "colab_reload", "The second pass. Nothing new goes in.")

    # Step 7
    doc.new_page()
    doc.grey_head("Step 7: Run the Web Application", size=24)
    doc.body(
        "The final cell opens an ngrok tunnel, starts the application behind it, and prints a "
        "public URL. Leave the cell running while you use the app; stopping it closes the tunnel."
    )
    doc.space(6)
    doc.body(
        "app.py starts the FastAPI backend as a child process and then hands over to Streamlit, "
        "so one command and one tunnel run both halves. The layer boundary is unchanged — the UI "
        "still reaches the database only through HTTP calls to the API."
    )
    doc.space(6)
    doc.body(
        "If you have not used ngrok before, sign up for a free account and copy your authtoken "
        "from the dashboard. The cell stops any server left over from an earlier run before it "
        "starts a new one. Without that, the port stays taken, the new server exits, and the "
        "tunnel keeps serving the old application."
    )
    figure(doc, "colab_ngrok", "The tunnel open and the application running behind it.")

    # Step 8
    doc.new_page()
    doc.grey_head("Step 8: Using the Application", size=24)
    doc.body(
        "Open the ngrok URL. The application asks for a Neon connection string and a Claude API "
        "key on its own connect screen, both masked. Neither is written to disk — they live in "
        "server-side session memory for as long as the browser session lasts, and no longer."
    )
    figure(doc, "app_connect", "The connect screen. Both fields are masked.")

    doc.space(4)
    doc.heading("Manual mode", size=22)
    doc.numbered([
        "Overview shows live counts and total revenue, read straight from the database.",
        "Add holds the three insert forms — customer, product and sale.",
        "Browse holds the three list views plus the joined sales_detail view.",
        "Import takes a CSV and reports accepted and rejected rows in separate tables, each "
        "rejection naming its reason.",
    ])
    figure(doc, "app_manual", "Manual mode, showing the joined sales_detail view.")

    doc.new_page()
    doc.heading("AI mode", size=22)
    doc.body(
        "The toggle at the top right switches to a chat over the same database. Ask it how many "
        "customers there are, what a given customer has bought, or to add a product."
    )
    doc.space(6)
    doc.body(
        "Claude reaches the database only through the API's own endpoints, handed to it as tools. "
        "It has no way to write SQL, so every guarantee in this lab still holds regardless of "
        "what it decides to do. Ask it to delete something and it will tell you it cannot — "
        "because nothing in the system can."
    )
    doc.space(6)
    doc.body(
        "It will not invent a value you did not give it. Ask it to record a sale without saying "
        "when, and it asks which moment you mean rather than defaulting to now — the same rule "
        "the loader enforces, expressed as a question."
    )
    figure(doc, "app_ai", "AI mode. Every tool call is named above the reply.")


# ------------------------------------------------------------ code teardown

FIRST_CODE_STEP = 9

CODE_SECTIONS = [
    (
        "Understanding requirements.txt",
        "This file lists every library the lab needs.",
        "requirements.txt",
        lambda: source("requirements.txt"),
        [
            ("sqlalchemy", "builds every statement the application issues, as expressions rather "
                           "than strings."),
            ("psycopg[binary]", "the PostgreSQL driver. Version 3, not psycopg2 — Neon's pooled "
                                "endpoint requires channel binding, which psycopg2 cannot do."),
            ("fastapi and uvicorn", "the API layer that owns all database access."),
            ("streamlit", "builds both interfaces, Manual and AI."),
            ("anthropic", "the Claude SDK, used by AI mode for tool use. Never used to build SQL."),
            ("pytest", "runs the suite that proves the constraints are real."),
        ],
    ),
    (
        "Understanding db/schema.sql",
        "The single source of truth. Every guarantee in this lab is written here.",
        "db/schema.sql",
        lambda: source("db/schema.sql", between=("CREATE TABLE sales", "CREATE INDEX ix_sales_customer_id")),
        [
            ("line_total", "is GENERATED ALWAYS AS (quantity * unit_price) STORED. The database "
                           "computes it, so the application cannot disagree with it — and cannot "
                           "write it at all."),
            ("uq_sales_natural_key", "makes every insert path idempotent. Replaying the same fact "
                                     "conflicts instead of doubling revenue."),
            ("ON DELETE RESTRICT", "blocks a delete from cascading. DELETE is out of scope "
                                   "entirely, so this is a second line of defence, not a "
                                   "permission."),
            ("The CHECK constraints", "quantity > 0 and unit_price >= 0 — enforced here so they "
                                      "hold against every client, not only this one."),
            ("sold_at", "is NOT NULL with no default. A sale with no timestamp is rejected, never "
                        "stamped with the current time."),
        ],
    ),
    (
        "Understanding db/run.py",
        "This file applies the SQL scripts, and is the only thing in the lab that does.",
        "db/run.py",
        lambda: source("db/run.py", between=("def _for_psycopg", "def main")),
        [
            ("The connection string", "is read from DATABASE_URL, or prompted for with getpass. "
                                      "It is never printed, never logged and never committed."),
            ("_for_psycopg", "strips the +psycopg driver qualifier. SQLAlchemy understands it; "
                             "psycopg's own connect() does not, so one DATABASE_URL value has to "
                             "work for both."),
            ("Each file is applied whole", "and committed before the next one, so a failure "
                                           "leaves a clear boundary rather than a half-applied "
                                           "schema."),
        ],
    ),
    (
        "Understanding models/sales.py",
        "The SQLAlchemy mirror of the sales table. Column definitions only — no I/O.",
        "models/sales.py",
        lambda: source("models/sales.py", between=("class Sale", None)),
        [
            ("Computed(persisted=True)", "documents that the database owns line_total. The model "
                                         "declares it so the schema-drift test can compare them, "
                                         "and the application never assigns it."),
            ("Numeric(12, 2)", "maps to decimal.Decimal in Python. Never float — binary floating "
                               "point cannot hold 0.10 exactly, and a total that drifts by a cent "
                               "is a defect."),
            ("Identity(always=True)", "the surrogate key is generated by the database. It is "
                                      "never used in an ordering or a report, because it is not "
                                      "stable across a rebuild."),
        ],
    ),
    (
        "Understanding repository/db.py",
        "The only place in the application a connection string is read.",
        "repository/db.py",
        lambda: source("repository/db.py", between=("def _normalize_scheme", "def get_engine")),
        [
            ("_normalize_scheme", "upgrades a bare postgres:// or postgresql:// to the psycopg 3 "
                                  "scheme. Every provider hands out the plain form, so the "
                                  "application accepts what you were actually given."),
            ("connect_timeout", "keeps a bad host from hanging the connect attempt for minutes. "
                                "It fails fast and says so instead."),
            ("reconfigure", "verifies a new connection string before swapping it in, so a typo "
                            "never disturbs a connection that was already working."),
        ],
    ),
    (
        "Understanding repository/sales_repository.py",
        "The validation pipeline. Every sale, from either surface, comes through here.",
        "repository/sales_repository.py",
        lambda: source("repository/sales_repository.py",
                       between=("def submit_sale", "sale = Sale(")),
        [
            ("One pipeline, one order", "customer, product, sold_at, quantity, unit_price, then "
                                        "the insert. A row with more than one problem is always "
                                        "reported by whichever check comes first."),
            ("Both surfaces funnel through it", "the API and the CSV loader call the same "
                                                "function, so a row is judged identically "
                                                "however it arrived."),
            ("Rejection, never repair", "a failing row raises with one of the six reasons. The "
                                        "insert runs inside a savepoint, so a rejection leaves "
                                        "nothing behind but a line in the report."),
            ("Lookups, never creation", "an unknown email or SKU is rejected. The loader never "
                                        "creates a customer or a product implicitly."),
        ],
    ),
    (
        "Understanding api/main.py",
        "The HTTP surface. It wires requests to repository/ and holds no SQL.",
        "api/main.py",
        lambda: source("api/main.py", between=("@app.post(\"/sales\"", "@app.get(\"/sales\"")),
        [
            ("Two verbs only", "POST to insert, GET to read. There is no PUT, no PATCH and no "
                               "DELETE route anywhere in the API, on any resource."),
            ("SaleRejected becomes 422", "carrying the reject reason as structured JSON, so the "
                                         "caller sees which of the six rules it broke."),
            ("The session is a dependency", "opened per request and closed in a finally block. "
                                            "Before a database is connected it returns 503 rather "
                                            "than crashing."),
        ],
    ),
    (
        "Understanding ui/chat.py",
        "AI mode. Claude gets tools over the API — never a database connection.",
        "ui/chat.py",
        lambda: source("ui/chat.py", between=("SYSTEM_PROMPT = ", "TOOLS = [")),
        [
            ("The tools are API endpoints", "one per insert and one per read. Claude cannot write "
                                            "SQL because it is never given anything that would "
                                            "run it — every safety rule in this lab therefore "
                                            "still holds."),
            ("Never invent a value", "no email, no SKU, no price and above all no timestamp. "
                                     "Anything ambiguous comes back as one specific question."),
            ("The agentic loop is manual", "request, execute the tool calls, feed the results "
                                           "back, repeat until Claude stops asking for tools."),
            ("Conversations are kept", "each titled from its first message and switchable from "
                                       "the sidebar, with the full transcript preserved."),
        ],
    ),
    (
        "Understanding tests/test_line_total.py",
        "One test out of thirty-four, chosen because it shows the shape of all of them.",
        "tests/test_line_total.py",
        lambda: source("tests/test_line_total.py",
                       between=("def test_line_total_cannot_be_written_directly", None)),
        [
            ("It writes raw SQL on purpose", "bypassing the application entirely. The point is "
                                             "to prove the database refuses this, not that the "
                                             "application avoids it."),
            ("GeneratedAlways is the expected error", "Postgres will not accept a value for a "
                                                      "generated column at all, which is a "
                                                      "stronger guarantee than any check the "
                                                      "application could make."),
            ("Every test cleans up by rollback", "never by DELETE. The no-DELETE rule applies to "
                                                 "the test suite as much as to the application."),
        ],
    ),
]


def code_teardown(doc: Doc) -> None:
    for n, (title, intro, filename, code_fn, explanation) in enumerate(
            CODE_SECTIONS, start=FIRST_CODE_STEP):
        code = code_fn()
        # Only call it an excerpt when it actually is one — comparing against
        # the file on disk keeps the label honest without a flag to maintain.
        whole = (LAB / filename).read_text(encoding="utf-8").strip("\n")
        label = filename if code.strip() == whole.strip() else f"{filename}  (excerpt)"

        doc.new_page()
        doc.grey_head(f"Step {n}: {title}", size=23)
        doc.body(intro)
        doc.body(f"File: {label}", font="Mono", size=14, colour=INK_SOFT)
        doc.code_block(filename.replace("/", "_").replace(".", "_"), code)

        doc.need(140)
        doc.heading("Explanation:", size=24)
        doc.numbered([f"{bold} {rest}" for bold, rest in explanation])


# --------------------------------------------------------- how it works

def how_it_works(doc: Doc) -> None:
    step = FIRST_CODE_STEP + len(CODE_SECTIONS)

    doc.new_page()
    doc.grey_head(f"Step {step}: How Everything Works Together", size=24)

    doc.heading("Recording a sale, through the form", size=21)
    doc.numbered([
        "The user opens the application; app.py starts the API and then the UI.",
        "They connect with a Neon connection string, which api/ verifies before accepting.",
        "They fill in the sale form — customer email, SKU, quantity, price and the moment it "
        "happened.",
        "ui/ POSTs that to api/, over HTTP. It has no other route to the database.",
        "api/ hands the values to repository/, which resolves the customer by email and the "
        "product by SKU.",
        "repository/ validates in order, then inserts inside a savepoint.",
        "The database computes line_total, enforces the CHECK constraints, and rejects a "
        "duplicate natural key.",
        "The row comes back, or one of six reject reasons does.",
    ])

    doc.space(10)
    doc.heading("Recording a sale, through the chat", size=21)
    doc.numbered([
        "The user types what happened in plain language.",
        "ui/chat.py sends the conversation to Claude, with the API's endpoints described as "
        "tools.",
        "Claude asks for anything missing rather than inventing it — above all the timestamp.",
        "When it has everything, it calls the record_sale tool.",
        "chat.py turns that tool call into exactly the same HTTP POST the form makes.",
        "From there the path is identical — api/, repository/, the database, the same six "
        "reject reasons.",
    ])

    doc.space(10)
    doc.callout(
        "The two paths converge at the API. That is the whole design: AI mode is safe not "
        "because the model is careful, but because it cannot reach anything the form could not."
    )


# ----------------------------------------------------------------- summary

def summary(doc: Doc) -> None:
    doc.new_page()
    doc.heading("What to Take Away")
    doc.space(8)

    doc.heading("Put the guarantee in the database", size=21)
    doc.body(
        "A CHECK constraint holds against every client, including the ones nobody has written "
        "yet. Validation in Python alone is a convention; validation in the schema is a rule. "
        "The test suite proves the difference by writing raw SQL straight past the application "
        "and watching the database refuse it anyway."
    )
    doc.space(10)

    doc.heading("Append-only makes correctness checkable", size=21)
    doc.body(
        "Because nothing is ever updated or deleted, the same input always produces the same "
        "database. That is what lets the lab rebuild from empty ten times and compare the results "
        "exactly — one row count, one total, one hash of the joined view."
    )
    doc.space(10)

    doc.heading("Money is NUMERIC, never a float", size=21)
    doc.body(
        "Binary floating point cannot represent 0.10 exactly. A total that drifts by a cent is a "
        "defect, not a rounding style — so money is NUMERIC in the database and decimal.Decimal "
        "in Python, end to end."
    )
    doc.space(10)

    doc.heading("A recorded fact keeps its own values", size=21)
    doc.body(
        "The price on a sale is copied onto the row, not read back through the product. Changing "
        "a price today must not rewrite what happened last year — so a sale priced differently "
        "from its product's current price is correct input, not an error."
    )
    doc.space(10)

    doc.heading("Give a model tools, not a database", size=21)
    doc.body(
        "AI mode is useful precisely because it cannot do anything a form could not. The safety "
        "lives in the layer underneath, where it holds regardless of what the model decides — "
        "which is a better place for it than in the model's instructions."
    )
    doc.space(10)

    doc.heading("Never hardcode a credential", size=21)
    doc.body(
        "The notebook prompts with getpass, the application with a password field. Neither the "
        "connection string nor the API key is written to disk, logged, or committed. The "
        ".gitignore blocking .env files is the second line of defence; the first is that nothing "
        "in the code ever looks for one."
    )


# -------------------------------------------------------------------- main

def _attach_code_block(doc_cls) -> None:
    """Give Doc a code_block() that renders and places a code screenshot."""

    def code_block(self, name: str, code: str) -> None:
        path = render_code(code, CODE_DIR / f"{name}.png")
        self.picture(path, max_w=CONTENT_W)

    doc_cls.code_block = code_block


def _parse_args():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=["bootcamp", "original", "dboperations"],
                    default="dboperations")
    ap.add_argument("--out", default=None)
    return ap.parse_args()


def main() -> int:
    args = _parse_args()
    layout.apply_theme(args.theme)
    _attach_code_block(Doc)
    CODE_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    out = Path(args.out) if args.out else HERE / "Lab-2_DB_Operations.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = Doc(out, ASSETS)
    doc.c.setTitle("Lab 2 - DB Operations")

    cover(doc)
    front_matter(doc)
    source_organization(doc)
    summary_of_steps(doc)
    deployment(doc)
    code_teardown(doc)
    how_it_works(doc)
    summary(doc)

    doc.save()
    print(f"wrote {out}  ({doc.page} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
