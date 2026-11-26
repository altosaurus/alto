---
title: KeyDiagram
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-keydiagram/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyDiagram(
    keys: set[int] | None = None,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyDiagram" line=432 %}{% raw %}

</div>

Bases: `QWidget`

A small fork showing which key signatures are selected.

C major is on the left, then two rows of seven dots: 1 to 7 sharps
on the top row and 1 to 7 flats on the bottom.
Selected keys are filled, the rest are hollow.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `DOT, PITCH, ROW_GAP, PAD` | `float` | The dot radius and the spacing, in pixels. |
| `keys` | `set of int` | The selected key signatures: sharps if positive, flats if negative. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyDiagram({0, 2}).toolTip()
'C, D'
```

**Constructor**

Create the diagram.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `keys` | `set of int or None, default None` | The key signatures to show as selected. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyDiagram().keys
set()
```

## KeyDiagram.set_keys

<div class="api-signature" markdown="1">

```python
def set_keys(keys: set[int]) -> None
```

{% endraw %}{% include api-source.html name="KeyDiagram.set_keys" line=507 %}{% raw %}

</div>

Choose which key signatures are shown as selected.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `keys` | `set of int` | Sharps if positive, flats if negative. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> diagram = KeyDiagram()
>>> diagram.set_keys({2, -1, 0})
>>> diagram.toolTip()
'C, D, F'
```

## KeyDiagram.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyDiagram.paintEvent" line=545 %}{% raw %}

</div>

Draw a dot for each key signature, filled when selected.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyDiagram({0, 1, -1}).grab().isNull()
False
```
{% endraw %}
