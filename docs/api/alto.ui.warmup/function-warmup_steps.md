---
title: warmup_steps
parent: alto.ui.warmup
api_module: alto.ui.warmup
package: alto.ui
permalink: /api/alto.ui.warmup/function-warmup_steps/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def warmup_steps() -> list[Callable[[], None]]
```

{% endraw %}{% include api-source.html name="warmup_steps" line=195 %}{% raw %}

</div>

List the steps of the warm-up.

They draw a staff; lay out text in the application's own font size
and each style sheet size, plain and bold, at the zoom;
and, while sound is on, make the notes the current instrument has no
recording of.

**Returns**

| Type | Description |
| --- | --- |
| `list of callable` | The steps, each a few tens of milliseconds at most. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> notes = (
...     len(sounds.unrecorded())
...     if sounds.enabled
...     else 0
... )
>>> len(
...     warmup_steps()
... # the staff, eleven sizes in two weights, and the notes
... ) == 1 + 22 + notes
True
```
{% endraw %}
