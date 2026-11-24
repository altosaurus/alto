---
title: alto.ui.settings_menu
parent: api
package: alto.ui
permalink: /api/alto.ui.settings_menu/
---
{% raw %}
The building blocks of the settings panels that slide in beside an
exercise.

A panel is a menu of rows (Clefs, Range, Key signatures ...) that each
lead to a page, in a `SlideStack`. This module has the
rows, switches, checklists and editors those pages are made of, and the
panels' shared base classes: `ExerciseSettingsPanel`
(navigation and saving), `ClefsPanel` (a Clefs page) and
`StaffRangePanel` (a Range page per clef). The panels themselves are
in `alto.ui.settings_panel` and `alto.ui.pack_settings_panel`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> _key_label(2)
'D  ·  2♯'
>>> row = MenuRow("Clefs")
>>> row.title.text()
'<b>Clefs</b>'
```

## guard_last

```python
def guard_last(
    boxes: Iterable[QAbstractButton],
    *,
    enabled: bool = True,
) -> None
```

Disable the only checked box, so that at least one choice always
stays selected.

**Parameters**

- `boxes` (*iterable of QAbstractButton*): The checkboxes of one choice.
- `enabled` (*bool, default True*): False disables them all (for when the whole choice is switched off). Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> first, second = QCheckBox(), QCheckBox()
>>> first.setChecked(True)
>>> guard_last([first, second])
>>> first.isEnabled(), second.isEnabled()
(False, True)
>>> second.setChecked(True)
>>> guard_last([first, second])
>>> first.isEnabled()
True
```

## arrow_button

```python
def arrow_button(
    kind: Qt.ArrowType,
    *,
    tip: str,
) -> QToolButton
```

Make a small arrow button that repeats while it is held.

**Parameters**

- `kind` (*Qt.ArrowType*): Which way the arrow points.
- `tip` (*str*): The tooltip. Keyword-only.

**Returns**

- *QToolButton*: The button.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> button = arrow_button(
...     Qt.ArrowType.UpArrow,
...     tip="Raise the lowest note",
... )
>>> button.toolTip(), button.autoRepeat()
('Raise the lowest note', True)
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

Arrows on the left move the lower bound, arrows on the right move
the upper bound.

**Attributes**

