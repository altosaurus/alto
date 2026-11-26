---
title: ClefPictures
parent: alto.ui.pictures
api_module: alto.ui.pictures
package: alto.ui
permalink: /api/alto.ui.pictures/class-clefpictures/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ClefPictures(
    clefs: list[str] | None = None,
    *,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ClefPictures" line=560 %}{% raw %}

</div>

Bases: `_Picture`

The selected clefs, each on its own five-line staff, and a two-stave
picture with a brace for the grand staff.

Showing each clef on its own staff lets alto and tenor, which share
a symbol, look different.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `H, W, GAP, SPACING` | `float` | The picture's height, the width of one clef, the distance between staff lines and the space between clefs. |
| `NAMES` | `dict of str to str` | The name of each clef. |
| `clefs` | `list of str` | The clefs shown. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefPictures(["alto", "tenor"]).toolTip()
'Alto, Tenor'
```

**Constructor**

Create the picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clefs` | `list of str or None, default None` | The clefs to show, any of `CLEF_NAMES`. |
| `scale` | `float, default 1.0` | How much to enlarge it. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefPictures(["treble"], scale=2.0).width()
60
```

## ClefPictures.set_clefs

<div class="api-signature" markdown="1">

```python
def set_clefs(clefs: list[str]) -> None
```

{% endraw %}{% include api-source.html name="ClefPictures.set_clefs" line=616 %}{% raw %}

</div>

Show different clefs and size the picture for them.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clefs` | `list of str` | The clefs to show, any of `CLEF_NAMES`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = ClefPictures()
>>> pictures.set_clefs(
...     ["treble", "bass", "alto"]
... )
>>> pictures.width()  # three clefs and the space between them
106
>>> pictures.toolTip()
'Treble, Bass, Alto'
```

## ClefPictures.icon

<div class="api-signature" markdown="1">

```python
@classmethod
def icon(
    clef: str,
    *,
    scale: float = 1.8,
) -> QIcon
```

{% endraw %}{% include api-source.html name="ClefPictures.icon" line=643 %}{% raw %}

</div>

Return one clef as an icon.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | A key of `CLEF_NAMES`. |
| `scale` | `float, default 1.8` | How much to enlarge it. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QIcon` | The icon. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefPictures.icon("grand").isNull()
False
```

## ClefPictures.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="ClefPictures.paintEvent" line=671 %}{% raw %}

</div>

Draw each clef on its staff, or the grand staff with its brace.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefPictures(
...     ["treble", "grand"]
... ).grab().isNull()
False
```
{% endraw %}
