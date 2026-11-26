---
title: ValuePictures
parent: alto.ui.pictures
api_module: alto.ui.pictures
package: alto.ui
permalink: /api/alto.ui.pictures/class-valuepictures/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ValuePictures(
    values: list[str] | None = None,
    *,
    scale: float = 1.0,
    center_stemless: bool = False,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ValuePictures" line=800 %}{% raw %}

</div>

Bases: `_Picture`

Note values as engraved symbols (no staff), each with its head on
the same baseline so they line up.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `values` | `list of str` | The note values shown, keys of `VALUE_NAMES`. |
| `center_stemless` | `bool` | Whether the double whole note and whole note sit at the picture's vertical center. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = ValuePictures(
...     ["whole", "quarter", "eighth"]
... )
>>> pictures.values
['whole', 'quarter', 'eighth']
```

**Constructor**

Create the picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `values` | `list of str or None, default None` | The note values to show. |
| `scale` | `float, default 1.0` | How much to enlarge it. Keyword-only. |
| `center_stemless` | `bool, default False` | Center double whole notes and whole notes vertically so they align with the middle of adjacent text. Other notes keep their heads low so their stems fit above. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ValuePictures(
...     ["half"], center_stemless=True
... ).center_stemless
True
```

## ValuePictures.set_values

<div class="api-signature" markdown="1">

```python
def set_values(values: list[str]) -> None
```

{% endraw %}{% include api-source.html name="ValuePictures.set_values" line=871 %}{% raw %}

</div>

Show different note values and size the picture for them.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `values` | `list of str` | The note values to show. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = ValuePictures()
>>> pictures.set_values(["breve", "whole"])
>>> pictures.values
['breve', 'whole']
```

## ValuePictures.icon

<div class="api-signature" markdown="1">

```python
@classmethod
def icon(
    value: str,
    *,
    scale: float = 1.7,
) -> QIcon
```

{% endraw %}{% include api-source.html name="ValuePictures.icon" line=899 %}{% raw %}

</div>

Return one note value as an icon.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `str` | A key of `VALUE_NAMES`. |
| `scale` | `float, default 1.7` | How much to enlarge it. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QIcon` | The icon. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ValuePictures.icon("quarter").isNull()
False
```

## ValuePictures.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="ValuePictures.paintEvent" line=927 %}{% raw %}

</div>

Draw each note value.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ValuePictures(
...     ["whole", "half", "quarter"]
... ).grab().isNull()
False
```
{% endraw %}
