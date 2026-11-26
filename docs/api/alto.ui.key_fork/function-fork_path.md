---
title: fork_path
parent: alto.ui.key_fork
api_module: alto.ui.key_fork
package: alto.ui
permalink: /api/alto.ui.key_fork/function-fork_path/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def fork_path() -> QPainterPath
```

{% endraw %}{% include api-source.html name="fork_path" line=314 %}{% raw %}

</div>

Return the outline of the fork: the stem, a half circle for the U,
and the two tines.

**Returns**

| Type | Description |
| --- | --- |
| `QPainterPath` | One smooth line, drawn from the end of the stem. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> outline = fork_path()
>>> (
...     outline.boundingRect().left() == STEM_X
...     and outline.boundingRect().top() == TOP_Y
... )
True
```
{% endraw %}
