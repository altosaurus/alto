---
title: SegmentedControl
parent: alto.ui.widgets
api_module: alto.ui.widgets
package: alto.ui
permalink: /api/alto.ui.widgets/class-segmentedcontrol/
---
{% raw %}
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

| Attribute | Type | Description |
| --- | --- | --- |
| `buttons` | `list of QPushButton` | One per choice, in order. |
| `chosen` | `Signal` | Emitted with the number of the choice when the learner picks one. |

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

| Parameter | Type | Description |
| --- | --- | --- |
| `labels` | `sequence of str` | The text of each choice. |
| `icons` | `sequence of str, default ()` | The icon of each choice, as the inside of a 24 by 24 SVG; fewer than the labels, or none, leaves the rest without. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

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

## SegmentedControl.set_compact

<div class="api-signature" markdown="1">

```python
def set_compact(compact: bool) -> None
```

{% endraw %}{% include api-source.html name="SegmentedControl.set_compact" line=485 %}{% raw %}

</div>

Show only the icons, or the icons and the text.

The text is still the tooltip and the name a screen reader says.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `compact` | `bool` | True to hide the text. |

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

## SegmentedControl.current

<div class="api-signature" markdown="1">

```python
def current() -> int
```

{% endraw %}{% include api-source.html name="SegmentedControl.current" line=515 %}{% raw %}

</div>

Return the number of the chosen choice.

**Returns**

| Type | Description |
| --- | --- |
| `int` | The choice, from 0. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SegmentedControl(["A", "B"]).current()
0
```

## SegmentedControl.set_current

<div class="api-signature" markdown="1">

```python
def set_current(number: int) -> None
```

{% endraw %}{% include api-source.html name="SegmentedControl.set_current" line=531 %}{% raw %}

</div>

Choose one, without announcing it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `number` | `int` | The choice, from 0. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> control = SegmentedControl(["A", "B"])
>>> control.set_current(1)
>>> control.current()
1
```

## SegmentedControl.restyle

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
