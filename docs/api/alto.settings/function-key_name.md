---
title: key_name
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/function-key_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def key_name(midi: int) -> str
```

{% endraw %}{% include api-source.html name="key_name" line=860 %}{% raw %}

</div>

Return the name of a MIDI note with its octave, black keys as
sharps.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `midi` | `int` | The MIDI note number. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | For example 'C4' for 60 and 'C♯4' for 61. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> key_name(60), key_name(61)
('C4', 'C♯4')
```
{% endraw %}
