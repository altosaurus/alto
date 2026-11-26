---
title: deck_candidates
parent: alto.anki_export
api_module: alto.anki_export
package: alto
permalink: /api/alto.anki_export/function-deck_candidates/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def deck_candidates(
    exercise: Exercise,
    *,
    reviews: Sequence[Review],
) -> Iterator[tuple[Question, Review | None]]
```

{% endraw %}{% include api-source.html name="deck_candidates" line=102 %}{% raw %}

</div>

Visit eligible scheduled examples before generating additional
questions.

**Yields**

- *tuple of Question and optional Review*: Question to render and its matching schedule, if available.
{% endraw %}
