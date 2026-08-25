# Lab 1 — Loan Application Evaluation

Score a commercial loan application narrative against the **Five C's of Credit**,
twice, using two different Claude surfaces.

## Objective

Give participants a working feel for the question *"do I need an agent here?"* by
solving the same problem both ways and comparing the shape of the work.

| | Surface | What it does |
|---|---|---|
| **Part A** | Messages API | One call. The task is fully specified; Claude returns structured JSON, and Python does the weighted arithmetic. |
| **Part B** | Claude Agent SDK | An agent with a folder and built-in tools. It reads the rubric and the narrative, works through the five C's, and writes a credit memo itself. |

## Prerequisites

- Google account, Chrome, Google Colab
- An Anthropic API key — prompted at run time, never stored
- An ngrok authtoken (free) for the Streamlit step

## Files

```
Lab-1/
├── Lab_1.ipynb          Colab entry point — run this
├── app.py               Streamlit entry point
├── rubric.json          The Five C's: weights, levels, bands, hard rule
├── requirements.txt
├── data/                Four sample narratives, one per decision band
├── src/
│   ├── validate.py      Checks the API key before the lab spends tokens
│   ├── model.py         Part A — the Messages API call
│   ├── agent.py         Part B — the Claude Agent SDK
│   ├── scoring.py       Weighted arithmetic, banding, the hard rule
│   └── main.py          Streamlit UI and orchestration
└── style/final.css
```

## The rubric

Five criteria, weighted to 100:

| | Criterion | Weight | Primary metric |
|---|---|---|---|
| C1 | Character | 20 | FICO, experience, disclosure |
| C2 | Capacity | 30 | DSCR = Adjusted EBITDA / Total Annual Debt Service |
| C3 | Capital | 20 | Equity injection as % of total project cost |
| C4 | Collateral | 20 | LTV = Loan Amount / Appraised Value |
| C5 | Conditions | 10 | Industry, concentration, use of proceeds |

`points = (score / 5) × weight`, summed, then banded: **85+** APPROVE ·
**70–84** APPROVE WITH CONDITIONS · **55–69** REFER TO CREDIT COMMITTEE ·
**below 55** DECLINE.

One hard rule: **Capacity scoring 1 forces a DECLINE** regardless of the total.
A loan that cannot cover its own debt service is not rescued by good collateral.

## Sample applications

Between them these hit every decision band:

| File | What it tests |
|---|---|
| `strong-approve.txt` | Every C evidenced, comfortable metrics |
| `hard-rule-decline.txt` | DSCR 0.85x — the hard rule should override the band |
| `incomplete-evidence.txt` | No collateral evidence — one C should score N/E |
| `stated-vs-computed-conflict.txt` | Claims 1.45x DSCR; its own figures say otherwise |

The last two are the interesting ones. A C with no evidence is scored `N/E` and
its weight is **left out of the total** rather than counted as zero — silence is
not the same as weakness. And where a narrative asserts a ratio its own figures
contradict, the computed value governs and the contradiction is reported.

## Running it

Open `Lab_1.ipynb` in Colab and run the cells in order. The notebook clones the
lab, installs dependencies, prompts for your key, runs both parts, and finally
launches the Streamlit app through ngrok.
