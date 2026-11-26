---
title: write_decks
parent: alto.anki_export
api_module: alto.anki_export
package: alto
permalink: /api/alto.anki_export/function-write_decks/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def write_decks(
    path: Path,
    *,
    plans: Sequence[PlannedDeck],
    render: Callable[[Question, Path, Exercise], list[str]],
    progress: Callable[[str, int, int], None] | None = None,
    control: ExportControl | None = None,
    deck_progress: Callable[[int, bool], None] | None = None,
) -> int
```

{% endraw %}{% include api-source.html name="write_decks" line=363 %}{% raw %}

</div>

Write the cards from a completed export plan into a single package.

**Returns**

| Type | Description |
| --- | --- |
| `int` | Number of cards written across the selected decks. |
{% endraw %}
