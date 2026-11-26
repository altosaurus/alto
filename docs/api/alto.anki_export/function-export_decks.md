---
title: export_decks
parent: alto.anki_export
api_module: alto.anki_export
package: alto
permalink: /api/alto.anki_export/function-export_decks/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def export_decks(
    path: Path,
    *,
    selections: Sequence[DeckSelection],
    render: Callable[[Question, Path, Exercise], list[str]],
    progress: Callable[[str, int, int], None] | None = None,
) -> int
```

{% endraw %}{% include api-source.html name="export_decks" line=274 %}{% raw %}

</div>

Save the selected exercise decks together in one Anki package.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `path` | `Path` | Destination replaced once all selected decks and their media are ready. |
| `selections` | `sequence of DeckSelection` | Exercises to export and their optional schedules. |
| `render` | `callable` | Renders the fields and writes the media for one exercise question. |
| `progress` | `callable, optional` | Receives the current operation, completed work, and a fixed total for the whole package. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | Total cards written across all decks. |
{% endraw %}
