---
title: alto.ui.settings_panel
parent: api
package: alto.ui
permalink: /api/alto.ui.settings_panel/
---
{% raw %}
The settings panels that slide in beside an exercise, and the small widgets they are built from.

Each exercise with settings has a panel: a menu of rows (Clefs, Range, Key signatures ...) that each lead to a page. Edits
are live: they change the shared settings object, are saved, and a `changed` signal tells the exercise to ask a new
question. Loading and saving the settings is in `alto.ui.exercise_settings`.

**Examples**

```pycon
>>> _key_label(2)
'D  ·  2♯'
>>> row = _Row("Clefs")
>>> row.title.text()
'<b>Clefs</b>'
```

## RangeEditor

```python
RangeEditor(
    key: str,
    *,
    low: int,
    high: int,
    limits: tuple[int, int] | None = None,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

A staff showing the lowest and highest note asked for a clef.

Arrows on the left move the lower bound, arrows on the right move the upper bound.

**Attributes**

- `edited` (*Signal*): Emitted with the clef key, the lowest note and the highest note (as staff steps) after a change.
- `key` (*str*): The clef.
- `low` (*int*): The lowest note asked, as a staff step (`Note.diatonic`).
- `high` (*int*): The highest note asked.
- `limits` (*tuple of (int, int)*): The furthest the bounds may go.
- `staff` (*StaffWidget*): Shows the two notes.

**Examples**

```pycon
>>> editor = RangeEditor("treble", low=28, high=34)
>>> editor.caption_text.text()
'<b>C4 – B4</b>'
```

**Constructor**

Build the editor for a clef's range.

**Parameters**

- `key` (*str*): The clef, a key of `RANGE_LIMITS`.
- `low` (*int*): The lowest note asked, as a staff step. Keyword-only.
- `high` (*int*): The highest note asked. Keyword-only.
- `limits` (*tuple of (int, int) or None, default None*): The furthest the bounds may go, as staff steps; None for the clef's usual limits. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns the editor. Keyword-only.

**Constructor examples**

```pycon
>>> RangeEditor("bass", low=14, high=28).limits == settings.RANGE_LIMITS["bass"]
True
>>> RangeEditor("alto", low=21, high=30, limits=(21, 30)).limits
(21, 30)
```

## KeyDiagram

```python
KeyDiagram(
    keys: set[int] | None = None,
    *,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

A small fork showing which key signatures are selected.

C major is on the left, then two rows of seven dots: 1 to 7 sharps on the top row and 1 to 7 flats on the bottom.
Selected keys are filled, the rest are hollow.

**Attributes**

- `DOT, PITCH, ROW_GAP, PAD` (*float*): The dot radius and the spacing, in pixels.
- `keys` (*set of int*): The selected key signatures: sharps if positive, flats if negative.

**Examples**

```pycon
>>> KeyDiagram({0, 2}).toolTip()
'C, D'
```

**Constructor**

Create the diagram.

**Parameters**

- `keys` (*set of int or None, default None*): The key signatures to show as selected.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> KeyDiagram().keys
set()
```

### KeyDiagram.set_keys

```python
def set_keys(keys: set[int]) -> None
```

Choose which key signatures are shown as selected.

**Parameters**

- `keys` (*set of int*): Sharps if positive, flats if negative.

**Examples**

```pycon
>>> diagram = KeyDiagram()
>>> diagram.set_keys({2, -1, 0})
>>> diagram.toolTip()
'C, D, F'
```

### KeyDiagram.paintEvent

```python
def paintEvent(_: QPaintEvent) -> None
```

Draw a dot for each key signature, filled when selected.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```pycon
>>> KeyDiagram({0, 1, -1}).grab().isNull()
False
```

## Switch

```python
Switch(parent: QWidget | None = None)
```

Bases: `QAbstractButton`

A pill-shaped on/off switch whose knob slides across when toggled.

**Attributes**

- `W, H` (*int*): The switch's size, in pixels.

**Examples**

```pycon
>>> switch = Switch()
>>> switch.setChecked(True)
>>> switch.isChecked()
True
```

**Constructor**

Create a switch that is off.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> Switch().isChecked()
False
```

### Switch.setChecked

```python
def setChecked(on: bool) -> None
```

Turn the switch on or off without animating, as when a setting is loaded.

**Parameters**

- `on` (*bool*): The new state.

**Examples**

```pycon
>>> switch = Switch()
>>> switch.setChecked(True)
>>> switch._pos
1.0
```

### Switch.paintEvent

```python
def paintEvent(_: QPaintEvent) -> None
```

Draw the track, tinted between off and on, and the knob.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```pycon
>>> Switch().grab().isNull()
False
```

### Switch.sizeHint

```python
def sizeHint() -> QSize
```

Return the switch's fixed size.

**Returns**

- *QSize*: `W` by `H`.

**Examples**

```pycon
>>> Switch().sizeHint()
PySide6.QtCore.QSize(42, 24)
```

## SlideStack

```python
SlideStack(parent: QWidget | None = None)
```

Bases: `QStackedWidget`

A stacked widget whose pages slide in from the right (going deeper) or the left (going back).

**Examples**

```pycon
>>> stack = SlideStack()
>>> _ = stack.addWidget(QWidget())
>>> _ = stack.addWidget(QWidget())
>>> stack.sliding
False
```

**Constructor**

Create an empty stack.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> SlideStack().count()
0
```

### SlideStack.sliding

```python
@property
def sliding() -> bool
```

Report whether a page is sliding in.

**Returns**

- *bool*: True from the start of a slide until it finishes.

**Examples**

```pycon
>>> SlideStack().sliding
False
```

### SlideStack.slide_to

```python
def slide_to(index: int) -> None
```

Slide to another page.

Going to a later page slides it in from the right and going back slides it in from the left. A request made during a
slide, or for the page already showing, is ignored.

**Parameters**

- `index` (*int*): The page to go to.

**Examples**

```pycon
>>> stack = SlideStack()
>>> _ = stack.addWidget(QWidget())
>>> _ = stack.addWidget(QWidget())
>>> stack.slide_to(1)
>>> stack.sliding
True
```

## ExerciseSettingsPanel

```python
class ExerciseSettingsPanel(QWidget)
```

What every exercise's settings pane has in common: it says when a setting has been edited.

**Attributes**

- `changed` (*Signal*): Emitted after any setting is edited that changes what is asked, so the exercise asks a new question.
- `restyled` (*Signal*): Emitted after a setting is edited that changes only how the exercise looks, so the question stays and the picture is drawn again.

**Examples**

```pycon
>>> panel = ExerciseSettingsPanel()
>>> got = []
>>> _ = panel.changed.connect(lambda: got.append(1))
>>> panel.changed.emit()
True
>>> got
[1]
```

### ExerciseSettingsPanel.refresh_limits

```python
def refresh_limits(
    mode: str,
    *,
    self_grading: bool = False,
) -> None
```

Update scheduling controls for the active scheduler and profile.

**Parameters**

- `mode` (*str*): Selected question scheduler.
- `self_grading` (*bool*): Disable Next Question when a passing grade advances the exercise.

**Examples**

```pycon
Switching to ASRS hides the row and leaves its submenu.
```

## NoteNameSettingsPanel

```python
NoteNameSettingsPanel(
    cfg: NoteNameSettings,
    *,
    parent: QWidget | None = None,
)
```

Bases: `_StaffRangePanel`

The settings of the note identification exercise: a menu leading to a page for each group of settings.

Two layers: the menu (Clefs, Range, Key signatures, Note values, Note names, Accidentals and Octave) and a page for
each. Edits are live: each changes the settings, saves them and emits `changed`.

**Attributes**

- `cfg` (*NoteNameSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages.
- `boxes` (*dict of str to QCheckBox*): The clef checkboxes.
- `key_boxes` (*dict of int to QCheckBox*): The key signature checkboxes.
- `value_boxes` (*dict of str to QCheckBox*): The note value checkboxes.
- `naming_radios` (*dict of str to QRadioButton*): The letters and solfège choices, plus caret and function notation in the Scale degrees group.
- `octave_row` (*_ToggleRow*): Whether the answer must include the written octave.
- `range_editors` (*dict of str to RangeEditor*): The range editor of each clef in use, built when the Range page opens.

**Examples**

```pycon
>>> panel = NoteNameSettingsPanel(NoteNameSettings())
>>> panel.cfg.active_clefs()
['treble', 'bass']
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

- `cfg` (*NoteNameSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> panel = NoteNameSettingsPanel(NoteNameSettings())
>>> panel.stack.count()  # the menu and five pages
6
```

## KeyChecklist

```python
KeyChecklist(
    selected: set[int],
    *,
    allow_empty: bool = False,
    counts_only: bool = False,
    key_names: dict[int, str] | None = None,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

Checkboxes for the 15 major keys, flats on the left and sharps on the right.

At least one stays checked. Each is labeled with a picture of its signature.

**Attributes**

- `changed` (*Signal*): Emitted after a box is checked or unchecked.
- `boxes` (*dict of int to QCheckBox*): The checkbox of each key signature, from -7 (seven flats) to 7 (seven sharps).

**Examples**

```pycon
>>> KeyChecklist({0, 2}).selected() == {0, 2}
True
```

**Constructor**

Build the checklist.

**Parameters**

- `selected` (*set of int*): The key signatures to check initially.
- `allow_empty` (*bool, default False*): Allow every key to be unchecked. Keyword-only.
- `counts_only` (*bool, default False*): Label each box with its accidental count instead of drawing a signature. Keyword-only.
- `key_names` (*dict of int to str or None, default None*): Key names to display beside the signature diagrams. With None, show only diagrams. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> len(KeyChecklist({0}).boxes)
15
```

### KeyChecklist.selected

```python
def selected() -> set[int]
```

Return the checked key signatures.

**Returns**

- *set of int*: Sharps if positive, flats if negative.

**Examples**

```pycon
>>> KeyChecklist({-3, 1}).selected() == {-3, 1}
True
```

## KeySignaturePage

```python
KeySignaturePage(
    enabled: bool,
    *,
    selected: set[int],
    allow_empty: bool = False,
    key_names: dict[int, str] | None = None,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

The key signature sub-page: a switch for using key signatures at all, and the keys to draw from.

**Attributes**

- `changed` (*Signal*): Emitted after the switch or a key is changed.
- `switch_row` (*_ToggleRow*): The "Use key signatures" switch.
- `checklist` (*KeyChecklist*): The keys; only enabled while the switch is on.

**Examples**

```pycon
>>> page = KeySignaturePage(True, selected={0, 1})
>>> page.enabled(), page.selected() == {0, 1}
(True, True)
```

**Constructor**

Build the page.

**Parameters**

- `enabled` (*bool*): Whether key signatures are on.
- `selected` (*set of int*): The key signatures to check initially. Keyword-only.
- `allow_empty` (*bool, default False*): Allow every key to be unchecked. Keyword-only.
- `key_names` (*dict of int to str or None, default None*): Key names to display beside the signature diagrams. With None, show only diagrams. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> page = KeySignaturePage(False, selected={0})
>>> page.checklist.isEnabled()
False
```

### KeySignaturePage.enabled

```python
def enabled() -> bool
```

Report whether key signatures are switched on.

**Returns**

- *bool*: True if the switch is on.

**Examples**

```pycon
>>> KeySignaturePage(True, selected={0}).enabled()
True
```

### KeySignaturePage.selected

```python
def selected() -> set[int]
```

Return the checked key signatures.

**Returns**

- *set of int*: Sharps if positive, flats if negative.

**Examples**

```pycon
>>> KeySignaturePage(True, selected={-2, 0}).selected() == {-2, 0}
True
```

## KeyboardSettingsPanel

```python
KeyboardSettingsPanel(
    cfg: settings.KeyboardSettings,
    *,
    parent: QWidget | None = None,
)
```

Bases: `ExerciseSettingsPanel`

The settings of the keyboard exercise: a menu with a page for the range of keys.

The menu has Range, Black keys, Octave number and Key signatures. Edits are live: each changes the settings, saves them
and emits `changed`.

**Attributes**

- `cfg` (*KeyboardSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages.
- `span` (*KeyboardSpan*): The miniature piano on the Range page, which can be dragged to choose the keys.
- `low_label, high_label` (*QLabel*): The names of the lowest and highest key asked.
- `key_page` (*KeySignaturePage*): The key signature sub-page.

**Examples**

```pycon
>>> panel = KeyboardSettingsPanel(settings.KeyboardSettings())
>>> panel.low_label.text(), panel.high_label.text()
('C3', 'C5')
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

- `cfg` (*KeyboardSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> KeyboardSettingsPanel(settings.KeyboardSettings()).stack.count()  # the menu, the range and the keys
3
```

## NoteConstructionSettingsPanel

```python
NoteConstructionSettingsPanel(
    cfg: settings.ConstructionSettings,
    *,
    parent: QWidget | None = None,
)
```

Bases: `ExerciseSettingsPanel`

The settings of the note construction exercise: a menu with a page for the staff and one for the keys.

The menu has Clefs, Staff Key, Question Type, and Octave. Edits are live: each changes the settings, saves them and
emits `changed`.

**Attributes**

- `cfg` (*ConstructionSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages.
- `boxes` (*dict of str to QCheckBox*): The clef checkboxes, including the grand staff.
- `key_tabs` (*QTabWidget*): The key signature sub-page.

**Examples**

```pycon
>>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
>>> sorted(panel.boxes)[:3]
['alto', 'baritone', 'bass']
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

- `cfg` (*ConstructionSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> NoteConstructionSettingsPanel(settings.ConstructionSettings()).stack.count()
4
```

## ChoiceChecklist

```python
ChoiceChecklist(
    groups: list[tuple[str, list[tuple[object, str]]]],
    *,
    selected: set,
    allow_empty: bool = False,
    positions: Mapping[object, tuple[int, int]] | None = None,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

Checkboxes for a list of choices, optionally under headings and allowing an empty selection.

**Attributes**

- `changed` (*Signal*): Emitted after a box is checked or unchecked.
- `allow_empty` (*bool*): Whether all choices may be unchecked.
- `boxes` (*dict*): The checkbox of each choice, by its key.

**Examples**

```pycon
>>> groups = [("Triads", [("major", "Major"), ("minor", "Minor")]), ("", [("x", "Other")])]
>>> checklist = ChoiceChecklist(groups, selected={"major"})
>>> checklist.selected()
{'major'}
```

**Constructor**

Build the checklist.

**Parameters**

- `groups` (*list of tuple of (str, list of tuple of (object, str))*): The headings and, under each, the choices as (key, label); an empty heading shows none.
- `selected` (*set*): The keys to check initially. Keyword-only.
- `allow_empty` (*bool, default False*): Allow all choices to be unchecked. Keyword-only.
- `positions` (*mapping or None, default None*): Optional (row, column) for each key within its group. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> checklist = ChoiceChecklist([("", [(0, "Root"), (1, "1st")])], selected={0})
>>> # noinspection PyTypeChecker
>>> sorted(checklist.boxes)
[0, 1]
```

### ChoiceChecklist.selected

```python
def selected() -> set
```

Return the checked choices.

**Returns**

- *set*: The keys of the checked boxes.

**Examples**

```pycon
>>> ChoiceChecklist([("", [(0, "Root"), (1, "1st")])], selected={0, 1}).selected()
{0, 1}
```

## IntervalSettingsPanel

```python
IntervalSettingsPanel(
    cfg: settings.IntervalSettings,
    *,
    prefix: str = 'intervals',
)
```

Bases: `_StaffRangePanel`

Choose the notation and answer format for written intervals.

**Examples**

```pycon
>>> IntervalSettingsPanel(settings.IntervalSettings()).stack.count()
10
```

**Constructor**

Build the interval settings menu with direction choices under Melodic.

**Parameters**

- `cfg` (*IntervalSettings*): The interval exercise settings.
- `prefix` (*str*): Settings-store group for identification or construction.

**Constructor examples**

```pycon
>>> IntervalSettingsPanel(settings.IntervalSettings()).quality_row.value.text()
'Interval and Quality'
```

## KeyboardIntervalSettingsPanel

```python
KeyboardIntervalSettingsPanel(
    cfg: settings.KeyboardIntervalSettings,
    *,
    parent: QWidget | None = None,
)
```

Bases: `ExerciseSettingsPanel`

Range and interval selection pages for keyboard interval identification.

**Attributes**

- `cfg` (*KeyboardIntervalSettings*): The settings being edited.
- `stack` (*SlideStack*): The settings menu, range page, and interval page.
- `span` (*KeyboardSpan*): The draggable range selector.
- `interval_range` (*QWidget*): The interval range controls directly below Select all.
- `interval_slider` (*IntervalRangeSlider*): The two-handle interval selector.
- `interval_low_label, interval_high_label` (*FieldComboBox*): Clickable endpoint notation with scrollable interval lists.
- `interval_page` (*ChoiceChecklist*): The interval checkboxes, keyed by distance in half steps.

**Examples**

```pycon
>>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
>>> panel.stack.count()
4
```

**Constructor**

Build the range selector and interval checklist.

**Parameters**

- `cfg` (*KeyboardIntervalSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
>>> panel.low_label.text(), panel.high_label.text()
('C3', 'C5')
```

## ArpeggioSettingsPanel

```python
ArpeggioSettingsPanel(
    cfg: settings.ArpeggioSettings,
    *,
    parent: QWidget | None = None,
)
```

Bases: `ExerciseSettingsPanel`

The settings of the arpeggio exercise: a menu with a page for each group of settings.

The menu has Clefs, Arpeggio types, Inversions and Key signatures. Edits are live: each changes the settings, saves them
and emits `changed`.

**Attributes**

- `cfg` (*ArpeggioSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages.
- `boxes` (*dict of str to QCheckBox*): The clef checkboxes.
- `types` (*ChoiceChecklist*): The chord types.
- `inversions` (*ChoiceChecklist*): The inversions.
- `key_page` (*KeySignaturePage*): The key signature sub-page.

**Examples**

```pycon
>>> panel = ArpeggioSettingsPanel(settings.ArpeggioSettings())
>>> panel.types_row.value.text()
'4 of 9'
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

- `cfg` (*ArpeggioSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> ArpeggioSettingsPanel(settings.ArpeggioSettings()).stack.count()  # the menu and four pages
5
```

## KeySignatureSettingsPanel

```python
KeySignatureSettingsPanel(
    cfg: settings.KeySignatureSettings,
    *,
    prefix: str = 'keySignatures',
    keys_title: str = 'Key signatures',
    parent: QWidget | None = None,
)
```

Bases: `ExerciseSettingsPanel`

The settings of a key signature exercise: a menu with a page for each group of settings.

The same panel serves key signature identification, key signature construction and both scale exercises, each saving
under its own name.

The menu has Clefs, Scales and Key signatures. Both scale exercises have independent staff and scale key choices;
construction also has Octave and Steps switches. Edits are live: each changes the settings, saves them and emits `changed`.

**Attributes**

- `cfg` (*KeySignatureSettings*): The settings being edited.
- `prefix` (*str*): What the settings are saved under, such as "keySignatures".
- `stack` (*SlideStack*): The menu and its pages.
- `boxes` (*dict of str to QCheckBox*): The clef checkboxes.
- `modes` (*ChoiceChecklist*): The scales (major, minor and the modes).
- `key_list` (*KeyChecklist*): The key signatures (of the scales, in scale construction).
- `staff_key_list` (*KeyChecklist or None*): The key signatures that may be drawn on the staff; only scale construction has it.

**Examples**

```pycon
>>> panel = KeySignatureSettingsPanel(settings.KeySignatureSettings())
>>> panel.modes_row.value.text()
'2 of 7'
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

- `cfg` (*KeySignatureSettings*): The settings to edit.
- `prefix` (*str, default "keySignatures"*): What the settings are saved under. Keyword-only.
- `keys_title` (*str, default "Key signatures"*): Title for the signature checklist when the exercise uses a single list. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> KeySignatureSettingsPanel(settings.KeySignatureSettings()).stack.count()  # the menu and three pages
4
```

## NotationSettingsPanel

```python
NotationSettingsPanel()
```

Bases: `ExerciseSettingsPanel`

Choose the question type and the notation terms to practice.

**Examples**

```pycon
>>> "Trill" in NotationSettingsPanel().terms.boxes
True
```

**Constructor**

Build the settings menu and its Question Type and Terms pages.

**Constructor examples**

```pycon
>>> len(NotationSettingsPanel().terms.boxes) == len(settings.NOTATION_TERMS)
True
```

## ClefBasicsSettingsPanel

```python
ClefBasicsSettingsPanel(
    cfg: settings.ClefBasicsSettings,
    *,
    parent: QWidget | None = None,
)
```

Bases: `ExerciseSettingsPanel`

The settings of the clef basics exercise: a menu with two pages, Question Type and Clefs.

Question Type chooses between Clef Construction (put a named clef on a blank staff) and Clef Identification (name the clef on
a staff). Clefs lists the clefs in the same groups as the other exercises, with the French violin and subbass clefs, which
only this exercise has, at the bottom. Edits are live: each changes the settings, saves them and emits `changed`.

**Attributes**

- `cfg` (*ClefBasicsSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its two pages.
- `types` (*dict of str to QRadioButton*): The choice of question, by key of `CLEF_QUESTION_TYPES`.
- `boxes` (*dict of str to QCheckBox*): The checkbox of each clef.

**Examples**

```pycon
>>> panel = ClefBasicsSettingsPanel(settings.ClefBasicsSettings())
>>> panel.stack.count()  # the menu and two pages
3
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

- `cfg` (*ClefBasicsSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> panel = ClefBasicsSettingsPanel(settings.ClefBasicsSettings(clefs={"subbass"}))
>>> panel.boxes["subbass"].isChecked(), list(panel.boxes)[-2:]
(True, ['french', 'subbass'])
```

## settings_inversion_names

```python
def settings_inversion_names() -> tuple[str, ...]
```

Return the inversions as they are written in the settings.

**Returns**

- *tuple of str*: 'Root position', '1st inversion', '2nd inversion' and '3rd inversion'.

**Examples**

```pycon
>>> settings_inversion_names()
('Root position', '1st inversion', '2nd inversion', '3rd inversion')
```

## CircleSettingsPanel

```python
CircleSettingsPanel(
    cfg: settings.CircleSettings,
    *,
    parent: QWidget | None = None,
)
```

Bases: `ExerciseSettingsPanel`

The settings of the circle of fifths exercise: which kinds of question to ask, and the colors of the circle.

The menu has two rows. Questions opens a page of switches. Colors opens a page of color schemes to choose from, with a
button to make one of your own, which opens an editor. Edits are live: each changes the settings and saves them. A new kind
of question emits `changed`, and a new color scheme emits `restyled`, which keeps the question.

**Attributes**

- `cfg` (*CircleSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages: the menu, the questions, the color schemes and the editor of a scheme.
- `questions_row` (*_Row*): The menu row for the questions.
- `colors_row` (*_Row*): The menu row for the colors; its value is the name of the chosen scheme.
- `questions` (*ChoiceChecklist*): The kinds of question: relative major, relative minor and Roman numerals.
- `schemes` (*SchemePage*): The color schemes.
- `editor` (*SchemeEditor*): The editor of a scheme of your own.

**Examples**

```pycon
>>> panel = CircleSettingsPanel(settings.CircleSettings())
>>> panel.questions_row.value.text(), panel.colors_row.value.text()
('3 of 3', 'Cyan to indigo')
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

- `cfg` (*CircleSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> CircleSettingsPanel(settings.CircleSettings()).stack.count()  # the menu, the questions, the colors and the editor
4
```

## PackSettingsPanel

```python
PackSettingsPanel(
    exercise: type[PackExercise],
    *,
    parent: QWidget | None = None,
)
```

Bases: `_StaffRangePanel`

The settings a plugin declared for one of its note exercises, drawn from a fixed set of controls.

The plugin picks which controls appear: a switch for its own sound, a range selector on one clef, and switches for
accidentals and for the octave. Edits are live: each changes the options, saves them and emits `changed`.

**Attributes**

- `exercise` (*type of PackExercise*): The exercise whose options are edited.
- `cfg` (*PackExerciseSettings*): The options being edited.
- `range_row` (*_Row*): The Range row, present only if the plugin declared a range.
- `sound_row` (*_ToggleRow or None*): The plugin sound switch, if declared.
- `accidentals_row` (*_ToggleRow or None*): The accidentals switch, if declared.
- `octave_row` (*_ToggleRow or None*): The octave switch, if declared.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     controls = {"octave": True}
>>> panel = PackSettingsPanel(Demo)
>>> panel.octave_row is not None and not hasattr(panel, "range_row")
True
>>> _ = settings.pack_exercises.pop("Demo")
```

**Constructor**

Build the menu and, if the plugin offers a range, its page.

**Parameters**

- `exercise` (*type of PackExercise*): The exercise to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> class Sounds(PackExercise):
...     controls = {"sound": "Demo sound"}
>>> panel = PackSettingsPanel(Sounds)
>>> panel.stack.count()
2
>>> _ = settings.pack_exercises.pop("Sounds")
```

## PackKeyboardSettingsPanel

```python
PackKeyboardSettingsPanel(
    exercise: type[PackExercise],
    *,
    parent: QWidget | None = None,
)
```

Bases: `ExerciseSettingsPanel`

The settings a plugin declared for a keyboard interval exercise: its sound, the range of keys, and the intervals.

The plugin picks which controls appear. Edits are live: each changes the options, saves them and emits `changed`.

**Attributes**

- `exercise` (*type of PackExercise*): The exercise whose options are edited.
- `cfg` (*PackExerciseSettings*): The options being edited.
- `stack` (*SlideStack*): The settings menu, then the range page and the intervals page, as the plugin offers them.
- `sound_row` (*_ToggleRow or None*): The plugin sound switch, if declared.
- `range_row` (*_Row or None*): The Range row, if declared.
- `span` (*KeyboardSpan or None*): The draggable range selector, if a range is declared.
- `interval_page` (*ChoiceChecklist or None*): The interval checkboxes, keyed by interval name, if a choice of intervals is declared.
- `manual_page` (*ChoiceChecklist or None*): The keyboard checkboxes, keyed by keyboard name, if a choice of manuals is declared.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     controls = {"range": True, "intervals": True, "manuals": True}
...     spec = {"type": "keyboard-intervals"}
...     key_span, key_default = (28, 89), (48, 72)
...     interval_names = ("m2", "M2", "m3")
...     manual_names = ("Upper manual", "Lower manual")
>>> panel = PackKeyboardSettingsPanel(Demo)
>>> panel.stack.count(), panel.low_label.text(), panel.high_label.text()
(4, 'C3', 'C5')
>>> _ = settings.pack_exercises.pop("Demo")
```

**Constructor**

Build the menu and the pages the plugin offers.

**Parameters**

- `exercise` (*type of PackExercise*): The exercise to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```pycon
>>> class Sounds(PackExercise):
...     controls = {"sound": "Demo sound"}
...     spec = {"type": "keyboard-intervals"}
>>> panel = PackKeyboardSettingsPanel(Sounds)
>>> panel.stack.count()
2
>>> _ = settings.pack_exercises.pop("Sounds")
```

### PackKeyboardSettingsPanel.flush

```python
def flush() -> None
```

Save the options and ask a new question now, if an edit is waiting.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     controls = {"sound": "Demo sound"}
...     spec = {"type": "keyboard-intervals"}
>>> panel = PackKeyboardSettingsPanel(Demo)
>>> panel._sound_chosen("piano")
>>> panel.flush()
>>> panel._commit_timer.isActive()
False
>>> _ = settings.pack_exercises.pop("Demo")
```

### PackKeyboardSettingsPanel.hideEvent

```python
def hideEvent(event: QHideEvent) -> None
```

Keep an edit that is still waiting when the panel closes.

**Parameters**

- `event` (*QHideEvent*): The event.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     controls = {"sound": "Demo sound"}
...     spec = {"type": "keyboard-intervals"}
>>> panel = PackKeyboardSettingsPanel(Demo)
>>> panel._sound_chosen("piano")
>>> panel.show()
>>> panel.hide()
>>> panel._commit_timer.isActive()
False
>>> _ = settings.pack_exercises.pop("Demo")
```

## settings_panel_for

```python
def settings_panel_for(
    exercise: Exercise,
    *,
    learner: Learner | None = None,
) -> ExerciseSettingsPanel
```

Return the settings panel for an exercise.

**Parameters**

- `exercise` (*Exercise*): The exercise.
- `learner` (*Learner or None*): Profile whose calendar limits can be overridden.

**Returns**

- *ExerciseSettingsPanel*: A panel with the exercise options and the shared Next Question setting.

**Examples**

```pycon
>>> from alto.exercises.library import IntervalNames, NoteNames
>>> type(settings_panel_for(NoteNames())).__name__
'NoteNameSettingsPanel'
>>> type(settings_panel_for(IntervalNames())).__name__
'IntervalSettingsPanel'
```
{% endraw %}
