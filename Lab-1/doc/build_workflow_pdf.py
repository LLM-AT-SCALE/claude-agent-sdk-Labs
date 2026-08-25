"""Build the Lab 1 companion guide: how the application was built.

    python doc/build_workflow_pdf.py

Same page furniture as the lab guide, but the subject is the process rather
than the deployment: nine steps across three phases, the prompts that were
actually typed, what came back, and the four times the loop ran.
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from codeshot import render_code  # noqa: E402
from layout import (  # noqa: E402
    CONTENT_W, INK_SOFT, PAGE_H, PAGE_W, WHITE, Doc, find_asset,
)

ASSETS = HERE / "assets"
CODE_DIR = HERE / "code"
REPO = "https://github.com/chetankumarmk56/Claude-Agentic-SDK-Labs"


def cover(doc: Doc) -> None:
    doc.new_page(chrome=False)
    c = doc.c

    background = find_asset(ASSETS, "cover_bg.png")
    if background:
        c.drawImage(ImageReader(str(background)), 0, 0, PAGE_W, PAGE_H, mask="auto")

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
    c.roundRect(117, PAGE_H - 936, 904, 186, 8, stroke=0, fill=1)
    c.setFillColor(HexColor("#0F6B4F"))
    c.setFont("Segoe-Bold", 40)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 812, "LAB ONE — COMPANION")
    c.setFillColor(HexColor("#2A2A2A"))
    c.setFont("Segoe-Bold", 32)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 868, "How the Application Was Built")
    c.setFillColor(HexColor("#5A5A5A"))
    c.setFont("Segoe", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 912,
                        "Nine steps  ·  Three phases  ·  Four cycles")


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
    doc.space(16)

    doc.banner("Objective", width=300)
    doc.body(
        "Show how the Lab 1 application was actually built, using the real prompts that "
        "were given and the real answers that came back. The companion to the lab guide: "
        "that document explains how to run the application, this one explains how it came "
        "to exist."
    )
    doc.space(16)

    doc.banner("How to read this", width=360)
    doc.body(
        "The work followed a fixed workflow of nine steps across three phases. The human "
        "defines the problem and accepts the result; the model does the work in between. "
        "Cycle 1 is documented step by step. The loop then ran three more times, and "
        "those cycles are summarised."
    )
    doc.space(8)
    doc.callout(
        "Workflow model: Jothi Periasamy, Anthropic Claude Ambassador. Every prompt "
        "quoted in this document is reproduced exactly as it was typed."
    )


def workflow_overview(doc: Doc) -> None:
    doc.new_page()
    doc.running_head("GEN AI BOOTCAMP FOR ENTERPRISE ENABLEMENT")
    doc.grey_head("The Workflow", size=26)
    doc.body(
        "Three phases, nine steps. DEFINE asks what we are solving, BUILD generates the "
        "code, and VALIDATE runs it and proves it works. Each step is owned by either the "
        "human or the model."
    )
    doc.space(4)

    doc.table(
        ["Phase", "Step", "Owner", "What happens"],
        [
            ["DEFINE", "0", "Human", "Problem statement"],
            ["", "1", "LLM", "Refine the problem statement"],
            ["", "2", "LLM", "Write the system specification"],
            ["BUILD", "3", "LLM", "Write the system prompt for Claude Code"],
            ["", "4", "Claude Code", "Claude Code builds the application"],
            ["VALIDATE", "5", "Standalone code", "Run it on a real document"],
            ["", "6", "Standalone code", "Self-validates and reports, no action"],
            ["", "7", "Human", "Human reviews, loops back if needed"],
            ["", "8", "Human", "Final output accepted"],
        ],
        widths=[1.6, 0.7, 1.9, 5.3],
    )

    doc.space(6)
    doc.callout(
        "Two arrows make it a loop rather than a line. Step 4 can send the work back to "
        "step 3 when the build needs changing, and step 7 can send it back to the "
        "beginning. Both fired during this project."
    )


CYCLE_ONE = [
    dict(
        head="Step 0: Problem Statement",
        who="Human",
        intro="The human sets the working rules, then states the problem.",
        prompts=[
            ("Prompt 1 — setting the rules",
             "we'll go step by step now we are in the define stage where i define and you "
             "understand help refine the problem statement did you get that no coding till "
             "we go to the build stage"),
            ("Prompt 2 — the problem",
             "We need to build a loan evaluation web app. So users upload a loan application "
             "document, either a PDF or DOCX. And the system extracts borrower info, applies "
             "the attached five C's rubric, scores each C from 1 to 5, calculates weighted "
             "score, and enforces the hard rule. So if capacity equals 1, it is an automatic "
             "decline. And then it outputs a decision plus an evidence based explanation "
             "where the rubric JSON is the single source of truth."),
        ],
        explanation=[
            "Input — one document, PDF or DOCX.",
            "Scoring — five C's, 1 to 5 each, weighted to a total.",
            "Hard rule — Capacity of 1 forces an automatic decline.",
            "Output — a decision plus an evidence-based explanation.",
            "Authority — rubric.json is the single source of truth.",
        ],
        tail="Also handed over: rubric.json, carrying the five C's, weights of "
             "20/30/20/20/10, level descriptors 1 to 5, four decision bands and one hard "
             "rule. Everything the application scores against had to come from that file.",
    ),
    dict(
        head="Step 1: Refine the Problem Statement",
        who="LLM",
        intro="Before asking anything, the rubric itself was checked for consistency.",
        prompts=[],
        explanation=[
            "Weights sum to exactly 100.",
            "Every possible point value is a whole number.",
            "The four decision bands cover every reachable score.",
            "HR-1 is the only hard rule in the file.",
        ],
        tail="Six gaps were then raised. The two sharpest: the level descriptors are "
             "compound prose, so a borrower matching part of level 5 and part of level 3 "
             "has no defined outcome; and N/E creates a perverse result, because Capacity "
             "of 1 auto-declines while Capacity of N/E does not — an application that "
             "discloses a bad DSCR is punished harder than one that omits its financials.",
    ),
    dict(
        head="Step 1 continued: The Gaps Are Closed",
        who="Human",
        intro="Six questions in, six answers back. Each became a rule the build could not "
              "drift from.",
        prompts=[
            ("The answers, verbatim",
             "1. I agree with your judgement there  2. Renormalize the total over only the "
             "evidenced weights but also flag it as an incomplete in the outcome  3. compute "
             "the metrics  4. Should show what happened with all C's and it should be "
             "completely based on rubric  5. the user's will just upload their proposal get "
             "an output score and decision along with a word document of detail explanation  "
             "6. 1 document at a time, no OCR, the user can not upload their own rubric"),
        ],
        explanation=[
            "Lowest matching criterion wins — the weakest evidenced criterion sets the C.",
            "N/E leaves the denominator entirely, and raises an INCOMPLETE flag.",
            "DSCR, LTV and equity percentage are calculated, not taken on the document's word.",
            "Every C is shown, and every score is traced to a rubric level and a sentence.",
            "A summary on screen, plus a downloadable Word report.",
            "Scope sealed: one document, no OCR, no persistence, a fixed rubric.",
        ],
        tail="",
    ),
    dict(
        head="Step 2: Write the System Specification",
        who="LLM",
        intro="The answers themselves created new problems, which had to be caught before "
              "the specification could close.",
        prompts=[],
        explanation=[
            "Renormalising broke the arithmetic. Before, every total was a whole number. "
            "Renormalising over evidenced weight stops that: 58 divided by 80 times 100 is "
            "72.5. The decision bands are declared with whole-number bounds, so a "
            "renormalised 69.4 belongs to no band at all.",
            "Four policy decisions now existed nowhere in rubric.json, so the file was no "
            "longer the single source of truth it claimed to be.",
            "Three edge cases were uncovered: Capacity itself scoring N/E, every C scoring "
            "N/E and dividing by zero, and whether any minimum evidence threshold applies.",
        ],
        tail="The reply settled all three: convert the fractional total to an integer, "
             "extend rubric.json rather than putting policy in code, and treat the build as "
             "a teaching demonstration. The specification then closed as CLAUDE.md, which "
             "guided every build step that followed.",
    ),
    dict(
        head="Step 3: Write the System Prompt for Claude Code",
        who="Human",
        intro="With the specification closed, the build could be described in one prompt.",
        prompts=[
            ("The build prompt",
             "build a code with a proper architecture and modularity. I want the back end to "
             "be fast API and the front end to be React, use TypeScript for the front end. "
             "So create a Claude dot MD file and update the specifications for this "
             "application. Like, the input should be a document and the output should be a "
             "summary of the result along with the detailed word document to download about "
             "their application against the rubric."),
        ],
        explanation=[
            "FastAPI on the back end, React with TypeScript on the front.",
            "Proper layering and modularity, not a single file.",
            "CLAUDE.md as the written specification.",
            "A document in, a summary and a Word report out.",
        ],
        tail="",
    ),
    dict(
        head="Step 3 loop-back: Changes Needed",
        who="Human",
        intro="This is the loop-back arrow. It arrived mid-build and changed the design.",
        prompts=[
            ("The correction",
             "I forgot to mention, the parser should be completely deterministic should not "
             "use any AI to do any so that no matter how many time i ask or which year i ask "
             "the output will be the same"),
        ],
        explanation=[
            "The phrase that mattered was “which year i ask”. Appraisal age is the "
            "one rubric input that invites date arithmetic, and computing it against "
            "today's date would make the same document score differently next year.",
            "Appraisal age now reads only an explicitly stated interval, such as "
            "“completed 4 months ago”, and never a calendar date.",
            "The AI extractor was dropped entirely; a deterministic rule engine became the "
            "only way facts leave the document.",
        ],
        tail="Three prohibitions now hold the guarantee up: no model, no clock, and no "
             "randomness anywhere in the evaluation path.",
    ),
]


def cycle_one(doc: Doc) -> None:
    for section in CYCLE_ONE:
        doc.new_page()
        doc.grey_head(section["head"], size=23)
        doc.body(section["intro"])
        for label, text in section["prompts"]:
            doc.prompt_box(label, f"“{text}”", who=section["who"])
        if section["explanation"]:
            doc.heading("Explanation:", size=24)
            doc.numbered(section["explanation"])
        if section["tail"]:
            doc.body(section["tail"])


def build_and_validate(doc: Doc) -> None:
    doc.new_page()
    doc.grey_head("Step 4: Claude Code Builds the Application", size=23)
    doc.body(
        "One deterministic pipeline, each stage swappable behind an interface: ingest, "
        "extract, compute the metrics, score, aggregate, decide, report."
    )
    doc.numbered([
        "rubric.json was extended with machine-readable criteria per level, so the "
        "lowest-matching-criterion rule could be executed rather than described.",
        "Extraction became ordered rule tuples — numeric, categorical and boolean — "
        "with every fact carrying the sentence it came from.",
        "Scoring applies the weights, renormalises, rounds half-up and then applies the "
        "hard rules, in that order.",
        "Reporting traces each score to a rubric level and a quoted sentence.",
    ])
    doc.space(4)
    doc.body("The rounding, written explicitly rather than left to the language:",
             colour=INK_SOFT, size=14)
    doc.code_block("wf_rounding", '''def round_half_up(value: float) -> int:
    """Round .5 upwards.

    Python's built-in round() is banker's rounding: round(68.5) gives 68,
    not 69. A credit decision should not turn on that quirk.
    """
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))''')

    doc.new_page()
    doc.grey_head("Step 5: Run It on a Real Document", size=23)
    doc.body(
        "Four sample narratives, chosen so that between them they exercise every decision "
        "band."
    )
    doc.table(
        ["Document", "What it tests", "Score", "Decision"],
        [
            ["strong-approve", "All five C's evidenced, comfortable metrics", "92", "APPROVE"],
            ["hard-rule-decline", "DSCR 0.85x, so Capacity scores 1 and HR-1 overrides "
                                  "the band", "44", "DECLINE"],
            ["incomplete-evidence", "No collateral evidence, so 58 over 80 becomes 72.5",
             "73", "APPROVE WITH CONDITIONS"],
            ["stated-vs-computed", "Claims 1.45x; its own figures compute 1.17x", "62",
             "REFER TO CREDIT COMMITTEE"],
        ],
        widths=[2.0, 4.4, 0.8, 2.4],
    )

    doc.new_page()
    doc.grey_head("Step 6: It Self-Validates and Reports — No Action", size=23)
    doc.body(
        "When the application meets something wrong, it says so and stops. It never "
        "quietly repairs the gap."
    )
    doc.numbered([
        "Collateral never mentioned — scores N/E, its 20 points leave the denominator, "
        "and an INCOMPLETE flag is raised. It does not guess a value.",
        "The narrative claims a DSCR of 1.45x while its own figures compute 1.17x — the "
        "computed value governs and the contradiction is printed. It does not hide the "
        "conflict.",
        "A scanned PDF with no text layer — rejected with a message naming the reason. "
        "It does not attempt a guess.",
    ])
    doc.space(4)
    doc.body(
        "Determinism was tested rather than asserted: the same bytes produce identical "
        "output five runs in a row, and the evaluation id is a digest of the document, so "
        "even the id reproduces."
    )

    doc.new_page()
    doc.grey_head("Step 7: Human Reviews, Loops Back If Needed", size=23)
    doc.body(
        "Running real documents surfaced three defects that the unit tests had not "
        "reached."
    )
    doc.numbered([
        "Hard-wrapped lines split sentences mid-clause, so “Total annual / debt service "
        "of $890,000” became two fragments and the figure lost the phrase identifying "
        "it. Real PDFs wrap exactly this way.",
        "“Unlimited personal guarantees” matched the pattern for “limited”, "
        "because the word contains it. The strongest guarantee scored as the weakest.",
        "The override wording read wrongly when the hard rule and the band agreed, saying "
        "the score “would otherwise have banded as DECLINE” when it already had.",
    ])
    doc.space(6)
    doc.callout(
        "The pattern worth noting: the tests proved the rules were applied correctly. Only "
        "running real documents proved the right things were being read in the first place."
    )

    doc.new_page()
    doc.grey_head("Step 8: Final Output Accepted", size=23)
    doc.body("What existed at the end of the first pass through the nine steps.")
    doc.card_row([
        ("Web application", "Upload a PDF or DOCX, get a decision, a weighted score with "
                            "its arithmetic shown, and a criterion-by-criterion breakdown."),
        ("Word report", "Every score traced to a rubric level and a quoted sentence, plus "
                        "what would raise each one."),
    ])
    doc.card_row([
        ("rubric.json", "The single source of truth. Swap the file and the whole system's "
                        "behaviour changes with no code edit."),
        ("CLAUDE.md", "The specification, the layering rules, and the invariants that must "
                      "not break."),
    ])
    doc.space(4)
    doc.body("Accepted, and reproducible. But step 8 turned out not to be the end.")


def later_cycles(doc: Doc) -> None:
    doc.new_page()
    doc.chevron("The Loop Did Not Stop at Step 8")
    doc.body(
        "Each new requirement re-entered the workflow at step 0 and ran the whole way "
        "through. Nothing skipped the define phase, and nothing skipped validation."
    )
    doc.space(4)

    doc.table(
        ["Cycle", "What was asked for", "What changed", "Tests"],
        [
            ["2", "A list of missed evidence, and any recommendations",
             "Every unevidenced criterion listed, and four kinds of recommendation — "
             "all derived from rubric.json rather than written", "65 → 81"],
            ["3", "Split the specification out of the working instructions",
             "SPEC.md holds what the system is; CLAUDE.md dropped to 150 lines and holds "
             "only how to work on it", "81 → 81"],
            ["4", "Record which rules produced the facts",
             "Every fact now names the rule that read it and how the value was picked, in "
             "a new Extraction trace section", "81 → 96"],
        ],
        widths=[0.8, 3.0, 5.0, 1.2],
    )

    doc.new_page()
    doc.grey_head("What Cycle 2 Caught in Its Own New Code", size=23)
    doc.body(
        "The recommendations feature projected what each score could become. The first "
        "version assumed a criterion could always rise by one level."
    )
    doc.code_block("wf_levels", '''def available_levels(criterion) -> set[int]:
    """Every level this criterion can actually express.

    Rubric criteria are not obliged to define all five rungs - Conditions'
    regulatory exposure maps only to 5, 3 and 1. Assuming a criterion can
    always move up by exactly one would overstate what is reachable.
    """
    if criterion.type in ("numeric_desc", "numeric_asc"):
        return {t.level for t in criterion.thresholds}
    if criterion.type == "categorical":
        return set(criterion.mapping.values())''')

    doc.heading("Explanation:", size=24)
    doc.numbered([
        "Conditions' regulatory exposure maps only to levels 5, 3 and 1. From level 3 its "
        "next reachable level is 5, not 4.",
        "So “lift Conditions from 3 to 4 for two points” was wrong — the C "
        "would not have moved at all.",
        "Reachability is now read from the rubric rather than assumed, and where several "
        "criteria tie at the bottom, all of them are named.",
    ])


def what_review_caught(doc: Doc) -> None:
    doc.new_page()
    doc.grey_head("Every Defect Was Caught by a Step, Not by Luck", size=23)
    doc.body(
        "Six real defects reached working code across the four cycles. Each was found by "
        "the step designed to find it, and none by the test suite alone."
    )
    doc.table(
        ["Defect", "Cycle", "Found by"],
        [
            ["Hard-wrapped lines split sentences mid-clause, so a figure lost the phrase "
             "naming it", "1", "Step 5 — running a real file"],
            ["“Unlimited guarantees” matched the “limited” pattern, so "
             "the strongest read as the weakest", "1", "Step 5 — running a real file"],
            ["Override wording read wrongly when the hard rule and the band agreed", "1",
             "Step 7 — human review"],
            ["Projection assumed a next level the rubric did not define", "2",
             "Step 6 — self-validation"],
            ["Computed ratios carried no attribution, so the new feature looked absent", "4",
             "Step 5 — running a real file"],
            ["A stale payload could blank the panel after a backend restart", "4",
             "Step 6 — console check"],
        ],
        widths=[6.2, 0.8, 3.0],
    )


def closing(doc: Doc) -> None:
    doc.new_page()
    doc.heading("Summary — What Made It Work", size=30)
    doc.space(4)

    doc.grey_head("1. Defining took longer than building", size=20)
    doc.body(
        "Two rounds of questions before a line of code, and every later cycle re-entered "
        "at step 0. Each question was a decision that would otherwise have been made "
        "silently, and wrongly, inside the build."
    )

    doc.grey_head("2. Policy went into data, not code", size=20)
    doc.body(
        "Weights, thresholds, bands, rounding and hard rules all live in rubric.json. "
        "Changing credit policy is editing a file, not shipping a release — and the "
        "derived report text inherits the change for free."
    )

    doc.grey_head("3. The steps are a loop, not a line", size=20)
    doc.body(
        "Step 8 was reached four times. Each new requirement went back to the beginning "
        "rather than being bolted on, and every cycle surfaced a defect the previous one "
        "could not have seen."
    )

    doc.space(10)
    doc.callout(
        "Still true after four cycles: no language model at run time, no clock in the "
        "evaluation path, and no randomness. The same document produces the same report "
        "on any machine, in any year."
    )

    doc.space(6)
    doc.outlined_box("GitHub link:", f"{REPO}/tree/main/Lab-1")


def _attach_code_block(doc_cls) -> None:
    def code_block(self, name: str, code: str) -> None:
        path = render_code(code, CODE_DIR / f"{name}.png")
        self.picture(path, max_w=CONTENT_W)
    doc_cls.code_block = code_block


def main() -> int:
    _attach_code_block(Doc)
    CODE_DIR.mkdir(parents=True, exist_ok=True)

    out = HERE / "Lab-1_How_The_Application_Was_Built.pdf"
    doc = Doc(out, ASSETS)
    doc.c.setTitle("Lab 1 Companion - How the Application Was Built")

    cover(doc)
    front_matter(doc)
    workflow_overview(doc)
    cycle_one(doc)
    build_and_validate(doc)
    later_cycles(doc)
    what_review_caught(doc)
    closing(doc)

    doc.save()
    print(f"wrote {out}  ({doc.page} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
