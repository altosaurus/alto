# Code style for Alto

These are the author's rules. Ruff enforces some of them; the rest are only enforced by following this file. When Ruff cannot
enforce a rule, follow it anyway in every line you write or touch.

## Imports (not enforceable by Ruff)

- A `from` import of **two or more names** is written one name per line, in parentheses, with a trailing comma:

  ```python
  from alto.learning.database import (
      Database,
      ItemRecord,
      Profile,
  )
  ```

  The trailing comma is what makes Ruff's isort keep it that way. A one-name import stays on one line.
- Absolute imports only, never `from .x import y` (Ruff `TID252`).
- Every import at the top of the file, never inside a function (Ruff `PLC0415`). Doctests import what they use. Break import
  cycles with a registration hook (see `on_redraw`), not a local import.
- Sorted like isort, with `alto` as its own section after the third-party packages (Ruff `I`).
- In `conftest.py` files the imports after the environment setup carry `# noqa: E402`, on the first line of the statement.

## Layout (Ruff `format` and `check`, run in that order)

- Anything with several elements (a list, dict, call, tuple or signature) that does not fit on a line goes one element per
  line with a trailing comma. Function definitions with two or more parameters, and calls, collections and tuples with four or
  more elements, are one per line. Short calls stay on one line.
- Only the first parameter of a function may be positional; the rest are keyword-only, and every call names them
  (`Note(3, letter=1)`), tests included.
- Line length 130, double quotes.

## Docstrings and types

- Every module, class, function, method, nested function and test has a NumPy-style docstring. The text starts on the line
  after the opening `"""`.
- Describe every parameter, with its type, and every return or yield. Add an `Examples` section that runs as a doctest
  (not needed under `tests/`). Add `Raises` for errors the function raises.
- Every signature is fully annotated. Do not use `Any`; give a real type.

## Warnings

- No warnings in any code you write, in Ruff, Pyright (`sh scripts/typecheck.sh`) or PyCharm. Lint every file you create or
  change with the PyCharm MCP `lint_files` tool and fix what it reports. Fix the cause where you can; for a real false
  positive use a narrow `# noinspection <Inspection>` comment (in a doctest, a `>>> # noinspection <Inspection>` line).
- `docs/development.md` explains the PyCharm settings a fresh clone needs.

## Validation checkpoints

If you changed a docstring or a public signature, run `python scripts/api_docs.py` so `docs/api` matches.

During development, format and lint the changed Python files and run the tests directly affected by the change. Use
type checking when signatures or types change, and PyCharm inspections on changed Python files. Documentation-only
changes need only relevant documentation checks. Do not run the full test suite after every prompt or minor edit.

Run `ruff format .`, `ruff check .`, `sh scripts/typecheck.sh` and `pytest` at commit, PR and release checkpoints, and
after broad changes whose effects cannot be covered confidently by focused checks. Reuse passing checkpoint results
when the code has not changed; after small follow-up edits, rerun the affected checks rather than starting over.

Broaden validation when a failure or an unresolved concern warrants it. Report which checks ran and any limitations.

## Git

Commits are the author's alone: no Claude attribution lines. Stage files by explicit path and commit or push only when asked.

## Glossary design decisions

These choices were made with the user; preserve them when continuing work on the glossary.

- Entry point: a button in the top-right toolbar, alongside Statistics and Database. The glossary is not a Lessons tile.
- Icon: use `icons.GLOSSARY`, the thin-stroke **A with horizontal text lines** (option 4 from the icon comparison).
  It follows the toolbar's text color and turns blue when active; only the drawing is highlighted, not the button background.
- Navigation: clicking the toolbar button again returns to the previous screen. Use the shared arrow Back button beside
  the main search bar, and support Escape.
- Layout: a left-hand list box with a search field above it; selecting a term shows its entry in the main pane.
  Include a magnifying glass in the search field, a clear action, and an accessible search label.
- List: sort terms alphabetically. Give rows enough height and spacing that selection highlights do not overlap neighboring
  words. Filtering selects a visible match and shows an explicit empty state when no terms match.
- Content: provide more depth than a textbook's back-of-book glossary, while keeping each term to one concise page.
  Explain the concept, practical reading or listening guidance, and common pitfalls. Small notation examples and modest
  interactivity are welcome; avoid turning an entry into a multi-page lesson.
- Examples: the current entries have a staff illustration, a Next example action, and a Hear note action. Keep examples
  relevant to the term and identify the written pitch and clef.
- Related activities: use an **Exercises / Lessons** switch to toggle clickable activity tiles, rather than text links.
  Display tiles horizontally. Clicking a tile opens that exercise or lesson directly.
- Initial terms: pitch, octave, octave register, staff, ledger lines, clef, grand staff.
- Implementation: `alto/ui/glossary.py` contains entries, examples, filtering, and activity tiles; `alto/ui/main_window.py`
  owns the toolbar entry and navigation; `alto/ui/icons.py` contains the chosen icon. Related activities currently use
  existing exercise cards and the Clef Basics lesson. The glossary itself is a reference page, not a lesson.
