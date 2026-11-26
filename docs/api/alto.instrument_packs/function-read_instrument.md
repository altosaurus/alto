---
title: read_instrument
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_instrument/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_instrument(
    row: object,
    *,
    pack: str,
    files: PackFiles,
    pack_name: str = '',
) -> PackInstrument
```

{% endraw %}{% include api-source.html name="read_instrument" line=1450 %}{% raw %}

</div>

Validate one declared instrument against its own artwork and
recordings.

**Returns**

| Type | Description |
| --- | --- |
| `PackInstrument` | The calibrated instrument available to exercises in this pack. |

**Raises**

- *ValueError*: If a required field, string, image, or recording is invalid.
{% endraw %}
