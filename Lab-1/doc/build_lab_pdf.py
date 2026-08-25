"""Build the Lab 1 step-by-step guide as a PDF.

    python doc/build_lab_pdf.py

Follows the structure of the existing bootcamp documents: cover, disclaimer
and objective, source-code organization, a click-by-click deployment
walkthrough, a file-by-file code teardown with explanations, then how it all
fits together and what was learned.

Screenshots are reused from the existing bootcamp document as placeholders —
swap the files in doc/assets/ for your own captures.
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from codeshot import render_code  # noqa: E402
import layout  # noqa: E402
from layout import (  # noqa: E402
    CONTENT_W,
    find_asset,
    INK,
    INK_SOFT,
    MARGIN_L,
    PAGE_H,
    PAGE_W,
    WHITE,
    Doc,
)

def original_cover(doc, lab_line: str, title_lines: list, subtitle: str) -> None:
    """A cover drawn from scratch - no borrowed photography, logos or marks.

    Uses the application's own palette so the document and the software it
    documents read as one thing.
    """
    from layout import PAGE_H, PAGE_W, MARGIN_L, MARGIN_R
    doc.new_page(chrome=False)
    c = doc.c

    paper = HexColor("#F5F2EA")
    ink = HexColor("#17150F")
    c.setFillColor(paper)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # A broad ink field for the title to sit on, with the decision colours
    # from the application running down its left edge.
    field_top, field_h = PAGE_H - 300, 470
    c.setFillColor(ink)
    c.rect(0, field_top - field_h, PAGE_W, field_h, stroke=0, fill=1)
    for i, colour in enumerate(("#2E6F45", "#2C6480", "#8F5C0B", "#9B2C2C")):
        c.setFillColor(HexColor(colour))
        c.rect(0, field_top - field_h + i * (field_h / 4), 12, field_h / 4,
               stroke=0, fill=1)

    c.setFillColor(HexColor("#B9B2A2"))
    c.setFont("Segoe-Bold", 15)
    c.drawString(MARGIN_L, field_top - 74, lab_line.upper())

    c.setFillColor(HexColor("#F5F2EA"))
    c.setFont("Cambria-Bold", 74)
    for i, line in enumerate(title_lines):
        c.drawString(MARGIN_L, field_top - 168 - i * 84, line)

    c.setFillColor(HexColor("#C9C2B2"))
    c.setFont("Segoe", 26)
    c.drawString(MARGIN_L, field_top - 372, subtitle)

    # Author block
    c.setFillColor(ink)
    c.setFont("Cambria-Bold", 30)
    c.drawString(MARGIN_L, 300, "Chetan Kumar M K")
    c.setFillColor(HexColor("#4A463C"))
    c.setFont("Segoe", 18)
    c.drawString(MARGIN_L, 262, "github.com/chetankumarmk56/Claude-Agentic-SDK-Labs")

    c.setStrokeColor(HexColor("#C2BAA5"))
    c.setLineWidth(1.2)
    c.line(MARGIN_L, 226, PAGE_W - MARGIN_R, 226)

    c.setFillColor(HexColor("#4A463C"))
    c.setFont("Segoe", 17)
    c.drawString(MARGIN_L, 186, "Claude Agent SDK  ·  Messages API  ·  Python  ·  Streamlit")

    for i, colour in enumerate(("#2E6F45", "#2C6480", "#9B2C2C")):
        c.setFillColor(HexColor(colour))
        c.rect(i * (PAGE_W / 3), 0, PAGE_W / 3 + 1, 22, stroke=0, fill=1)


ASSETS = HERE / "assets"
CODE_DIR = HERE / "code"
LAB = HERE.parent
REPO = "https://github.com/chetankumarmk56/Claude-Agentic-SDK-Labs"


# --------------------------------------------------------------------- cover

def cover(doc: Doc) -> None:
    doc.new_page(chrome=False)
    c = doc.c

    background = find_asset(ASSETS, "cover_bg.png")
    if background:
        c.drawImage(ImageReader(str(background)), 0, 0, PAGE_W, PAGE_H, mask="auto")

    # Paint over the two text panels of the source cover and set our own.
    # The panel has to be fully opaque: at any transparency the original
    # title bleeds through and, because ours says much the same thing, it
    # reads as doubled text. #2E63B4 sits inside the surrounding gradient.
    c.setFillColor(HexColor("#2E63B4"))
    c.roundRect(102, PAGE_H - 664, 934, 294, 10, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#6FA3DC"))
    c.setLineWidth(1.6)
    c.roundRect(102, PAGE_H - 664, 934, 294, 10, stroke=1, fill=0)

    c.setFillColor(WHITE)
    c.setFont("Segoe-Bold", 62)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 456, "Generative AI for Schools")
    c.setFont("Segoe", 40)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 528, "Creating Agents to Solve")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 580, "Industrial Challenges")

    c.setFillColor(WHITE)
    c.roundRect(117, PAGE_H - 916, 904, 166, 8, stroke=0, fill=1)
    c.setFillColor(HexColor("#0F6B4F"))
    c.setFont("Segoe-Bold", 44)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 818, "LAB ONE")
    c.setFillColor(HexColor("#2A2A2A"))
    c.setFont("Segoe-Bold", 34)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 884, "Loan Application Evaluation")


# ------------------------------------------------- disclaimer and objective

def front_matter(doc: Doc) -> None:
    doc.new_page()

    doc.banner("Disclaimer", width=300)
    doc.body(
        "This document is intended only for internal use. The information contained in "
        "this document is confidential and should not be shared without prior "
        "authorization. As this document is shared for educational purposes only, there "
        "is a possibility that the steps in this document will not work in the user "
        "environment, and it is not a production-ready solution."
    )
    doc.space(20)

    doc.banner("Objective", width=300)
    doc.body(
        "Score a commercial loan application against the Five C's of Credit using two "
        "different Claude surfaces, so the difference between them is visible side by "
        "side. Part A answers the question with a single Messages API call. Part B hands "
        "the same application to an agent built on the Claude Agent SDK, which reads the "
        "files, works through the rubric and writes a credit memo itself."
    )
    doc.space(20)

    doc.banner("Prerequisites", width=340)
    doc.body(
        "The solution runs entirely in Google Colab, so nothing is installed on your own "
        "machine. It is strongly recommended that participants have all of the following "
        "in place before the session."
    )
    doc.space(6)
    doc.bullets([
        "Google Account (ex: GMAIL)",
        "Chrome Browser",
        "Google Colab",
        "An Anthropic API key — console.anthropic.com",
        "An ngrok authtoken (free) — dashboard.ngrok.com",
    ])

    doc.space(10)
    doc.callout(
        "Your Anthropic API key is requested at run time. It is never written into the "
        "notebook, never committed to the repository, and never stored on disk."
    )


# ------------------------------------------------- source code organization

def source_organization(doc: Doc) -> None:
    doc.new_page()
    doc.running_head("LOAN APPLICATION EVALUATION"
                     if layout.THEME == "original"
                     else "GEN AI BOOTCAMP FOR ENTERPRISE ENABLEMENT")

    doc.grey_head("Source Code Organization", size=26)
    doc.card_row([
        ("app.py", "This script is the entry point. It sets the page configuration and "
                   "calls the main() function from src/main.py, which builds the whole "
                   "interface."),
        ("src/main.py", "This script drives the application. It prompts for the API key, "
                        "reads the uploaded application, and renders Part A and Part B "
                        "in their own tabs."),
    ])
    doc.card_row([
        ("src/model.py", "Part A. Sends one Messages API call carrying the rubric and the "
                         "narrative, and receives the five scores back as structured JSON."),
        ("src/agent.py", "Part B. Runs the Claude Agent SDK over a working folder so the "
                         "agent can read the rubric, read the application and write the memo."),
    ])
    doc.space(6)
    doc.outlined_box("GitHub link:", f"{REPO}/tree/main/Lab-1")

    doc.new_page()
    doc.chevron("Summary of Steps Performed in the Document")
    doc.space(10)

    steps = [
        ("STEP 1: OPEN THE IPYTHON NOTEBOOK",
         "Open the IPython notebook needed for this project.",
         "Start the deployment process by opening the provided notebook.",
         "Open the .ipynb file on GitHub and load it in Google Colab through your browser."),
        ("STEP 2: CLONE THE LAB AND INSTALL DEPENDENCIES",
         "Bring the lab code into the Colab session.",
         "Fetch only the Lab-1 folder and install everything the lab needs.",
         "Run the first cell. It clones the repository, installs the Python packages and "
         "installs the Claude Code CLI that the Agent SDK drives."),
        ("STEP 3: PROVIDE YOUR ANTHROPIC API KEY",
         "Authenticate against the Claude API.",
         "Supply the key at run time rather than storing it anywhere.",
         "Run the getpass cell and paste your key. Nothing is echoed to the screen."),
        ("STEP 4: SCORE THE APPLICATION WITH THE MESSAGES API",
         "See a single, fully specified call do the whole job.",
         "Understand when one API call is the right tool.",
         "Run the Part A cells and read the returned JSON and the weighted total."),
        ("STEP 5: HAND THE SAME APPLICATION TO AN AGENT",
         "See the Claude Agent SDK drive its own steps.",
         "Understand what an agent adds, and what it costs.",
         "Run the Part B cell and watch the tool calls as the agent works."),
        ("STEP 6: RUN THE WEB APPLICATION",
         "Use both parts through a browser interface.",
         "Deploy the Streamlit application and open it over ngrok.",
         "Run the final cell and open the printed URL."),
        ("STEP 7: USE THE APPLICATION",
         "Score a real application end to end.",
         "See the decision, the score and the hard rule in the interface.",
         "Open the ngrok URL, enter your key, choose an application and read the result."),
    ]

    for title, purpose, objective, action in steps:
        doc.grey_head(title, size=19)
        doc.rich([("Purpose: ", True), (purpose, False)], indent=26)
        doc.rich([("Objective: ", True), (objective, False)], indent=26)
        doc.rich([("Action: ", True), (action, False)], indent=26)
        doc.space(14)


# ------------------------------------------------------------- deployment

def deployment(doc: Doc) -> None:
    doc.new_page()
    doc.grey_head("Step 1: Open the IPython Notebook", size=24)
    doc.body(
        "Open the GitHub repository for this lab, go into the Lab-1 folder and click "
        "Lab_1.ipynb. Then click the Open in Colab badge at the top of the notebook."
    )
    doc.body(f"Repository: {REPO}", font="Mono", size=14, colour=INK_SOFT)
    doc.numbered([
        "Open the repository link in Chrome.",
        "Navigate to the Lab-1 folder.",
        "Click Lab_1.ipynb to preview it.",
        "Click the Open in Colab badge, as shown in the image below.",
    ])
    doc.picture(ASSETS / "colab_open.jpeg")

    doc.new_page()
    doc.grey_head("Step 2: Clone the Lab and Install Dependencies", size=24)
    doc.body(
        "Run the first cell of the notebook. It removes any earlier copy of the lab, "
        "clones only the Lab-1 folder, installs the Python packages, and installs the "
        "Claude Code CLI, which the Agent SDK in Part B runs as a subprocess."
    )
    doc.body("2.1. Click the play button on the first cell to execute it.")
    doc.picture(ASSETS / "colab_run_cell.jpeg")
    doc.space(6)
    doc.body(
        "2.2. While executing, if you see a “Restart session” dialog box as shown "
        "in the image below, select “Restart session” to proceed, then run the "
        "cell again."
    )
    if layout.THEME != "original":
        doc.picture(ASSETS / "colab_restart.jpeg")

    doc.new_page()
    doc.body(
        "2.3. While executing the cell, you will see the project folder and files in the "
        "Files section of Colab, as shown in the image below."
    )
    doc.picture(ASSETS / "colab_files.jpeg", max_w=640)
    doc.space(6)
    doc.callout(
        "The cell prints the commit it fetched, the file types the uploader accepts and "
        "the Claude Code CLI version. If those three lines look right, you are running "
        "current code. The cell is safe to run again at any time."
    )

    doc.new_page()
    doc.grey_head("Step 3: Provide Your Anthropic API Key", size=24)
    doc.body(
        "The key is requested at run time. getpass hides what you type, so the key never "
        "appears in the notebook output and is never saved with the file."
    )
    doc.code_block(
        "apikey",
        '''import os, getpass

os.environ["ANTHROPIC_API_KEY"] = getpass.getpass("Enter your Anthropic API key: ")
print("Key stored for this session only.")''',
    )
    doc.body(
        "Run the next cell to check the key before the lab spends any tokens. You should "
        "see Valid API Key!"
    )

    doc.new_page()
    doc.grey_head("Step 6: Run the Web Application", size=24)
    doc.body(
        "The final cell opens an ngrok tunnel, starts the Streamlit application behind "
        "it, and prints a public URL. Leave the cell running while you use the app; "
        "stopping it closes the tunnel."
    )
    doc.body(
        "If you have not used ngrok before, sign up for a free account and copy your "
        "authtoken from the dashboard."
    )
    if layout.THEME != "original":
        doc.picture(ASSETS / "ngrok_login.jpeg", max_w=520)
    doc.space(6)
    doc.callout(
        "The cell stops any server left over from an earlier run before it starts a new "
        "one. Without that, the port stays taken, the new server exits, and the tunnel "
        "keeps serving the old application — which looks like the page hanging on "
        "“Please wait…” with no explanation."
    )

    doc.new_page()
    doc.grey_head("Step 7: Using the Application", size=24)
    doc.body(
        "Open the ngrok URL. Enter your Anthropic API key in the password field, choose "
        "a sample application or upload your own, then work through the two tabs."
    )
    doc.picture(ASSETS / "app_result.png")
    doc.space(4)
    doc.numbered([
        "Part A scores the application in one Messages API call and shows the decision, "
        "the weighted score, and the arithmetic that produced it.",
        "The decision panel names the outcome. Here the application scored 52, but the "
        "decision is DECLINE rather than the band that 52 would fall into.",
        "That is hard rule HR-1: Capacity scored 1, because DSCR is below 1.00x. A loan "
        "that cannot cover its own debt service is not rescued by good collateral, so "
        "the rule overrides the weighted total.",
        "Part B hands the same application to the Claude Agent SDK, which reads the "
        "rubric and the narrative itself and writes a credit memo you can download.",
    ])


# --------------------------------------------------------- code teardown

CODE_SECTIONS = [
    (
        "Step 8: Understanding requirements.txt",
        "This file lists every library the lab needs.",
        "requirements.txt",
        """anthropic==1.0.0
