---
title: KeySignaturePicture
parent: alto.ui.pictures
api_module: alto.ui.pictures
package: alto.ui
permalink: /api/alto.ui.pictures/class-keysignaturepicture/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeySignaturePicture(
    key: int = 0,
    *,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeySignaturePicture" line=1065 %}{% raw %}

</div>

Bases: `_Picture`

A key signature as a plain row of its sharps or flats, with no staff
or clef.

Each sign sits at the height it has after a treble clef, and C
major, which has none, shows a natural sign.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `H, GAP, STEP` | `float` | The picture's height, the distance between staff lines and the space between signs. |
| `ORDER` | `dict of int to str` | Where each sign is written, in order, for sharps (1) and flats (-1). |
| `key` | `int` | The key signature: sharps if positive, flats if negative. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePicture(2).toolTip()
'D major: 2 sharps'
```

**Constructor**

Create the picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `int, default 0` | The key signature: that many sharps if positive, flats if negative. |
| `scale` | `float, default 1.0` | How much to enlarge it. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePicture(0).toolTip()
'C major: no sharps or flats'
>>> KeySignaturePicture(-1).toolTip()
'F major: 1 flat'
```

## KeySignaturePicture.icon

<div class="api-signature" markdown="1">

```python
@classmethod
def icon(
    key: int,
    *,
    scale: float = 1.2,
) -> QIcon
```

{% endraw %}{% include api-source.html name="KeySignaturePicture.icon" line=1146 %}{% raw %}

</div>

Return a key signature as an icon.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `int` | Sharps if positive, flats if negative. |
| `scale` | `float, default 1.2` | How much to enlarge it. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QIcon` | The icon. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePicture.icon(3).isNull()
False
```

## KeySignaturePicture.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="KeySignaturePicture.paintEvent" line=1240 %}{% raw %}

</div>

Draw the row of sharps or flats, or a natural sign for C major.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePicture(-3).grab().isNull()
False
```
{% endraw %}
