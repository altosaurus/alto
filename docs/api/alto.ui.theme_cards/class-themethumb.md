---
title: ThemeThumb
parent: alto.ui.theme_cards
api_module: alto.ui.theme_cards
package: alto.ui
permalink: /api/alto.ui.theme_cards/class-themethumb/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ThemeThumb(
    key: str,
    *,
    colors: dict[str, str],
    other: dict[str, str] | None = None,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ThemeThumb" line=116 %}{% raw %}

</div>

Bases: `QPushButton`

A small picture of the window in a theme, to click to choose the
theme.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `theme_key` | `str` | The key of the theme it chooses. |
| `colors` | `dict of str to str` | The colors it is drawn in. |
| `other` | `dict of str to str or None` | The colors of the dark half, for a picture that is cut through on a slant; None for a plain one. |
| `scale_by` | `float` | How many times bigger than the smallest size it is drawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ThemeThumb("dark", colors=DARK).theme_key
'dark'
```

**Constructor**

Build the picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The theme it chooses. |
| `colors` | `dict of str to str` | The colors of the picture, or of its light half. |
| `other` | `dict of str to str or None, default None` | The colors of its dark half, for a picture cut through on a slant. Keyword-only. |
| `scale` | `float, default 1.0` | How many times bigger than the smallest size to draw it. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     ThemeThumb(
...         "system", colors=LIGHT, other=DARK
...     ).width(),
...     ThemeThumb(
...         "light", colors=LIGHT, scale=2.0
...     ).width(),
... )
(116, 232)
```

## ThemeThumb.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="ThemeThumb.paintEvent" line=191 %}{% raw %}

</div>

Draw the window, cut through on a slant if it has two halves,
with an outline that is heavier when it is chosen.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ThemeThumb(
...     "light", colors=LIGHT
... ).grab().isNull()
False
```
{% endraw %}
