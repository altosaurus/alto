---
title: RangePictures
parent: alto.ui.pictures
api_module: alto.ui.pictures
package: alto.ui
permalink: /api/alto.ui.pictures/class-rangepictures/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
RangePictures(
    items: list[tuple[str, int, int]] | None = None,
    *,
    scale: float = 1.0,
    max_width: float | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="RangePictures" line=1278 %}{% raw %}

</div>

Bases: `_Picture`

For each clef, a staff with its lowest and highest note, so the
range can be read off at a glance.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `H, W, SPACING` | `float` | The picture's height, the width of one staff and the space between staves. |
| `MAX_SCALE` | `float` | The most the picture is enlarged to fit `max_width`. |
| `max_width` | `float or None` | The width to enlarge the picture to, if any. |
| `items` | `list of tuple of (str, int, int)` | Each clef with its lowest and highest note, as staff steps (`Note.diatonic`). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = RangePictures(
...     [("treble", 22, 52)]
... )
>>> pictures.toolTip()
'Treble: D3 to F7'
```

**Constructor**

Create the picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `items` | `list of tuple of (str, int, int) or None, default None` | Each clef with its lowest and highest note. |
| `scale` | `float, default 1.0` | How much to enlarge it. Keyword-only. |
| `max_width` | `float or None, default None` | Enlarge the picture to use this width (up to `MAX_SCALE`) however many clefs there are. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RangePictures(
...     [("treble", 22, 52)], max_width=238
... ).scale
1.9
```

## RangePictures.set_items

<div class="api-signature" markdown="1">

```python
def set_items(items: list[tuple[str, int, int]]) -> None
```

{% endraw %}{% include api-source.html name="RangePictures.set_items" line=1343 %}{% raw %}

</div>

Show the ranges of some clefs and size the picture for them.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `items` | `list of tuple of (str, int, int)` | Each clef with its lowest and highest note, as staff steps (`Note.diatonic`). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = RangePictures()
>>> pictures.set_items(
...     [("bass", 10, 40), ("alto", 21, 35)]
... )
>>> pictures.toolTip().splitlines()
['Bass: F1 to A5', 'Alto: C3 to C5']
```

## RangePictures.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="RangePictures.paintEvent" line=1463 %}{% raw %}

</div>

Draw a staff for each clef with its lowest and highest note.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RangePictures(
...     [("treble", 22, 52), ("bass", 10, 40)]
... ).grab().isNull()
False
```
{% endraw %}
