# Code style for Alto

Use American English spelling, grammar, vocabulary, and idioms in code, comments, docstrings, documentation, and user-facing text.

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

## UI consistency

- Match dropdowns to Alto's existing controls. Use `FieldComboBox` from `alto/ui/dropdown.py`; it marks the field for the
  shared theme-aware styles in `alto/ui/style.py` and rounds the popup's outer window as well as its item view.
- Dropdown popup corners must be visibly rounded. Styling only the closed field or inner list is insufficient: retain
  the shared popup mask and verify the open menu, including after resizing and scrolling.
- Preserve the shared rounded border, padding, chevron, focus highlight, and popup colors. Avoid borderless native controls
  or local style overrides unless the user explicitly requests a different appearance.
- Keep long lists scrollable and verify that the closed control, longest notation, and popup fit their intended pane with
  the application stylesheet applied. Use palette colors so light, dark, and custom themes remain consistent.

- Match arrow buttons to Alto's shared button styling in `alto/ui/style.py`. Reuse `_arrow()` in settings panels;
  elsewhere, mark `QToolButton` controls with `setProperty("arrowButton", True)`.
- Preserve the shared rounded border, heavier lower edge, palette colors, and hover, focus, pressed, and disabled states.
  Avoid local styling and hardcoded arrow colors unless the user explicitly requests a different appearance.
- Give arrow buttons descriptive tooltips and accessible names. Preserve auto-repeat for endpoint adjustments and check
  that buttons and adjacent labels fit the actual pane with the application stylesheet applied.

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
- Term names: use lowercase in the list and entry heading unless a term is a proper noun. Preserve the entry's defined
  casing rather than automatically capitalizing headings.
- Boxes: use consistent rounded corners, thin borders, and generous whitespace between edges and content. Match the
  Lessons panels' theme background (`palette(window)`) in the term list, description, related activities, and search field.
- Alignment: the description box's top edge aligns with the search field's top edge; the related activities box's bottom
  edge aligns with the term list's bottom edge. Avoid extra inner column margins that offset these edges.
- Description layout: use one large rounded box for the explanation and any interactive example. Keep examples compact
  rather than stretching a staff with only a few notes across the page. On wide layouts, wrap explanation text around the
  example, with its top flush with the first paragraph below the term heading. On narrow layouts, stack the example above
  the text within the same box.
- Content: provide more depth than a textbook's back-of-book glossary, while keeping each term to one concise page.
  Explain the concept, practical reading or listening guidance, and common pitfalls. Small notation examples and modest
  interactivity are welcome; avoid turning an entry into a multi-page lesson.
- Examples: the current entries have a staff illustration, a Next example action, and a Hear note action. Keep examples
  relevant to the term and identify the written pitch and clef.
- Related activities: use an **Exercises / Lessons** switch to toggle clickable activity tiles, rather than text links.
  Display tiles horizontally. Clicking a tile opens that exercise or lesson directly.
- Theme changes: preserve the current page instead of navigating away from the glossary. Retain the selected term,
  search filter, example index, related activities tab, and description scroll position, as well as the previous screen
  reached through Back. Bind deferred layout and scroll callbacks to their widgets' lifetimes.
- Initial terms: pitch, octave, octave register, staff, ledger lines, clef, grand staff.
- Implementation: `alto/ui/glossary.py` contains entries, examples, filtering, and activity tiles; `alto/ui/main_window.py`
  owns the toolbar entry and navigation; `alto/ui/icons.py` contains the chosen icon. Related activities currently use
  existing exercise cards and the Clef Basics lesson. The glossary itself is a reference page, not a lesson.