- `edited` (*Signal*): Emitted with the clef key, the lowest note and the highest note (as staff steps) after a change.
- `key` (*str*): The clef.
- `low` (*int*): The lowest note asked, as a staff step (`Note.diatonic`).
- `high` (*int*): The highest note asked.
- `limits` (*tuple of (int, int)*): The furthest the bounds may go.
- `staff` (*StaffWidget*): Shows the two notes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = RangeEditor(
...     "treble", low=28, high=34
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> RangeEditor(
...     "bass", low=14, high=28
... ).limits == settings.RANGE_LIMITS["bass"]
True
>>> RangeEditor(
...     "alto", low=21, high=30, limits=(21, 30)
... ).limits
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

C major is on the left, then two rows of seven dots: 1 to 7 sharps
on the top row and 1 to 7 flats on the bottom.
Selected keys are filled, the rest are hollow.

**Attributes**

- `DOT, PITCH, ROW_GAP, PAD` (*float*): The dot radius and the spacing, in pixels.
- `keys` (*set of int*): The selected key signatures: sharps if positive, flats if negative.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyDiagram({0, 2}).toolTip()
'C, D'
```

**Constructor**

Create the diagram.

**Parameters**

- `keys` (*set of int or None, default None*): The key signatures to show as selected.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyDiagram({0, 1, -1}).grab().isNull()
False
```

## label_with_picture

```python
def label_with_picture(
    button: QAbstractButton,
    *,
    picture: _Picture,
    name: str,
) -> None
```

Label a checkbox or radio button with a picture instead of text.

The name stays as the tooltip and the accessible name.

**Parameters**

- `button` (*QAbstractButton*): The button to label.
- `picture` (*_Picture*): The picture (a clef, a note value ...). Keyword-only.
- `name` (*str*): What it is called. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> box = QCheckBox()
>>> label_with_picture(
...     box,
...     picture=ClefPictures(["treble"]),
...     name="Treble",
... )
>>> box.toolTip(), box.accessibleName()
('Treble', 'Treble')
```

## clef_choice_page

```python
def clef_choice_page(
    choices: Iterable[str],
    *,
    selected: set[str],
    edited: Callable[[], object],
    back: Callable[[], object],
    title: str = 'Clefs',
    hint: str = 'One of the checked clefs is picked at random.',
) -> tuple[dict[str, QCheckBox], QWidget]
```

Build the "Clefs" page that every exercise with a choice of clefs
shares.

**Parameters**

- `choices` (*iterable of str*): The clefs to offer, from `settings.RANGE_KEYS`; "grand" is left out of exercises that cannot use the grand staff.
- `selected` (*set of str*): The clefs that start checked. Keyword-only.
- `edited` (*callable*): Called whenever a box is checked or unchecked. Keyword-only.
- `back` (*callable*): Called when the Back button is clicked. Keyword-only.
- `title` (*str, default "Clefs"*): The page's title. Keyword-only.
- `hint` (*str, default "One of the checked clefs is picked at random."*): The gray line above the list. Keyword-only.

**Returns**

- *dict of str to QCheckBox*: The checkbox of each clef offered.
- *QWidget*: The page, with its title. The last checked clef cannot be unchecked.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> checked = []
>>> boxes_, page_ = clef_choice_page(
...     ("treble", "bass"),
...     selected={"bass"},
...     edited=lambda: checked.append(1),
...     back=lambda: None,
... )
>>> boxes_[
...     "bass"
... ].isEnabled()  # it is the only one checked, so it stays checked
False
>>> boxes_["treble"].setChecked(True)
>>> (
...     sorted(
...         c
...         for c, ticked_box in boxes_.items()
...         if ticked_box.isChecked()
...     ),
...     checked,
... )
(['bass', 'treble'], [1])
```

## show_keys

```python
def show_keys(
    row: MenuRow,
    *,
    diagram: KeyDiagram,
    enabled: bool,
    keys: set[int],
) -> None
```

Show the selected keys as a diagram in a menu row, or "Off" when key
signatures are switched off.

**Parameters**

- `row` (*MenuRow*): The menu row.
- `diagram` (*KeyDiagram*): The diagram to update. Keyword-only.
- `enabled` (*bool*): Whether key signatures are on. Keyword-only.
- `keys` (*set of int*): The selected key signatures. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row_, diagram_ = (
...     MenuRow("Key signatures"),
...     KeyDiagram(),
... )
>>> show_keys(
...     row_,
...     diagram=diagram_,
...     enabled=False,
...     keys={0},
... )
>>> row_.value.text(), diagram_.isHidden()
('Off', True)
```

## MenuRow

```python
MenuRow(
    title: str,
    *,
    chevron: bool = True,
    tall: bool = False,
)
```

Bases: `QPushButton`

A menu row: title on the left, current value and a chevron on the
right.

A `tall` row puts a picture on a second line of its own, using the
full width, for summaries that need room to be
readable.

**Attributes**

- `tall` (*bool*): Whether the row has a second line.
- `title` (*QLabel*): The title.
- `value` (*QLabel*): The current value, shown on the right.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = MenuRow("Range", tall=True)
>>> row.tall, row.title.text()
(True, '<b>Range</b>')
```

**Constructor**

Build the row.

**Parameters**

- `title` (*str*): The row's title.
- `chevron` (*bool, default True*): Show a chevron on the right, to say it opens a page. Keyword-only.
- `tall` (*bool, default False*): Give the row a second line for a picture. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MenuRow("Clefs").minimumHeight()
48
```

### MenuRow.attach

```python
def attach(widget: QWidget) -> None
```

Put a widget in the row.

Just after the value text, or (in a tall row) centered on its
own line below.

**Parameters**

- `widget` (*QWidget*): The widget, usually a small picture of the current choice.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = MenuRow("Clefs")
>>> picture = ClefPictures(["treble"])
>>> row.attach(picture)
>>> # noinspection PyUnresolvedReferences
>>> row.layout().indexOf(picture)
2
```

### MenuRow.fit

```python
def fit() -> None
```

Make a tall row as high as its contents need.

A button does not size itself to a layout inside it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = MenuRow("Range", tall=True)
>>> row.attach(QLabel("a picture"))
>>> row.minimumHeight() > 0
True
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

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> Switch().isChecked()
False
```

### Switch.setChecked

```python
def setChecked(on: bool) -> None
```

Turn the switch on or off without animating, as when a setting
is loaded.

**Parameters**

- `on` (*bool*): The new state.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> Switch().sizeHint()
PySide6.QtCore.QSize(42, 24)
```

## ToggleRow

```python
ToggleRow(title: str)
```

Bases: `MenuRow`

A menu row with a switch that changes a setting in place instead of
opening a page.

**Attributes**

- `switched` (*Signal*): Emitted with the new state when the row is clicked.
- `switch` (*Switch*): The switch.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = ToggleRow("Accidentals")
>>> changes = []
>>> _ = row.switched.connect(changes.append)
>>> row.click()
>>> changes, row.isOn()
([True], True)
```

**Constructor**

Build the row with its switch off.

**Parameters**

- `title` (*str*): The row's title.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ToggleRow("Accidentals").isOn()
False
```

### ToggleRow.isOn

```python
def isOn() -> bool
```

Report whether the switch is on.

**Returns**

- *bool*: True if on.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ToggleRow("Accidentals").isOn()
False
```

### ToggleRow.setOn

```python
def setOn(on: bool) -> None
```

Set the switch without announcing it, as when a setting is
loaded.

**Parameters**

- `on` (*bool*): The new state.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = ToggleRow("Accidentals")
>>> row.setOn(True)
>>> row.isOn()
True
```

## subpage

```python
def subpage(
    title: str,
    *,
    body: QWidget,
    back: Callable[[], object],
    fill: bool = False,
) -> QWidget
```

Build a second-layer page: a Back button and title above a body.

**Parameters**

- `title` (*str*): The page's title.
- `body` (*QWidget*): What the page shows. Keyword-only.
- `back` (*callable*): Called when Back is clicked. Keyword-only.
- `fill` (*bool, default False*): Let the body take all the room (so a long page can scroll) instead of leaving space below it. Keyword-only.

**Returns**

- *QWidget*: The page.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> calls = []
>>> page_ = subpage(
...     "Clefs",
...     body=QWidget(),
...     back=lambda: calls.append("back"),
... )
>>> next(
...     b
...     for b in page_.findChildren(QToolButton)
...     if b.text() == "‹ Back"
... ).click()
>>> calls
['back']
```

## SlideStack

```python
SlideStack(parent: QWidget | None = None)
```

Bases: `QStackedWidget`

A stacked widget whose pages slide in from the right (going deeper)
or the left (going back).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> SlideStack().sliding
False
```

### SlideStack.slide_to

```python
def slide_to(index: int) -> None
```

Slide to another page.

Going to a later page slides it in from the right and going back
slides it in from the left. A request made during a
slide, or for the page already showing, is ignored.

**Parameters**

- `index` (*int*): The page to go to.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

What every exercise's settings pane has in common: it says when a
setting has been edited.

**Attributes**

- `changed` (*Signal*): Emitted after any setting is edited that changes what is asked, so the exercise asks a new question.
- `restyled` (*Signal*): Emitted after a setting is edited that changes only how the exercise looks, so the question stays and the picture is drawn again.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ExerciseSettingsPanel()
>>> got = []
>>> _ = panel.changed.connect(
...     lambda: got.append(1)
... )
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

```text
Switching to ASRS hides the row and leaves its submenu.
```

## KeyboardRangePanel

```python
class KeyboardRangePanel(ExerciseSettingsPanel)
```

Settings for selecting a practice range on a keyboard.

**Examples**

```text
Keyboard note identification allows the lowest and highest keys to
coincide.
```

## ClefsPanel

```python
class ClefsPanel(ExerciseSettingsPanel)
```

A settings pane with a Clefs page, whose checkboxes choose the clefs
that are asked about.

**Attributes**

- `cfg` (*ClefChoice*): The settings being edited.
- `boxes` (*dict of str to QCheckBox*): The checkbox of each clef.
- `clef_pictures` (*ClefPictures*): The clefs shown in the menu's Clefs row.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.ui.settings_panel import (
...     ClefBasicsSettingsPanel,
... )
>>> isinstance(
...     ClefBasicsSettingsPanel(
...         settings.ClefBasicsSettings()
...     ),
...     ClefsPanel,
... )
True
```

## StaffRangePanel

```python
class StaffRangePanel(ClefsPanel)
```

Shared navigation and per-clef pitch range editors.

**Examples**

```text
Note and interval identification both open Range on page two.
```

## NoteAnswerSettingsPanel

```python
class NoteAnswerSettingsPanel(StaffRangePanel)
```

Staff range settings for note names and optional octaves.

**Examples**

```text
A plugin and the built-in note identification exercise can both
require the octave in an answer.
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

