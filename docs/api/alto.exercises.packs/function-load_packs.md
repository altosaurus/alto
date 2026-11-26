---
title: load_packs
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/function-load_packs/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_packs(folder: Path) -> list[str]
```

{% endraw %}{% include api-source.html name="load_packs" line=2076 %}{% raw %}

</div>

Register valid packs and return readable errors for any packs that
were skipped.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `folder` | `Path` | The plugins folder containing pack ZIPs or editable pack folders. |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | File names and reasons for packs that could not be loaded. |

**Examples**

```text
A missing plugins folder yields an empty list.
```
{% endraw %}
