---
title: alto.ui.widgets
parent: api
package: alto.ui
permalink: /api/alto.ui.widgets/
---
{% raw %}
Small widgets shared by several screens: the sidebar toggle, the help
button and a segmented control.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SidebarToggle().toolTip()
'Hide exercise list'
```

## vertical_scroll_area

<div class="api-signature" markdown="1">

```python
def vertical_scroll_area(body: QWidget) -> QScrollArea
```

{% endraw %}{% include api-source.html name="vertical_scroll_area" line=48 %}{% raw %}

</div>

Put a resizable widget in a frameless vertical scroll area.

**Parameters**

- `body` (*QWidget*): Contents of the viewport.

**Returns**

- *QScrollArea*: The scroll area containing the body.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> body = QWidget()
>>> scroll = vertical_scroll_area(body)
>>> scroll.widget() is body
True
```

## busy_progress_bar

<div class="api-signature" markdown="1">

```python
def busy_progress_bar() -> QProgressBar
```

{% endraw %}{% include api-source.html name="busy_progress_bar" line=77 %}{% raw %}

</div>

Create the indeterminate progress indicator used during updates.

**Returns**

- *QProgressBar*: A progress bar with no percentage label.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bar = busy_progress_bar()
>>> (
...     bar.minimum(),
...     bar.maximum(),
...     bar.isTextVisible(),
... )
(0, 0, False)
```

## PracticeCounts

<div class="api-signature" markdown="1">

```python
class PracticeCounts(QLabel)
```

{% endraw %}{% include api-source.html name="PracticeCounts" line=102 %}{% raw %}

</div>

Colored counts for calendar practice on tiles and in the exercise
screen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> label = PracticeCounts()
>>> label.set_counts(
...     (2, 3, 1),
...     studying=True,
...     current="incorrect",
... )
>>> "1 incorrect card" in label.toolTip()
True
```

### PracticeCounts.set_counts

<div class="api-signature" markdown="1">

```python
def set_counts(
    counts: tuple[int, int, int],
    *,
    studying: bool = False,
    current: str | None = None,
    totals: bool = False,
) -> None
```

{% endraw %}{% include api-source.html name="PracticeCounts.set_counts" line=121 %}{% raw %}

</div>

Show the counts in blue, red, green order and underline the
active queue.

**Parameters**

- `counts` (*tuple of int*): Due reviews, new cards, and outstanding incorrect cards.
- `studying` (*bool*): Separate the exercise screen's counts with slashes.
- `current` (*str or None*): The queue of the unanswered card, or None between cards.
- `totals` (*bool*): Label the grid totals and show one queue per line.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> label = PracticeCounts()
>>> label.set_counts((1, 2, 0))
>>> label.toolTip().startswith(
...     "Blue — 2 new cards available"
... )
True
```

## SidebarToggle

<div class="api-signature" markdown="1">

```python
SidebarToggle(
    parent: QWidget | None = None,
    *,
    noun: str = 'exercise list',
)
```

{% endraw %}{% include api-source.html name="SidebarToggle" line=216 %}{% raw %}

</div>

Bases: `QToolButton`

A button that shows or hides the exercise list.

Connect to `clicked`; the main window decides what to show and calls
`set_open` to match.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> SidebarToggle().autoRaise()
True
>>> SidebarToggle(noun="lesson list").toolTip()
'Hide lesson list'
```

### SidebarToggle.set_open

<div class="api-signature" markdown="1">

```python
def set_open(is_open: bool) -> None
```

{% endraw %}{% include api-source.html name="SidebarToggle.set_open" line=265 %}{% raw %}

</div>

Show the icon and tooltip for the list being open or closed.

**Parameters**

- `is_open` (*bool*): True if the exercise list is showing.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> button = SidebarToggle()
>>> button.set_open(False)
>>> button.toolTip()
'Show exercise list'
```

## HelpButton

<div class="api-signature" markdown="1">

```python
HelpButton(
    text_provider: Callable[[], str],
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="HelpButton" line=290 %}{% raw %}

</div>

Bases: `QToolButton`

A "?" button that opens a small popover with help text.

