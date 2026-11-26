---
title: Switch
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-switch/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Switch(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="Switch" line=1095 %}{% raw %}

</div>

Bases: `QAbstractButton`

A pill-shaped on/off switch whose knob slides across when toggled.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `W, H` | `int` | The switch's size, in pixels. |

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

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Switch().isChecked()
False
```

## Switch.setChecked

<div class="api-signature" markdown="1">

```python
def setChecked(on: bool) -> None
```

{% endraw %}{% include api-source.html name="Switch.setChecked" line=1180 %}{% raw %}

</div>

Turn the switch on or off without animating, as when a setting
is loaded.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `on` | `bool` | The new state. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> switch = Switch()
>>> switch.setChecked(True)
>>> switch._pos
1.0
```

## Switch.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="Switch.paintEvent" line=1204 %}{% raw %}

</div>

Draw the track, tinted between off and on, and the knob.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Switch().grab().isNull()
False
```

## Switch.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="Switch.sizeHint" line=1236 %}{% raw %}

</div>

Return the switch's fixed size.

**Returns**

| Type | Description |
| --- | --- |
| `QSize` | `W` by `H`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Switch().sizeHint()
PySide6.QtCore.QSize(42, 24)
```
{% endraw %}
