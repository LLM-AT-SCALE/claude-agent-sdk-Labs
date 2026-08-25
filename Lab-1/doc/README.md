# Lab 1 — step-by-step guide (PDF)

Builds `Lab-1_Loan_Application_Evaluation.pdf` in the format of the existing
bootcamp documents: cover, disclaimer and objective, source-code organization,
a click-by-click deployment walkthrough, a file-by-file code teardown with
explanations, then how it all fits together and what was learned.

```bash
python doc/build_lab_pdf.py
```

## Files

| File | What it does |
|---|---|
| `build_lab_pdf.py` | The document — content and page order |
| `layout.py` | Page furniture and layout primitives |
| `codeshot.py` | Renders a snippet of Python as a dark editor screenshot |
| `assets/` | Images the document places (**not in version control** — see below) |

## Assets are not committed

`doc/assets/` holds artwork and screenshots lifted from the existing bootcamp
PDF, which is marked *Confidential and Proprietary — Not for Distribution*.
This repository is public, so those files are gitignored and the built PDF is
too. Anyone rebuilding the document supplies their own.

The build degrades gracefully: a missing image is skipped rather than raising,
so the PDF still assembles with the text intact.

Assets the document looks for:

| File | Used for |
|---|---|
| `cover_bg.png` | Full-bleed cover artwork |
| `mascot.jpg` | Robot at the top right of every page |
| `stripe.png` | Its shadow |
| `colab_open.jpeg` | Opening the notebook in Colab |
| `colab_run_cell.jpeg` | Running the first cell |
| `colab_restart.jpeg` | The *Restart session* dialog |
| `colab_files.jpeg` | The Files panel after cloning |
| `ngrok_login.jpeg` | Signing in to ngrok |

## Page geometry

Measured from the source document so the two sit side by side: 1080×1500pt
page, hairline rule 31pt from the top, mascot at `[943, 51, 1051, 159]` with a
green chevron drawn as vector art over it, the page number in bold 12pt
`#333333` on a 145pt baseline, and a 22pt bar across the foot split into equal
blue / green / purple thirds.