claude-agent-sdk==0.2.144
streamlit==1.50.0
pandas==2.2.2
python-docx==1.1.2
pypdf==5.1.0""",
        [
            ("anthropic", "the official SDK for the Claude API, used by Part A."),
            ("claude-agent-sdk", "the Claude Agent SDK, used by Part B."),
            ("streamlit", "builds the web interface."),
            ("python-docx and pypdf", "read the uploaded Word and PDF applications."),
        ],
    ),
    (
        "Step 9: Understanding src/validate.py",
        "This file checks the API key before the lab spends anything.",
        "src/validate.py",
        """import anthropic

VALIDATION_MODEL = "claude-haiku-4-5"


def validate_anthropic_key(api_key: str) -> str:
    \"\"\"Return "Valid API Key!" or a message explaining why it was rejected.\"\"\"
    if not api_key or not api_key.strip():
        return "Invalid - please enter your Anthropic API key."

    try:
        client = anthropic.Anthropic(api_key=api_key.strip())
        client.messages.create(
            model=VALIDATION_MODEL,
            max_tokens=1,
            messages=[{"role": "user", "content": "ping"}],
        )
        return "Valid API Key!"

    except anthropic.AuthenticationError:
        return "Invalid API Key - the key was rejected by Anthropic."
    except anthropic.RateLimitError:
        return "Valid API Key!"
    except anthropic.APIConnectionError:
        return "Invalid - could not reach the Anthropic API." """,
        [
            ("The function verifies the given Anthropic API key",
             "by making one very small test request."),
            ("If valid, it lets you into the application;",
             "otherwise it returns a message naming the reason."),
            ("A rate-limit error still counts as valid",
             "— the key itself is fine, the account is simply busy."),
        ],
    ),
    (
        "Step 10: Understanding src/ingestion.py",
        "This file reads the application out of whatever file was uploaded.",
        "src/ingestion.py",
        """SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".txt")
