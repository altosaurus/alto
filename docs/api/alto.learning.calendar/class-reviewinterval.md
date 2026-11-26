---
title: ReviewInterval
parent: alto.learning.calendar
api_module: alto.learning.calendar
package: alto.learning
permalink: /api/alto.learning.calendar/class-reviewinterval/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ReviewInterval(
    seconds: int,
    identity: tuple[int, str, str, str],
    previous_state: str | None,
    rating: Rating = Rating.Good,
    graded_state: str | None = None,
    previous_due: float | None = None,
)
```

{% endraw %}{% include api-source.html name="ReviewInterval" line=105 %}{% raw %}

</div>

A preview of one rating for a card in its current scheduling state.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ReviewInterval(
...     600,
...     (1, "NoteNames", "abc", "FSRS"),
...     None,
... ).seconds
600
```

## ReviewInterval.duration

<div class="api-signature" markdown="1">

```python
@property
def duration() -> str
```

{% endraw %}{% include api-source.html name="ReviewInterval.duration" line=127 %}{% raw %}

</div>

Format a review interval for display above a grade button or
beside the music.

**Returns**

| Type | Description |
| --- | --- |
| `str` | A whole-day interval or a short learning step in minutes and seconds. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ReviewInterval(
...     330,
...     (1, "NoteNames", "abc", "FSRS"),
...     None,
... ).duration
'5 min 30 s'
```
{% endraw %}
