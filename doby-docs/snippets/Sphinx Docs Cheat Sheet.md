# 🌌 ESA Pyxel - Sphinx Docs Cheat Sheet 

*A friendly working-notes guide to build, preview, and write docs for ESA Pyxel.*  
_Not official ESA documentation — just my contributor notes._

---

## 🛠️ Build & preview

### First-time (sets up tox env)
```console
.\.venv\Scripts\activate
pip install tox
tox -e docs
```

### Fast local preview (skip notebook execution)
Use the Sphinx that tox installs, **skip** executing notebooks, and rebuild everything:
```console
.\.tox\docs\Scripts\sphinx-build -E -a -b html -D nb_execution_mode=off docs\source docs\html
start "" docs\html\index.html
```

**Flags I use**
- `-E` → ignore saved environment (clean build of sources)  
- `-a` → rebuild **all** files (not just changed)  
- `-W` → treat warnings as errors (strict)  
- `-D nb_execution_mode=off` → don’t execute notebooks (great for text‑only edits)

**Strict but still skip notebooks**
```console
.\.tox\docs\Scripts\sphinx-build -E -W -b html -D nb_execution_mode=off docs\source docs\html
```

**Clean output directory + rebuild**
```console
rmdir /s /q docs\html
.\.tox\docs\Scripts\sphinx-build -E -a -b html -D nb_execution_mode=off docs\source docs\html
```

**Find the built page path**
```console
dir /b /s docs\html\*install*.html
```

**Search a phrase across built HTML**
```console
findstr /s /m /c:"nb_execution_mode" docs\html\*.html
```

> 💡 If `sphinx-build` isn’t found, use the one inside `.tox\docs\Scripts\` as shown above.

---

## 🧭 Where to put things

```
docs/
  source/
    tutorials/        # getting started guides
    howto/            # task-focused “how-to” pages
    references/       # API/overview/reference
    about/            # FAQ, license, contributors, etc.
```

When adding a new page, place the `.rst` (or `.md` with MyST) under the right folder and include it in the parent **toctree** (see below).

---

## ✍️ RST essentials (reStructuredText)

**Headings**
```rst
Title in sentence case
======================

Section
-------

Subsection
~~~~~~~~~~
```

**Anchors / labels (for cross-references)**
```rst
.. _install_windows_tip:

Title
=====
```

**Links**
- External: `` `Anaconda <https://www.anaconda.com/download>`_ ``  
- Internal section: ``:ref:`Text to show <install_windows_tip>` ``

**Admonitions**
```rst
.. tip::
   Helpful hint goes here.

.. note::
   Extra context or background.

.. warning::
   Things that can break or surprise users.
```

**Code blocks**
```rst
.. code-block:: console

   sphinx-build -E -b html -D nb_execution_mode=off docs/source docs/html
```
Choose a lexer that matches the content: `console`, `bash`, `powershell`, `python`, `yaml`, etc. Avoid shell prompts like `$` or `C:\>` — just the commands.

**Images**
```rst
.. image:: ../_static/my-screenshot.png
   :alt: Local docs preview showing the Windows tip
   :width: 700px
```
Use meaningful `:alt:` text for accessibility. Prefer relative paths.

**Quick table**
```rst
.. list-table:: Supported OS
   :header-rows: 1

   * - OS
     - Notes
   * - Windows
     - Use ``nb_execution_mode=off`` for quick previews
   * - macOS
     - Tested with …
```

---

## ✍️ MyST Markdown (optional) — Sphinx‑friendly MD

You can write some pages in Markdown using **MyST**. Keep consistent with the folder’s existing format.

```md
# Title

{ref}`install_windows_tip`

```{note}
This is a MyST note admonition.
```

```{code-block} console
sphinx-build -E -b html -D nb_execution_mode=off docs/source docs/html
```
```

---

## 🌳 Toctree — make your page appear in the sidebar

Add your file (without `.rst`) to the parent’s `.. toctree::`. Example in `tutorials/overview.rst`:

```rst
.. toctree::
   :maxdepth: 1

   install
   running
   get_help
   environments
   windows-tips   # <— your new page filename (windows-tips.rst)
```

After editing a toctree, rebuild and check the left sidebar.

---

## 🧪 Troubleshooting builds

- Notebook execution fails → build with `-D nb_execution_mode=off`.  
- Where’s the error? Sphinx prints the file path; for myst‑nb it may also log under `docs/html/reports/...`.  
- Old content still shows → hard‑refresh the browser (Ctrl+F5) or rebuild with `-E -a`.  
- Warnings stop the build → drop `-W` locally; CI will enforce strictness.  
- Windows quoting → avoid `#` and `<…>` in CMD; replace placeholders with real names.

---

## Writing style (what I aim for)

- Clear, step‑by‑step, **welcoming** tone.  
- Sentence case headings; **macOS** capitalization.  
- Prefer active voice and short sentences.  
- When steps differ by OS, **split** them (Windows / macOS / Linux).  
- Add **alt text** for images; describe *what the user should see*.  
- Use cross‑refs (`:ref:`) instead of repeating long links.  
- Show **one** good way first; add alternatives afterwards.

---

## MR & commits (docs‑only)

**Commit messages**
```
docs(install): add Windows tip for fast local preview; tidy wording
docs(get-help): clarify link to issue tracker
```

**MR description template**
```
Docs-only change.

- Add Windows tip to preview docs locally without executing notebooks:
    sphinx-build -E -b html -D nb_execution_mode=off docs/source docs/html
- Minor wording/consistency fixes.

No code changes.
```

---

## ✅ Quick reminder

Lets write it kindly so future contributors feel brave to join. 🌷
