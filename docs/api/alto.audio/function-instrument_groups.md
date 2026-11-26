---
title: instrument_groups
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/function-instrument_groups/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def instrument_groups() -> list[tuple[str, list[Instrument]]]
```

{% endraw %}{% include api-source.html name="instrument_groups" line=371 %}{% raw %}

</div>

Return the instruments as they are listed for choosing.

Ways of playing one instrument share a single entry.

**Returns**

| Type | Description |
| --- | --- |
| `list of tuple of (str, list of Instrument)` | Each entry's picker group and its instruments, in the order listed. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [name for name, _ in instrument_groups()]
['Piano', 'Flute', 'French Horn', 'Viola', 'Marimba', 'Vibraphone']
>>> [
...     inst_.variant
...     for inst_ in dict(instrument_groups())[
...         "Viola"
...     ]
... ]
['Arco', 'Pizzicato']
```
{% endraw %}