MIN_USABLE_CHARS = 200


def extract_text(filename: str, data: bytes) -> str:
    \"\"\"Return the narrative held in the uploaded file.\"\"\"
    if not data:
        raise UnreadableDocument("That file is empty.")

    suffix = PurePosixPath(filename.replace("\\\\", "/")).suffix.lower()
    parser = _PARSERS.get(suffix)

    if parser is None:
        raise UnreadableDocument(f"'{filename}' is not a supported format.")

    text = parser(data).strip()

    if len(text) < MIN_USABLE_CHARS:
        raise UnreadableDocument(
            "No readable text was found in that document. If it is a scanned "
            "PDF, this lab cannot read it - there is no OCR step."
        )

    return text""",
        [
            ("A loan application arrives as a PDF or a Word document,",
             "so both are read here — pypdf for PDF, python-docx for DOCX."),
            ("Word tables are read as well as paragraphs,",
             "because narratives routinely put the financial figures in a table."),
            ("There is no OCR.",
             "A scanned PDF has no text layer, so it is rejected with a clear message "
             "rather than scored on nothing."),
        ],
    ),
    (
        "Step 11: Understanding src/model.py — Part A",
        "This file makes the single Messages API call that scores the application.",
        "src/model.py",
        """MODEL = "claude-opus-5"


