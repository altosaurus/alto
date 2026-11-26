---
title: card_fields
parent: alto.ui.anki_exporter
api_module: alto.ui.anki_exporter
package: alto.ui
permalink: /api/alto.ui.anki_exporter/function-card_fields/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def card_fields(
    question: Question,
    *,
    folder: Path,
    exercise: Exercise,
) -> list[str]
```

{% endraw %}{% include api-source.html name="card_fields" line=136 %}{% raw %}

</div>

Render an exercise as a reveal-and-grade card.

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The prompt, illustrations, answer, and explanation fields as HTML. |
{% endraw %}
