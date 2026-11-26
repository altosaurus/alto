---
title: keyboard_interval_name
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/function-keyboard_interval_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def keyboard_interval_name(distance: int) -> str
```

{% endraw %}{% include api-source.html name="keyboard_interval_name" line=962 %}{% raw %}

</div>

Name a keyboard interval by its distance, including compound
intervals.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `distance` | `int` | The distance in half steps, from 1 through the full piano span. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | A conventional interval name, with both spellings for tritones. |

**Raises**

- *ValueError*: If the distance cannot occur between two distinct piano keys.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     keyboard_interval_name(13),
...     keyboard_interval_name(18),
...     keyboard_interval_name(24),
... )
('m9', 'A11 / d12', 'P15')
>>> keyboard_interval_name(87)
'm52'
```
{% endraw %}
