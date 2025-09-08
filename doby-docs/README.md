# Doby’s ESA Pyxel Notes (living) 🌙✨

---

<img src="assets/pyxel-badge.png" alt="pyxel" width="350"/> 

These are my personal, evolving notes while I contribute to the **ESA Pyxel** project —
mostly documentation, clarity, accessibility, and Windows onboarding. I’m learning out
loud and keeping a trail for future‑me (and anyone else who finds it useful).

⚠️ Not official ESA documentation. Just my notes and iterations.

---

## Quick links:
- Upstream repo: https://gitlab.com/esa/pyxel
- My fork: https://gitlab.com/dobybaxter127/pyxel/-/tree/doby-notes
- Contributing guide: https://esa.gitlab.io/pyxel/doc/stable/references/contributing.html
- Issues: https://gitlab.com/esa/pyxel/-/issues

---

## 🌳 How I organize branches
- Personal notes branch: `doby-notes` (never used for merge requests).
- Contribution branches: start from `master` (e.g., `docs-windows-tips`) and open an MR to `esa/pyxel`.

Keep my fork fresh:
```
git switch master
git fetch upstream
git rebase upstream/master
```

Start a small docs change:
```
git switch -c docs-<short-topic>
```

---

## 💻 Local docs workflow (Windows)

I use the Sphinx that **tox** installs and skip notebook execution for quick previews.

First time (sets up tox env):
```
.\.venv\Scripts ctivate
pip install tox
tox -e docs
```

Fast preview afterwards (skip notebook execution; rebuild from source):
```
.\.tox\docs\Scripts\sphinx-build -E -a -b html -D nb_execution_mode=off docs\source docs\html
start "" docs\html\index.html
```

---

## 🧰 Windows tips I keep bumping into
- In CMD, `#` is NOT a comment and `< >` are redirection operators. Don’t paste comment lines;
  replace placeholders like `<topic>` with real names (e.g., `docs-windows-tips`).
- If `sphinx-build` isn’t found, use the one inside `.tox\docs\Scripts\`.

---

## 🪐 Contribution log (living)
Format I use:
```
YYYY-MM-DD — <Area/Page> — <Summary> — <MR link> — <Status>
```

Example:
```
2025-09-06 — Installation — Add Windows tip for fast local preview; tidy wording — MR #1092 — Open
```

---

## 📙 MR description template (docs-only)
```
Docs-only change.

- Add Windows tip to preview docs locally without executing notebooks:
    sphinx-build -E -b html -D nb_execution_mode=off docs/source docs/html
- Minor wording/consistency fixes on the Installation page.

No code changes.
```

---

## 👾 Commit message style (mine)
- `docs: <summary>` (general docs)
- `docs(<section>): <summary>` (scoped to a page/section)

Examples:
```
docs(install): add Windows tip for fast local preview; tidy wording
docs(get-help): clarify link to issue tracker and support channels
```

---

## ✅ Pre-push sanity checklist
- Built locally and previewed the exact page.
- RST/MD indentation is clean; code blocks render.
- Wording is clear and welcoming; “macOS” capitalization consistent.
- Links work.
- New pages (if any) are included in the correct `toctree`.

---

## 🚀 Roadmap / ideas (growing list)
- Add a short “Windows placeholders” note near the Installation tip.
- Audit Tutorials for Windows-specific caveats (paths, shells).
- Improve **Get Help** with “what to include in a docs issue”.
- Tiny glossary for new readers (model, pipeline, detector).
- Contributing to yaml, py and other files. 

---

Thank you for being here!🌈☀️
