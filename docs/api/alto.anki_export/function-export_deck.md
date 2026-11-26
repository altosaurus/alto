---
title: export_deck
parent: alto.anki_export
api_module: alto.anki_export
package: alto
permalink: /api/alto.anki_export/function-export_deck/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def export_deck(
    path: Path,
    *,
    exercise: Exercise,
    reviews: Sequence[Review],
    render: Callable[[Question, Path], list[str]],
) -> int
```

{% endraw %}{% include api-source.html name="export_deck" line=187 %}{% raw %}

</div>

Write a deck and replace the destination only after the package is
complete.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `path` | `Path` | Destination package. |
| `exercise` | `Exercise` | Source of questions under the current export settings. |
| `reviews` | `sequence of Review` | Eligible schedules to prioritize and transfer when requested. |
| `render` | `callable` | Produces Anki fields and writes their PNG illustrations in the working directory. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | Number of exported cards. An empty selection leaves the destination untouched. |
{% endraw %}
