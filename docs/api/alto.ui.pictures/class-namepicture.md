---
title: NamePicture
parent: alto.ui.pictures
api_module: alto.ui.pictures
package: alto.ui
permalink: /api/alto.ui.pictures/class-namepicture/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
NamePicture(
    naming: str = 'letters',
    *,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="NamePicture" line=1575 %}{% raw %}

</div>

Bases: `_Picture`

How notes are named: C, D and E on a staff, labeled with letters,
solfège syllables or scale degrees.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `H, W` | `float` | The picture's height and width. |
| `LETTERS, SYLLABLES` | `tuple of str` | The two sets of labels. |
| `naming` | `str` | "letters", "solfege", "degrees" (caret) or "functions". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NamePicture("solfege").toolTip()
'Solfège (Do Re Mi)'
```

**Constructor**

Create the picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `naming` | `str, default "letters"` | "letters", "solfege", "degrees" (caret) or "functions". |
| `scale` | `float, default 1.0` | How much to enlarge it. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NamePicture().naming
'letters'
```

## NamePicture.set_naming

<div class="api-signature" markdown="1">

```python
def set_naming(naming: str) -> None
```

{% endraw %}{% include api-source.html name="NamePicture.set_naming" line=1627 %}{% raw %}

</div>

Choose which labels are drawn.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `naming` | `str` | "letters" for C D E, "solfege" for Do Re Mi, or "degrees" for 1̂ 2̂ 3̂, or "functions" for function names. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picture = NamePicture()
>>> picture.set_naming("solfege")
>>> picture.toolTip()
'Solfège (Do Re Mi)'
```

## NamePicture.icon

<div class="api-signature" markdown="1">

```python
@classmethod
def icon(
    naming: str,
    *,
    scale: float = 1.6,
) -> QIcon
```

{% endraw %}{% include api-source.html name="NamePicture.icon" line=1653 %}{% raw %}

</div>

Return the picture as an icon.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `naming` | `str` | "letters", "solfege", "degrees" (caret) or "functions". |
| `scale` | `float, default 1.6` | How much to enlarge it. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QIcon` | The icon. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NamePicture.icon("letters").isNull()
False
```

## NamePicture.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="NamePicture.paintEvent" line=1681 %}{% raw %}

</div>

Draw the staff, the clef, the three notes and their labels.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NamePicture("letters").grab().isNull()
False
```
{% endraw %}
