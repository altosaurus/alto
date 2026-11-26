---
title: busy_progress_bar
parent: alto.ui.widgets
api_module: alto.ui.widgets
package: alto.ui
permalink: /api/alto.ui.widgets/function-busy_progress_bar/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def busy_progress_bar() -> QProgressBar
```

{% endraw %}{% include api-source.html name="busy_progress_bar" line=77 %}{% raw %}

</div>

Create the indeterminate progress indicator used during updates.

**Returns**

| Type | Description |
| --- | --- |
| `QProgressBar` | A progress bar with no percentage label. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bar = busy_progress_bar()
>>> (
...     bar.minimum(),
...     bar.maximum(),
...     bar.isTextVisible(),
... )
(0, 0, False)
```
{% endraw %}
