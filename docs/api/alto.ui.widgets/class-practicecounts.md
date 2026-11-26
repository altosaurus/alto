---
title: PracticeCounts
parent: alto.ui.widgets
api_module: alto.ui.widgets
package: alto.ui
permalink: /api/alto.ui.widgets/class-practicecounts/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class PracticeCounts(QLabel)
```

{% endraw %}{% include api-source.html name="PracticeCounts" line=102 %}{% raw %}

</div>

Colored counts for calendar practice on tiles and in the exercise
screen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> label = PracticeCounts()
>>> label.set_counts(
...     (2, 3, 1),
...     studying=True,
...     current="incorrect",
... )
>>> "1 incorrect card" in label.toolTip()
True
```

## PracticeCounts.set_counts

<div class="api-signature" markdown="1">

```python
def set_counts(
    counts: tuple[int, int, int],
    *,
    studying: bool = False,
    current: str | None = None,
    totals: bool = False,
) -> None
```

{% endraw %}{% include api-source.html name="PracticeCounts.set_counts" line=121 %}{% raw %}

</div>

Show the counts in blue, red, green order and underline the
active queue.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `counts` | `tuple of int` | Due reviews, new cards, and outstanding incorrect cards. |
| `studying` | `bool` | Separate the exercise screen's counts with slashes. |
| `current` | `str or None` | The queue of the unanswered card, or None between cards. |
| `totals` | `bool` | Label the grid totals and show one queue per line. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> label = PracticeCounts()
>>> label.set_counts((1, 2, 0))
>>> label.toolTip().startswith(
...     "Blue — 2 new cards available"
... )
True
```
{% endraw %}