Checkboxes for the 15 major keys, flats on the left and sharps on
the right.

At least one stays checked. Each is labeled with a picture of its
signature.

**Attributes**

- `changed` (*Signal*): Emitted after a box is checked or unchecked.
- `boxes` (*dict of int to QCheckBox*): The checkbox of each key signature, from -7 (seven flats) to 7 (seven sharps).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
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

The key signature sub-page: a switch for using key signatures at
all, and the keys to draw from.

**Attributes**

- `changed` (*Signal*): Emitted after the switch or a key is changed.
- `switch_row` (*ToggleRow*): The "Use key signatures" switch.
- `checklist` (*KeyChecklist*): The keys; only enabled while the switch is on.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = KeySignaturePage(
...     True, selected={0, 1}
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePage(
...     True, selected={0}
... ).enabled()
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePage(
...     True, selected={-2, 0}
... ).selected() == {-2, 0}
True
```

## ScaleKeyPicker

```python
ScaleKeyPicker(
    *,
    major_keys: set[int],
    minor_keys: set[int],
)
```

Bases: `QTabWidget`

Select major and minor keys independently.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleKeyPicker(
...     major_keys={0}, minor_keys={-2}
... ).count()
2
```

**Constructor**

Build one checklist per mode.

**Parameters**

- `major_keys` (*set of int*): Selected major signatures. Keyword-only.
- `minor_keys` (*set of int*): Selected minor signatures. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleKeyPicker(
...     major_keys=set(), minor_keys={0}
... ).currentIndex()
1
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

Checkboxes for a list of choices, optionally under headings and
allowing an empty selection.

**Attributes**

- `changed` (*Signal*): Emitted after a box is checked or unchecked.
- `allow_empty` (*bool*): Whether all choices may be unchecked.
- `boxes` (*dict*): The checkbox of each choice, by its key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> groups = [
...     (
...         "Triads",
...         [
...             ("major", "Major"),
...             ("minor", "Minor"),
...         ],
...     ),
...     ("", [("x", "Other")]),
... ]
>>> checklist = ChoiceChecklist(
...     groups, selected={"major"}
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> checklist = ChoiceChecklist(
...     [("", [(0, "Root"), (1, "1st")])],
...     selected={0},
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> ChoiceChecklist(
...     [("", [(0, "Root"), (1, "1st")])],
...     selected={0, 1},
... ).selected()
{0, 1}
```

## buttons_page

```python
def buttons_page(
    cfg: ButtonSettings | settings.IntervalSettings | settings.ScaleIdentificationSettings,
    *,
    changed: Callable[[], None],
    back: Callable[[], None],
) -> QWidget
```

Build the shared Limited and All answer-button submenu.

**Parameters**

- `cfg` (*ButtonSettings or IntervalSettings*): The exercise that owns the button mode and count.
- `changed` (*callable*): Save and apply an edit.
- `back` (*callable*): Return to the exercise settings menu.

**Returns**

- *QWidget*: The Buttons page with the count picker below Limited.

**Examples**

```text
Choosing All hides the count picker and retains its last value.
```

## direction_choices

```python
def direction_choices(
    cfg: settings.ScaleIdentificationSettings | settings.ScaleConstructionSettings,
    *,
    edited: Callable[[], None],
) -> QWidget
```

Choose the direction of a scale.

**Parameters**

- `cfg` (*ScaleIdentificationSettings or ScaleConstructionSettings*): The exercise settings that store the selected motion.
- `edited` (*callable*): Save the edit and refresh the exercise.

**Returns**

- *QWidget*: A pair of mutually exclusive Ascending and Descending radio buttons.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = settings.ScaleIdentificationSettings()
>>> choices = direction_choices(
...     cfg, edited=lambda: None
... )
>>> next(
...     b
...     for b in choices.findChildren(
...         QRadioButton
...     )
...     if b.text() == "Descending"
... ).click()
>>> cfg.motion
'descending'
```

## scrolling

```python
def scrolling(body: QWidget) -> QScrollArea
```

Put a page's body in a scroll area, so a long page scrolls inside
the pane and never makes the window taller.

**Parameters**

- `body` (*QWidget*): What the page shows.

**Returns**

- *QScrollArea*: The scroll area that holds it, with no frame and no sideways scrolling.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = QWidget()
>>> scrolling(page).widget() is page
True
```
{% endraw %}