Click anywhere else to close it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HelpButton(
...     lambda: "<b>Press the right note.</b>"
... ).toolTip()
'How this exercise works'
```

**Constructor**

Create the button.

**Parameters**

- `text_provider` (*callable*): Called with no arguments each time the help is shown, so the text can follow the current settings. It returns simple HTML.
- `parent` (*QWidget or None, default None*): The widget that owns the button. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> calls = []
>>> button = HelpButton(
...     lambda: calls.append(1) or "help"
... )
>>> # the text is not asked for until the button is clicked
>>> calls
[]
```

### HelpButton.show_help

<div class="api-signature" markdown="1">

```python
def show_help() -> None
```

{% endraw %}{% include api-source.html name="HelpButton.show_help" line=343 %}{% raw %}

</div>

Open the popover under the button, right-aligned with it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HelpButton(
...     lambda: "<b>Help</b>"
... ).show_help()  # doctest: +SKIP
```

## SegmentedControl

<div class="api-signature" markdown="1">

```python
SegmentedControl(
    labels: Sequence[str],
    *,
    icons: Sequence[str] = (),
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="SegmentedControl" line=389 %}{% raw %}

</div>

Bases: `QFrame`

A pill-shaped row of choices of which exactly one is chosen, like
the switch between two views.

**Attributes**

- `buttons` (*list of QPushButton*): One per choice, in order.
- `chosen` (*Signal*): Emitted with the number of the choice when the learner picks one.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> control = SegmentedControl(
...     ["Exercises", "Lessons"]
... )
>>> control.current()
0
>>> control.set_current(1)
>>> (
...     control.current(),
...     control.buttons[1].isChecked(),
... )
(1, True)
```

**Constructor**

Build the control with the first choice chosen.

**Parameters**

- `labels` (*sequence of str*): The text of each choice.
- `icons` (*sequence of str, default ()*): The icon of each choice, as the inside of a 24 by 24 SVG; fewer than the labels, or none, leaves the rest without. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(
...     SegmentedControl(
...         ["A", "B", "C"]
...     ).buttons
... )
3
>>> SegmentedControl(
...     ["A"], icons=[HELP]
... ).buttons[0].icon().isNull()
False
```

### SegmentedControl.set_compact

<div class="api-signature" markdown="1">

```python
def set_compact(compact: bool) -> None
```

{% endraw %}{% include api-source.html name="SegmentedControl.set_compact" line=485 %}{% raw %}

</div>

Show only the icons, or the icons and the text.

The text is still the tooltip and the name a screen reader says.

**Parameters**

- `compact` (*bool*): True to hide the text.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> control = SegmentedControl(
...     ["Exercises", "Lessons"],
...     icons=[HELP, HELP],
... )
>>> control.set_compact(True)
>>> (
...     control.buttons[0].text(),
...     control.buttons[0].toolTip(),
... )
('', 'Exercises')
>>> control.set_compact(False)
>>> control.buttons[0].text()
'Exercises'
```

### SegmentedControl.current

<div class="api-signature" markdown="1">

```python
def current() -> int
```

{% endraw %}{% include api-source.html name="SegmentedControl.current" line=515 %}{% raw %}

</div>

Return the number of the chosen choice.

**Returns**

- *int*: The choice, from 0.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SegmentedControl(["A", "B"]).current()
0
```

### SegmentedControl.set_current

<div class="api-signature" markdown="1">

```python
def set_current(number: int) -> None
```

{% endraw %}{% include api-source.html name="SegmentedControl.set_current" line=531 %}{% raw %}

</div>

Choose one, without announcing it.

**Parameters**

- `number` (*int*): The choice, from 0.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> control = SegmentedControl(["A", "B"])
>>> control.set_current(1)
>>> control.current()
1
```

### SegmentedControl.restyle

<div class="api-signature" markdown="1">

```python
def restyle() -> None
```

{% endraw %}{% include api-source.html name="SegmentedControl.restyle" line=549 %}{% raw %}

</div>

Style the control from the palette now in use: a rounded track
with the chosen choice raised and tinted.

A change of theme rebuilds the main window, so the control there
is drawn afresh in the new colors. One that stays, as in
the settings, is restyled by calling this.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "segments" in SegmentedControl(
...     ["A", "B"]
... ).styleSheet()
True
```
{% endraw %}
