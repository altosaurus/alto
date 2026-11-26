---
title: lesson_card
parent: alto.ui.home
api_module: alto.ui.home
package: alto.ui
permalink: /api/alto.ui.home/function-lesson_card/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def lesson_card(
    lesson: Lesson,
    *,
    parent: QWidget | None = None,
) -> TileCard
```

{% endraw %}{% include api-source.html name="lesson_card" line=674 %}{% raw %}

</div>

Make the card of a lesson: the icon of the exercise that practices
the same topic, and a bar for how far through it you are.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `lesson` | `Lesson` | The lesson. |
| `parent` | `QWidget or None, default None` | The widget that owns the card. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `TileCard` | The card, with a progress bar and "Step N/M" in its corner once the lesson has been begun. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = lesson_card(LESSONS[0])
>>> card.accessibleName()
'Pitches and Notes, Notation'
```
{% endraw %}
