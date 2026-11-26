---
title: made
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-made/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def made(
    key: str,
    *,
    label: str,
    about: str,
    leaving: Motion | None,
    arriving: Motion,
) -> Transition
```

{% endraw %}{% include api-source.html name="made" line=1102 %}{% raw %}

</div>

Make a transition from motions.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | What it is saved as. |
| `label` | `str` | What the settings call it. Keyword-only. |
| `about` | `str` | A sentence saying what it looks like. Keyword-only. |
| `leaving` | `Motion or None` | What the old cards do. Keyword-only. |
| `arriving` | `Motion` | What the new cards do. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Transition` | The transition. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> made(
...     "x",
...     label="X",
...     about="Does x.",
...     leaving=None,
...     arriving=Motion(),
... ).key
'x'
```
{% endraw %}
