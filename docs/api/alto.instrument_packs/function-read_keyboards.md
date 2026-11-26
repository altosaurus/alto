---
title: read_keyboards
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_keyboards/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_keyboards(
    value: object,
    *,
    where: str,
) -> tuple[PackKeyboard, ...]
```

{% endraw %}{% include api-source.html name="read_keyboards" line=1264 %}{% raw %}

</div>

Validate the optional keyboards of an instrument, which Alto draws
from their ranges.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The instrument's ``keyboards`` entry, a list of objects, or None. |
| `where` | `str` | The instrument's qualified key, used in messages. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of PackKeyboard` | The keyboards in the order the manifest lists them, which is the order Alto draws them from top to bottom. Empty when none were declared. |

**Raises**

- *ValueError*: If the entry is not a short list of keyboards with distinct names and natural end keys.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_keyboards(None, where="pack.v.va")
()
>>> read_keyboards(
...     [
...         {
...             "name": "Manual",
...             "lowest": "C4",
...             "highest": "E4",
...         }
...     ],
...     where="pack.v.va",
... )[0].naturals
3
```
{% endraw %}
