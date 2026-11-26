---
title: SchemeThumb
parent: alto.ui.circle_colors
api_module: alto.ui.circle_colors
package: alto.ui
permalink: /api/alto.ui.circle_colors/class-schemethumb/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
SchemeThumb(
    scheme: Scheme,
    *,
    size: int = THUMB,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="SchemeThumb" line=98 %}{% raw %}

</div>

Bases: `QPushButton`

A small picture of the circle in a color scheme, to click to choose
the scheme.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `scheme` | `Scheme` | The scheme it shows and chooses. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> thumb = SchemeThumb(preset("paper"))
>>> thumb.isCheckable(), thumb.toolTip()
(True, 'Pastel wedges of every hue with dark names, which deepen
when lit.')
```

**Constructor**

Build the picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scheme` | `Scheme` | The color scheme to draw. |
| `size` | `int, default 112` | Its width and height in pixels. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> SchemeThumb(
...     preset("paper"), size=80
... ).width()
80
```

## SchemeThumb.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="SchemeThumb.sizeHint" line=153 %}{% raw %}

</div>

Return the size it asks for.

**Returns**

| Type | Description |
| --- | --- |
| `QSize` | The size it was built with. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> SchemeThumb(
...     preset("paper"), size=90
... ).sizeHint().width()
90
```

## SchemeThumb.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="SchemeThumb.paintEvent" line=172 %}{% raw %}

</div>

Draw the circle, with one cell asked and its relative lit, and a
ring around it when it is the chosen scheme.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> SchemeThumb(
...     preset("midnight")
... ).grab().isNull()
False
```
{% endraw %}
