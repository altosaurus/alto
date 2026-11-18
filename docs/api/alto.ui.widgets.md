---
title: alto.ui.widgets
parent: api
package: alto.ui
order: 68
permalink: /api/alto.ui.widgets/
---
{% raw %}
Small widgets shared by several screens: the sidebar toggle, the help button and a segmented control.

**Examples**

```pycon
>>> SidebarToggle().toolTip()
'Hide exercise list'
```

## SidebarToggle

```python
SidebarToggle(
    parent: QWidget | None = None,
    *,
    noun: str = 'exercise list',
)
```

Bases: `QToolButton`

A button that shows or hides the exercise list.

Connect to `clicked`; the main window decides what to show and calls `set_open` to match.

**Examples**

```pycon
>>> button = SidebarToggle()
>>> button.toolTip()
'Hide exercise list'
>>> button.set_open(False)
>>> button.toolTip()
'Show exercise list'
```

**Constructor**

Create the toggle, showing the list as open.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the button.
- `noun` (*str, default "exercise list"*): What the list is called in the tooltip: "Hide exercise list". Keyword-only.

**Constructor examples**

```pycon
>>> SidebarToggle().autoRaise()
True
>>> SidebarToggle(noun="lesson list").toolTip()
'Hide lesson list'
```

### SidebarToggle.set_open

```python
def set_open(is_open: bool) -> None
```

Show the icon and tooltip for the list being open or closed.

**Parameters**

- `is_open` (*bool*): True if the exercise list is showing.

**Examples**

```pycon
>>> button = SidebarToggle()
>>> button.set_open(False)
>>> button.toolTip()
'Show exercise list'
```

## HelpButton

```python
HelpButton(
    text_provider: Callable[[], str],
    *,
    parent: QWidget | None = None,
)
```

Bases: `QToolButton`

A "?" button that opens a small popover with help text.

Click anywhere else to close it.

**Examples**

```pycon
>>> HelpButton(lambda: "<b>Press the right note.</b>").toolTip()
'How this exercise works'
```

**Constructor**

Create the button.

**Parameters**

- `text_provider` (*callable*): Called with no arguments each time the help is shown, so the text can follow the current settings. It returns simple HTML.
- `parent` (*QWidget or None, default None*): The widget that owns the button. Keyword-only.

**Constructor examples**

```pycon
>>> calls = []
>>> button = HelpButton(lambda: calls.append(1) or "help")
>>> calls  # the text is not asked for until the button is clicked
[]
```

### HelpButton.show_help

```python
def show_help() -> None
```

Open the popover under the button, right-aligned with it.

**Examples**

```pycon
>>> HelpButton(lambda: "<b>Help</b>").show_help()  # doctest: +SKIP
```

## SegmentedControl

```python
SegmentedControl(
    labels: Sequence[str],
    *,
    icons: Sequence[str] = (),
    parent: QWidget | None = None,
)
```

Bases: `QFrame`

A pill-shaped row of choices of which exactly one is chosen, like the switch between two views.

**Attributes**

- `buttons` (*list of QPushButton*): One per choice, in order.
- `chosen` (*Signal*): Emitted with the number of the choice when the learner picks one.

**Examples**

```pycon
>>> control = SegmentedControl(["Exercises", "Lessons"])
>>> control.current()
0
>>> control.set_current(1)
>>> control.current(), control.buttons[1].isChecked()
(1, True)
```

**Constructor**

Build the control with the first choice chosen.

**Parameters**

- `labels` (*sequence of str*): The text of each choice.
- `icons` (*sequence of str, default ()*): The icon of each choice, as the inside of a 24 by 24 SVG; fewer than the labels, or none, leaves the rest without. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> len(SegmentedControl(["A", "B", "C"]).buttons)
3
>>> SegmentedControl(["A"], icons=[HELP]).buttons[0].icon().isNull()
False
```

### SegmentedControl.set_compact

```python
def set_compact(compact: bool) -> None
```

Show only the icons, or the icons and the text.

The text is still the tooltip and the name a screen reader says.

**Parameters**

- `compact` (*bool*): True to hide the text.

**Examples**

```pycon
>>> control = SegmentedControl(["Exercises", "Lessons"], icons=[HELP, HELP])
>>> control.set_compact(True)
>>> control.buttons[0].text(), control.buttons[0].toolTip()
('', 'Exercises')
>>> control.set_compact(False)
>>> control.buttons[0].text()
'Exercises'
```

### SegmentedControl.current

```python
def current() -> int
```

Return the number of the chosen choice.

**Returns**

- *int*: The choice, from 0.

**Examples**

```pycon
>>> SegmentedControl(["A", "B"]).current()
0
```

### SegmentedControl.set_current

```python
def set_current(number: int) -> None
```

Choose one, without announcing it.

**Parameters**

- `number` (*int*): The choice, from 0.

**Examples**

```pycon
>>> control = SegmentedControl(["A", "B"])
>>> control.set_current(1)
>>> control.current()
1
```

### SegmentedControl.restyle

```python
def restyle() -> None
```

Style the control from the palette now in use: a rounded track with the chosen choice raised and tinted.

A change of theme rebuilds the main window, so the control there is drawn afresh in the new colors. One that stays, as in
the settings, is restyled by calling this.

**Examples**

```pycon
>>> "segments" in SegmentedControl(["A", "B"]).styleSheet()
True
```
{% endraw %}
