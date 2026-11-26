---
title: record_of
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-record_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def record_of(
    key: str,
    *,
    name: str,
    mode: str,
    colors: list[str],
    light: bool = False,
) -> CustomRecord
```

{% endraw %}{% include api-source.html name="record_of" line=738 %}{% raw %}

</div>

Make the record of a scheme of the user's own.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | Its key, such as "custom-1". |
| `name` | `str` | Its name. Keyword-only. |
| `mode` | `str` | How its colors are made: a key of `MODES`. Keyword-only. |
| `colors` | `list of str` | The colors the mode takes, as "#rrggbb". Keyword-only. |
| `light` | `bool, default False` | Whether the wedges are light. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `CustomRecord` | The record. Nothing is checked: `clean_record` does that. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> record_of(
...     "custom-1",
...     name="Mine",
...     mode="single",
...     colors=["#2f6bd0"],
... )["light"]
False
```
{% endraw %}
