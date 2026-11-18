# Working preferences

- Use American English spelling, grammar, vocabulary, and idioms in code, comments, docstrings, documentation, and user-facing text.
- Use branches in the existing Alto repository for new work.
- Do not create nested Git repositories or separate worktrees unless the user explicitly requests them.

## UI consistency

- Default new exercise options to a settings row that shows the current selection and opens a titled submenu with Back.
  Use radio buttons for one choice and checkboxes for independent choices. A simple on/off option can use an inline switch.
  Follow the [exercise option procedure](docs/development.md#adding-an-exercise-option).

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

- For exercise button groups described by a label, place the label above the buttons, rather than beside them.
  Keep the label and its buttons visible or hidden together, and apply this consistently to answer and input controls.


## Glossary entries

- Match existing glossary entries with a definition, a short explanation, relevant practice links, and an interactive visual
  example. Use the shared example controls to cycle through examples and play their notes when the concept involves sound.
- Choose an illustration that lets the learner see or hear the defining feature. For an interval, show both endpoints.
  Derive playback and step labels from the displayed pitches. Inspect rendered examples at narrow and wide pane sizes,
  including ledger lines, accidentals, and key signatures where relevant.

## Lessons and exercises

- Organize lessons around a musical concept. Aim for a first pass of 20 minutes or less, including guided activities.
- Order lesson tiles from beginner to advanced. Start with no assumed knowledge and introduce each prerequisite before
  lessons that use it.
- Define each new musical term in plain language at its first use unless an earlier lesson in the sequence already
  taught it. Check captions, controls, questions, and hints as well as the lesson text.
- Scope each exercise to a specific technique the learner can practice repeatedly. Map exercises to lessons by the
  skills they reinforce. Several exercises can share a lesson, and an exercise can draw on several lessons.
- When designing or revising either, follow the [lesson and exercise authoring procedure](docs/development.md#designing-lessons-and-exercises).
