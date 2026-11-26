---
title: TileCard
parent: alto.ui.home
api_module: alto.ui.home
package: alto.ui
permalink: /api/alto.ui.home/class-tilecard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
TileCard(
    *,
    icon: str,
    category: str,
    name: str,
    about: str,
    progress: tuple[int, int] | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="TileCard" line=314 %}{% raw %}

</div>

Bases: `QPushButton`

A big button: an icon on top, then a category, a name and a short
description, and optionally a lesson's progress.

Progress takes no room in the layout: a strip along the bottom edge
shows it, and "Step N/M" sits in the top-right
corner, both only once the lesson has been begun. A card with or
without progress therefore has the same size and the
same icon.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = TileCard(
...     icon=icons.EXERCISE_CIRCLE,
...     category="Scales & Keys",
...     name="Circle of Fifths",
...     about="Find keys.",
... )
>>> (card.width(), card.height()) == (
...     CARD_W,
...     CARD_H,
... )
True
>>> card.accessibleName()
'Circle of Fifths, Scales & Keys'
```

**Constructor**

Build a card.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `icon` | `str` | The inside of a 24 by 24 SVG, drawn in the text color. Keyword-only. |
| `category` | `str` | The small heading above the name. Keyword-only. |
| `name` | `str` | The name. Keyword-only. |
| `about` | `str` | A line of description, which is also the tooltip. Keyword-only. |
| `progress` | `tuple of int or None, default None` | The step you are on, counting from 0, and how many steps there are. The bar and "Step N/M" appear only once the first step has been passed; nothing is drawn if None or at step 0. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the card. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = TileCard(
...     icon=icons.HELP,
...     category="Help",
...     name="Help",
...     about="Get help.",
...     progress=(1, 8),
... )
>>> card.toolTip(), card.accessibleDescription()
('Get help.', 'Get help. Continue at step 2 of 8.')
```

## TileCard.changeEvent

<div class="api-signature" markdown="1">

```python
def changeEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="TileCard.changeEvent" line=496 %}{% raw %}

</div>

Recolor the icon when the tile receives a new palette.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QEvent` | The widget change delivered by Qt. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = lesson_card(LESSONS[0])
>>> card.changeEvent(
...     QEvent(QEvent.Type.PaletteChange)
... )
```
{% endraw %}
