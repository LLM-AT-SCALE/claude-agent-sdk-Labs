# Claude Agentic SDK Labs

Hands-on labs for building with Claude — the **Messages API** for well-specified
tasks, and the **Claude Agent SDK** for work whose steps aren't knowable in
advance.

Every lab runs in **Google Colab**. Nothing installs locally, and **the API key
is prompted at run time** — never hardcoded, never committed, never written to
disk.

## Labs

| Lab | Title | Surfaces | Problem | Open |
|---|---|---|---|---|
| [Lab-1](Lab-1) | Loan Application Evaluation | Messages API · Agent SDK | Score a commercial loan application narrative against the Five C's of Credit | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LLM-AT-SCALE/claude-agent-sdk-Labs/blob/main/Lab-1/Lab_1.ipynb) |
| [Lab-2](Lab-2) | DB Operations | Messages API · tool use | Record customers, products and sales in an insert-only Postgres database, through forms or through chat | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LLM-AT-SCALE/claude-agent-sdk-Labs/blob/main/Lab-2/Lab_2.ipynb) |

## Running a lab

Click a badge above — it opens that lab's notebook straight in Colab. Run the
cells in order; the first one clones the lab into the session.

Or clone just one lab and run it locally:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/LLM-AT-SCALE/claude-agent-sdk-Labs.git
cd claude-agent-sdk-Labs
git sparse-checkout set Lab-2          # or Lab-1
cd Lab-2
pip install -r requirements.txt
streamlit run app.py
```

## Prerequisites

- A Google account and Chrome, for Colab
- An **Anthropic API key** — [console.anthropic.com](https://console.anthropic.com/settings/keys)
- An **ngrok authtoken**, free, only for the Streamlit step — [dashboard.ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken)
- For Lab 2 only: a free **Neon Postgres** project — [console.neon.tech](https://console.neon.tech)

## On secrets

Every lab prompts for what it needs when it runs — the Anthropic key in both
labs, and in Lab 2 the database connection string as well:

- **In the notebook** — `getpass.getpass()`, so nothing appears in cell output
  and nothing is saved with the file
- **In the app** — `st.text_input(type="password")`, validated once before use

No lab reads a `.env`, and no credential belongs in this repository.
`.gitignore` blocks `.env` files as a second line of defence, but the first line
is that the code never looks for one.

## Disclaimer

These labs are for education. They are not production systems, and their output
should not be relied on for a real decision.
