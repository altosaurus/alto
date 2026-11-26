---
title: explain
parent: alto.theory.fifths
api_module: alto.theory.fifths
package: alto.theory
permalink: /api/alto.theory.fifths/function-explain/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def explain(
    ring: str,
    *,
    place: int,
) -> str
```

{% endraw %}{% include api-source.html name="explain" line=364 %}{% raw %}

</div>

Explain a cell of the circle: its key signature, where it comes
from, its relative key and its chords.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `ring` | `str` | "outer" for the major key at the place, "inner" for its relative minor. |
| `place` | `int` | The place on the circle, clockwise from C at 0. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML, a few short paragraphs. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> text = explain("outer", place=1)
>>> (
...     "<b>G major</b>" in text
...     and "1 sharp: F♯" in text
...     and "a fifth above C" in text
... )
True
>>> "relative major, <b>C major</b>" in explain(
...     "inner", place=0
... )
True
>>> "<b>C♭ major</b>" in explain(
...     "outer", place=5
... ) and "7 flats" in explain("outer", place=5)
True
```
{% endraw %}