def score_application(narrative: str, rubric: dict, api_key: str) -> dict:
    \"\"\"Score one narrative in a single Messages API call.\"\"\"
    client = anthropic.Anthropic(api_key=api_key.strip())

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Here is the rubric:\\n\\n{json.dumps(rubric, indent=2)}\\n\\n"
                f"Here is the loan application narrative:\\n\\n{narrative}\\n\\n"
                "Score each of the five C's."
            ),
        }],
        output_config={"format": {"type": "json_schema", "schema": SCORE_SCHEMA}},
    )

    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)""",
        [
            ("One call, one answer.",
             "The task is completely specified, so no loop and no tools are needed."),
            ("output_config constrains the reply to a schema,",
             "so the application can rely on the fields existing instead of parsing prose."),
            ("The system prompt carries the scoring rules",
             "— score only what the narrative says, compute ratios rather than "
             "trusting stated ones, and return null where there is no evidence."),
        ],
    ),
    (
        "Step 12: Understanding src/agent.py — Part B",
        "This file gives the same application to an agent instead.",
        "src/agent.py",
        """def build_options(workspace: Path) -> ClaudeAgentOptions:
    \"\"\"Confine the agent to the lab folder and pre-approve its tools.\"\"\"
    return ClaudeAgentOptions(
        system_prompt=AGENT_SYSTEM_PROMPT,
        model=MODEL,
        cwd=str(workspace),
        allowed_tools=["Read", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=30,
    )


async def run_agent(narrative_path: Path, workspace: Path):
    \"\"\"Drive the agent and yield readable progress as it works.\"\"\"
    ensure_cli_available()

    prompt = (
        f"Score the loan application in {narrative_path.name} against "
        f"rubric.json, then write your credit memo to credit_memo.md."
    )

    async for message in query(prompt=prompt, options=build_options(workspace)):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    yield ("text", block.text)
                else:
                    yield ("tool", f"Using tool: {block.name}")""",
        [
            ("The agent is given a folder, not a question.",
             "It reads the rubric, reads the application, and decides its own steps."),
            ("allowed_tools pre-approves what it may use",
             "— Read to load the inputs, Write to produce the memo."),
            ("Every tool call is yielded to the interface,",
             "which is what makes the agent loop visible rather than a black box."),
        ],
    ),
    (
        "Step 13: Understanding src/scoring.py",
        "This file does the arithmetic once Claude has chosen the scores.",
        "src/scoring.py",
        """def round_half_up(value: float) -> int:
    \"\"\"Round .5 upwards.

    Python's built-in round() is banker's rounding: round(68.5) gives 68,
    not 69. A credit decision should not turn on that quirk.
    \"\"\"
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def aggregate(scores: list[dict], rubric: dict) -> dict:
    \"\"\"Turn per-C scores into a total, a band, and any hard-rule override.\"\"\"
    for item in scores:
        score = item.get("score")
        if score is None:
            continue                      # N/E leaves the denominator
        earned += points_for(score, weight)
        evidenced_weight += weight

    raw_total = earned / evidenced_weight * 100
    total = round_half_up(raw_total)
    band = band_for(total, rubric)""",
        [
            ("Claude chooses the 1-5 level; Python does the maths.",
             "That keeps the arithmetic identical on every run."),
            ("A C with no evidence scores N/E",
             "and its weight leaves the denominator rather than counting as zero — "
             "silence is not the same as weakness."),
            ("Rounding is half-up, stated explicitly,",
             "because a credit decision should not depend on a rounding quirk."),
        ],
    ),
]


def code_teardown(doc: Doc) -> None:
    for title, intro, filename, code, explanation in CODE_SECTIONS:
        doc.new_page()
        doc.grey_head(title, size=23)
        doc.body(intro)
        doc.body(f"File: {filename}", font="Mono", size=14, colour=INK_SOFT)
        doc.code_block(filename.replace("/", "_").replace(".", "_"), code)

        doc.need(120)
        doc.heading("Explanation:", size=24)
        items = [f"{bold} {rest}" for bold, rest in explanation]
        doc.numbered(items)


# ------------------------------------------------------------- how it works

def how_it_works(doc: Doc) -> None:
    doc.new_page()
    doc.grey_head("Step 14: How Everything Works Together", size=24)

    doc.body("Part A — the Messages API", font="Segoe-Bold", size=18)
    doc.numbered([
        "The user opens the web app (app.py runs).",
        "The user enters an Anthropic API key, which is validated once.",
        "The user uploads a loan application as a PDF or a Word document.",
        "src/ingestion.py reads the narrative out of that file.",
        "src/model.py sends one Messages API call carrying the rubric and the narrative.",
        "Claude returns the five scores as structured JSON, each with its evidence.",
        "src/scoring.py applies the weights, renormalises, rounds and bands the total.",
        "The decision, the arithmetic and the per-C reasoning are displayed.",
    ])

    doc.space(10)
    doc.body("Part B — the Claude Agent SDK", font="Segoe-Bold", size=18)
    doc.numbered([
        "The same narrative is written into a working folder alongside rubric.json.",
        "src/agent.py starts the agent with Read, Write, Glob and Grep available.",
        "The agent reads the rubric to learn the weights and level descriptors.",
        "The agent reads the application and works through the five C's itself.",
        "The agent writes credit_memo.md into the folder.",
        "Each tool call is streamed to the interface as it happens.",
    ])

    doc.space(10)
    doc.callout(
        "Both parts score the same application. The point of the lab is the difference "
        "in shape: Part A is one call you specify completely, Part B is a loop the model "
        "drives. Use a single call when the task can be specified; reach for an agent "
        "when the steps are not knowable in advance."
    )


# ----------------------------------------------------------------- summary

def summary(doc: Doc) -> None:
    doc.new_page()
    doc.heading("Summary of Lab-1", size=30)
    doc.space(6)
    doc.heading("What We Learned", size=26)

    entries = [
        ("requirements.txt", "Lists required software libraries."),
        ("app.py", "Entry point; hands off to src/main.py."),
        ("src/main.py", "Prompts for the API key, reads the upload, renders both parts."),
        ("src/ingestion.py", "Reads PDF, DOCX and TXT applications. No OCR."),
        ("src/validate.py", "Checks the API key before the lab spends tokens."),
        ("src/model.py", "Part A — one Messages API call, structured JSON back."),
        ("src/agent.py", "Part B — the Claude Agent SDK, with its own tools."),
        ("src/scoring.py", "Weighted arithmetic, renormalisation, banding, hard rule."),
        ("src/ui.py", "The interface components and the design system."),
        ("rubric.json", "The single source of truth for weights, levels and bands."),
    ]
    for n, (name, what) in enumerate(entries, start=1):
        doc.rich([(f"{n}. {name} ", True), (f"→ {what}", False)], indent=8)

    doc.space(16)
    doc.callout(
        "The API key was requested at run time in both halves of the lab — getpass in "
        "the notebook, a password field in the application. Nothing was written to disk, "
        "and nothing went into the repository."
    )


# --------------------------------------------------------------------- main

def _attach_code_block(doc_cls) -> None:
    """Give Doc a code_block() that renders and places a code screenshot."""

    def code_block(self, name: str, code: str) -> None:
        path = render_code(code, CODE_DIR / f"{name}.png")
        self.picture(path, max_w=CONTENT_W)

    doc_cls.code_block = code_block


def _parse_args():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=["bootcamp", "original"], default="bootcamp")
    ap.add_argument("--out", default=None)
    return ap.parse_args()


def main() -> int:
    args = _parse_args()
    layout.apply_theme(args.theme)
    _attach_code_block(Doc)
    CODE_DIR.mkdir(parents=True, exist_ok=True)

    out = Path(args.out) if args.out else HERE / "Lab-1_Loan_Application_Evaluation.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = Doc(out, ASSETS)

    if args.theme == "original":
        original_cover(doc, "Lab One", ["Loan Application", "Evaluation"],
                       "Scoring credit applications with the Claude Agent SDK")
    else:
        cover(doc)
    front_matter(doc)
    source_organization(doc)
    deployment(doc)
    code_teardown(doc)
    how_it_works(doc)
    summary(doc)

    doc.save()
    print(f"wrote {out}  ({doc.page} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
