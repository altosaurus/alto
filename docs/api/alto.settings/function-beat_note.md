---
title: beat_note
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/function-beat_note/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
@cache
def beat_note(value: str) -> tuple[str, int, Fraction]
```

{% endraw %}{% include api-source.html name="beat_note" line=808 %}{% raw %}

</div>

Read a rhythm token's written value, tuplet count, and duration.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `str` | A note or rest, optionally prefixed with a tuplet name. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of str, int, and Fraction` | Written value, group size (zero for ordinary notes), and exact length in sixteenth notes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> beat_note("triplet-eighth")
('eighth', 3, Fraction(4, 3))
```
{% endraw %}
