---
title: make_sides
parent: alto.ui.transition_preview
api_module: alto.ui.transition_preview
package: alto.ui
permalink: /api/alto.ui.transition_preview/function-make_sides/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def make_sides() -> tuple[list[TileCard], list[TileCard]]
```

{% endraw %}{% include api-source.html name="make_sides" line=79 %}{% raw %}

</div>

Make the cards for the two sides of the preview: the app's own
exercise cards, and its lesson cards.

The lessons side has the real lesson, and a few examples that are
marked as such, so that a transition has more than one
card to move.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (list of TileCard, list of TileCard)` | The cards of the exercises side, and of the lessons side. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> first, second = make_sides()
>>> len(first), len(second) > len(LESSONS)
(6, True)
```
{% endraw %}
