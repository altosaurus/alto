---
title: FingerboardPosition
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/class-fingerboardposition/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
FingerboardPosition(
    strings: tuple[str, ...],
    string: int,
    note: str,
    instrument: str = '',
)
```

{% endraw %}{% include api-source.html name="FingerboardPosition" line=47 %}{% raw %}

</div>

A written pitch on one string, with the tuning needed to redraw it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> FingerboardPosition(
...     ("C3", "G3", "D4", "A4"), 2, "E4"
... ).string
2
```
{% endraw %}
