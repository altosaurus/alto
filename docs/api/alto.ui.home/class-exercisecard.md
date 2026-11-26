---
title: ExerciseCard
parent: alto.ui.home
api_module: alto.ui.home
package: alto.ui
permalink: /api/alto.ui.home/class-exercisecard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ExerciseCard(
    cls: type[Exercise],
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ExerciseCard" line=575 %}{% raw %}

</div>

Bases: `TileCard`

The card of an exercise: its icon on top, then its category, name
and a one-line description.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> card = ExerciseCard(NoteNames)
>>> card.toolTip() == NoteNames.description
True
>>> (card.width(), card.height()) == (
...     CARD_W,
...     CARD_H,
... )
True
```

**Constructor**

Build the card for one exercise.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cls` | `type of Exercise` | The exercise class; its name, category and description are shown, and its class name picks the icon. |
| `parent` | `QWidget or None, default None` | The widget that owns the card. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     IntervalNames,
... )
>>> ExerciseCard(IntervalNames).toolTip()
'Name the interval between two notes.'
```

## ExerciseCard.set_counts

<div class="api-signature" markdown="1">

```python
def set_counts(counts: tuple[int, int] | tuple[int, int, int] | None) -> None
```

{% endraw %}{% include api-source.html name="ExerciseCard.set_counts" line=633 %}{% raw %}

</div>

Show due reviews, new cards, and outstanding incorrect cards in
the upper right corner.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `counts` | `tuple of int or None` | Reviews due, new cards available, and optionally the outstanding incorrect count. None hides the counts. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> card = ExerciseCard(NoteNames)
>>> card.set_counts((2, 3, 1))
>>> print(card.counts.toolTip())
Blue — 3 new cards available
Red — 1 incorrect card awaiting a correct answer
Green — 2 reviews due
```
{% endraw %}
