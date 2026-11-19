# Working preferences

- Use American English spelling, grammar, vocabulary, and idioms in code, comments, docstrings, documentation, and user-facing text.
- Use branches in the existing Alto repository for new work.
- Do not create nested Git repositories or separate worktrees unless the user explicitly requests them.

## Prose style

- Prefer short noun phrases for section headings in documentation, lessons, and in-app help. Name the specific topic
  readers will find in the section. Use parallel phrasing for related headings, such as “Major keys with sharps” and
  “Major keys with flats.”
- Use the body text for directions. Under “Major keys with sharps,” the first instruction might be “Find the last sharp
  in the signature, then go up a half step.” Exercise prompts and button labels can also use direct verbs.

## UI consistency

- Use `CORRECT_ANSWER_COLOR` from `alto/ui/colors.py` for correct-answer feedback, including animations on sounding notes.
  Correct-answer animations default to green in every theme. Use another color only when explicitly requested.
- When a correct answer plays notes, use the playback step callback to highlight exactly the pitches sounding at each onset.
  Highlight chord tones together, move the highlight for a melody, and clear it when playback ends or is interrupted.
  Follow the shared **Next Question** setting. **Immediately** plays the answer audio without highlighting the music, **Wait** requires Next,
  and **After Animation** advances after feedback. Use the same animation timing when muted.

- Include **Buttons** with **Limited**, **Button count**, and **All** by default whenever buttons are answer choices.
  Use `ChoiceExercise` for new multiple-choice exercises. Show this option in button-answer modes. Editing controls
  and a standalone **Answer** submission button do not qualify.

- For exercise settings, interpret names such as **Clef** or **Clefs**, **Staff Key**, and **Buttons** using the
  [exercise option vocabulary](docs/development.md#exercise-option-vocabulary). Start with the named exercise or
  the listed template and reuse its controls and behavior. “Propose options” asks for a comparison of applicable
  settings. “Add” or “use” asks for implementation. See [how to request exercise options](docs/development.md#requesting-exercise-options).

- Default new exercise options to a settings row that shows the current selection and opens a titled submenu with Back.
  Use radio buttons for one choice and checkboxes for independent choices. A simple on/off option can use an inline switch.
  Group submenu choices at the top with consistent row spacing. Extra window height belongs below the group.
  Use the shared scroll area for long option lists and check the layout at short and tall window sizes.
  Follow the [exercise option procedure](docs/development.md#adding-an-exercise-option).

- Match dropdowns to Alto's existing controls. Use `FieldComboBox` from `alto/ui/dropdown.py`; it marks the field for the
  shared theme-aware styles in `alto/ui/style.py` and rounds the popup's outer window as well as its item view.
- Dropdown popup corners must be visibly rounded. Styling only the closed field or inner list is insufficient: retain
  the shared popup mask and verify the open menu, including after resizing and scrolling.
- Preserve the shared rounded border, padding, chevron, focus highlight, and popup colors. Avoid borderless native controls
  or local style overrides unless the user explicitly requests a different appearance.
- Keep long lists scrollable and verify that the closed control, longest notation, and popup fit their intended pane with
  the application stylesheet applied. Use palette colors so light, dark, and custom themes remain consistent.

- Use a standard `QSpinBox` for editable integer settings. Alto’s application stylesheet supplies the rounded field,
  centered value, and stacked step arrows. Give the field a label and accessible name, and check that its widest
  value and both arrows fit in the settings pane. See the [numeric field guidelines](docs/guide/styling.md#numeric-fields).

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

- Keep lesson staves left-aligned. Size each white box to the wider of the music and its caption, with a small margin
  around both. Once the example fits, widening the pane should leave extra space outside the box. In a narrow pane,
  let long captions and phrases wrap. Check both widths against the [lesson engraving guidelines](docs/development.md#engraving-lesson-examples).
- Route musical examples and exercise feedback through `alto.audio.sounds`. Use the shared instrument gain for every
  playback path so the same note on the same instrument plays at the same level throughout Alto.
- For playable staff examples, highlight each written note at its audio onset. Light chord tones together and clear the
  playback highlight when the sample ends or the learner leaves the example.
- Group paired lesson staves side by side with a vertical divider and put playback beneath them on the same white
  notation paper. Extend the paper to the panel border in every theme.
  Align the panel with the top of the text on wide panes and insert it after the opening paragraph on narrow panes.
- Organize lessons around a musical concept. Aim for a first pass of 20 minutes or less, including guided activities.
- Order lesson tiles from beginner to advanced. Start with no assumed knowledge and introduce each prerequisite before
  lessons that use it.
- Define each new musical term in plain language at its first use unless an earlier lesson in the sequence already
  taught it. Check captions, controls, questions, and hints as well as the lesson text.
- Scope each exercise to a specific technique the learner can practice repeatedly. Map exercises to lessons by the
  skills they reinforce. Several exercises can share a lesson, and an exercise can draw on several lessons.
- When designing or revising either, follow the [lesson and exercise authoring procedure](docs/development.md#designing-lessons-and-exercises).
