---
title: read_positions
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_positions/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_positions(
    value: object,
    *,
    where: str,
) -> tuple[tuple[int, str], ...]
```

{% endraw %}{% include api-source.html name="read_positions" line=1359 %}{% raw %}

</div>

Validate the optional named positions along a string, which label
the ruler beside the fingerboard.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The instrument's ``positions`` entry, a list of ``{"name": ..., "half_steps": ...}``, or None when it has none. |
| `where` | `str` | The instrument's qualified key, used in error messages. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (int, str)` | Each position's half steps above the open string and its name, in ascending order. Empty when none were declared. |

**Raises**

- *ValueError*: If the entry is not a short list of named, ascending positions with plain-text names.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_positions(
...     [
...         {"name": "1st", "half_steps": 2},
...         {"name": "2nd", "half_steps": 3},
...     ],
...     where="pack.v.va",
... )
((2, '1st'), (3, '2nd'))
>>> read_positions(None, where="pack.v.va")
()
```
{% endraw %}
