---
title: signature
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/function-signature/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def signature(*parts: object) -> str
```

{% endraw %}{% include api-source.html name="signature" line=1008 %}{% raw %}

</div>

Describe the exercise settings in force, so a stored question is
only asked again under the settings it was made for.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `*parts` | `object` | The settings to describe: dataclasses, dictionaries, lists, sets and plain values, nested as needed. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | A JSON string that is the same for equal settings, however their sets and dictionaries happen to be ordered. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> signature({"clefs": {"bass", "treble"}}, 3)
'[{"clefs": ["bass", "treble"]}, 3]'
>>> signature(
...     {"clefs": {"treble", "bass"}}, 3
... ) == signature(
...     {"clefs": {"bass", "treble"}}, 3
... )
True
```
{% endraw %}
