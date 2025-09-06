# Doby's ESA Pyxel notes

ESA Pyxel – Doby Baxter (Living Documentation)
========================================================

Personal notes for my contributions to the ESA Pyxel project — focused on documentation,
accessibility, and Windows onboarding. This is NOT official ESA documentation.

Quick links
-----------
- Upstream repo: https://gitlab.com/esa/pyxel
- My fork: https://gitlab.com/dobybaxter127/pyxel
- Contributing guide: https://esa.gitlab.io/pyxel/doc/stable/references/contributing.html
- Issues: https://gitlab.com/esa/pyxel/-/issues

How I work (branches)
---------------------
- Personal notes branch: doby-notes (never used for merge requests).
- Feature branches for upstream MRs: start from master (e.g., docs-windows-tips), then open MR to esa/pyxel.

Keep fork fresh:
    git switch master
    git fetch upstream
    git rebase upstream/master

Start a docs change:
    git switch -c docs-<short-topic>

Local docs workflow (Windows)
-----------------------------
Use tox’s Sphinx to avoid installing Sphinx into my venv, and skip notebook execution for quick previews.

From repo root:
    .\.venv\Scripts\activate
    pip install tox

First run (sets up tox env; may try to run notebooks):
    tox -e docs

Fast preview (skip notebooks; rebuild from source):
    .\.tox\docs\Scripts\sphinx-build -E -a -b html -D nb_execution_mode=off docs\source docs\html
    start "" docs\html\index.html

Windows tips
------------
- In CMD, # is not a comment and < > are redirection operators. Don’t paste comment lines;
  replace placeholders like <topic> with real names (e.g., docs-windows-tips).
- If sphinx-build isn’t found, use the one inside .tox\docs\Scripts\

Contribution log (living)
-------------------------
Format:
    YYYY-MM-DD — <Area/Page> — <Summary> — <MR link> — <Status>

Example:
    2025-09-06 — Installation — Add Windows tip for fast local preview; tidy wording — MR #1092 (paste link) — Open

MR description template
-----------------------
Docs-only change.

- Add Windows tip to preview docs locally without executing notebooks:
      sphinx-build -E -b html -D nb_execution_mode=off docs/source docs/html
- Minor wording/consistency fixes on the Installation page.

No code changes.

Commit message guidelines (mine)
--------------------------------
- docs: <summary>     (general docs)
- docs(install): <summary>   (scoped to a page/section)

Examples:
    docs(install): add Windows tip for fast local preview; tidy wording
    docs(get-help): clarify link to issue tracker and support channels

Review checklist (before pushing)
---------------------------------
- Built locally and previewed the edited page.
- No broken RST indentation; code blocks render.
- Clear, inclusive wording; macOS capitalization consistent.
- Added/updated links are valid.
- If I added a new page, it’s referenced in the appropriate toctree.

Roadmap / ideas
---------------
- Add “Windows placeholders” note near the Installation tip.
- Audit Tutorials for Windows-specific caveats (paths, shells).
- Improve Get Help section with a short “What to include in a docs issue”.
- Tiny glossary of Pyxel docs terms (e.g., model, pipeline, detector).
---
