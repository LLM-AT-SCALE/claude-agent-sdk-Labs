# Claude Agentic SDK Labs

Hands-on labs for building with Claude — the **Messages API** for well-specified
tasks, and the **Claude Agent SDK** for work whose steps aren't knowable in
advance.

Every lab runs in **Google Colab**. Nothing installs locally, and **the API key
is prompted at run time** — never hardcoded, never committed, never written to
disk.

## Labs

| Lab | Title | Surfaces | Problem |
|---|---|---|---|
| [Lab-1](Lab-1) | Loan Application Evaluation | Messages API · Agent SDK | Score a commercial loan application narrative against the Five C's of Credit |

## Running a lab

Open the lab's notebook in Colab and run the cells in order:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chetankumarmk56/Claude-Agentic-SDK-Labs/blob/main/Lab-1/Lab_1.ipynb)

Or clone just one lab:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/chetankumarmk56/Claude-Agentic-SDK-Labs.git
cd Claude-Agentic-SDK-Labs
git sparse-checkout set Lab-1
cd Lab-1
pip install -r requirements.txt
streamlit run app.py
```

## Prerequisites

- A Google account and Chrome, for Colab
- An **Anthropic API key** — [console.anthropic.com](https://console.anthropic.com/settings/keys)
- An **ngrok authtoken**, free, only for the Streamlit step — [dashboard.ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken)

## On API keys

Every lab prompts for the key when it runs:

- **In the notebook** — `getpass.getpass()`, so the key never appears in cell output
  and is never saved with the file
- **In the app** — `st.text_input(type="password")`, validated once before use

No lab reads a `.env`, and no key belongs in this repository. `.gitignore` blocks
`.env` files as a second line of defence, but the first line is that the code
never looks for one.

## Disclaimer

These labs are for education. They are not production systems, and their output
should not be relied on for a real decision.
