---
title: joined
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-joined/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def joined(
    values: Iterable[object],
    *,
    separator: str = ',',
) -> str
```

{% endraw %}{% include api-source.html name="joined" line=418 %}{% raw %}

</div>

Write values as the text that `list_value`, `choices_value` and
`keys_value` read back.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `values` | `iterable of object` | The values, in the order to save them. |
| `separator` | `str, default ","` | What to put between them. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The values as text, joined by the separator. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     joined([-1, 0, 2]),
...     joined(
...         ["major", "minor"], separator="|"
...     ),
... )
('-1,0,2', 'major|minor')
```
{% endraw %}
