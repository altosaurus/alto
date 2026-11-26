---
title: diatonic_name
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/function-diatonic_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def diatonic_name(d: int) -> str
```

{% endraw %}{% include api-source.html name="diatonic_name" line=307 %}{% raw %}

</div>

Return the name and octave of the natural note on a staff step.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `d` | `int` | The staff-step index (see `Note.diatonic`). |

**Returns**

| Type | Description |
| --- | --- |
| `str` | For example 'E4'. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> diatonic_name(30)
'E4'
```
{% endraw %}
