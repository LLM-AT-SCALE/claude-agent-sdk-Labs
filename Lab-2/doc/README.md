# Lab 2 guide — build notes

```bash
cd Lab-2
python doc/build_lab_pdf.py
```

Writes `doc/Lab-2_DB_Operations.pdf`.

## Screenshots

Every figure is optional. Until an image exists, the page renders a dashed
placeholder naming the file that belongs there, so a missing capture is
obvious rather than silent.

Drop PNG or JPG files into `doc/assets/` using these names:

| File | What to capture |
|---|---|
| `colab_open.png` | `Lab_2.ipynb` on GitHub, with the Open in Colab badge visible |
| `colab_clone.png` | The first cell after a successful run — commit, tables, reject reasons |
| `neon_connect.png` | The Connect dialog in the Neon console |
| `colab_schema.png` | `db/run.py` output: drop, schema, seed applied |
| `colab_tests.png` | `34 passed` from the pytest cell |
| `colab_load.png` | The loader cell: 16 accepted, 8 rejected with reasons |
| `colab_reload.png` | The second load — zero rows added |
| `colab_ngrok.png` | The ngrok cell, tunnel open and URL printed |
| `app_connect.png` | The application's connect screen, both fields masked |
| `app_manual.png` | Manual mode, showing the joined `sales_detail` view |
| `app_ai.png` | AI mode, a reply with its tool call named above it |

Do not commit anything to `doc/assets/` that came from the bootcamp PDF —
`.gitignore` excludes the folder for that reason.

## Code listings

Listings are **read from the real source files at build time**, not pasted
into the build script. A guide that misquotes the code it documents is worse
than no guide, so `source()` slices the actual file between markers and
raises `LookupError` if a marker stops matching — which turns a silent
drift into a failed build.

The `(excerpt)` label is applied automatically, by comparing what was sliced
against the whole file. Nothing to keep in sync by hand.

## Theme

`--theme dboperations` (the default) uses the application's own palette —
warm paper, near-black ink, one terracotta accent — so the guide and the
software read as one thing. `--theme bootcamp` and `--theme original` are
inherited from the Lab 1 layout module and still work.
