---
title: pitch
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-pitch/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def pitch(value: object) -> Note
```

{% endraw %}{% include api-source.html name="pitch" line=505 %}{% raw %}

</div>

Read a pitch spelled with an octave.

**Returns**

| Type | Description |
| --- | --- |
| `Note` | The pitch used for playback and grading. |

**Raises**

- *ValueError*: If the pitch has an unsupported spelling.
{% endraw %}
