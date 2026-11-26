---
title: coverage
parent: alto.instrument_info
api_module: alto.instrument_info
package: alto
permalink: /api/alto.instrument_info/function-coverage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def coverage(midis: Iterable[int]) -> Coverage
```

{% endraw %}{% include api-source.html name="coverage" line=292 %}{% raw %}

</div>

Summarize the notes that have a recording.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `midis` | `iterable of int` | The MIDI numbers of the recorded notes, in any order and with repeats allowed. |

**Returns**

| Type | Description |
| --- | --- |
| `Coverage` | The count, the range and the number of gaps. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> coverage([64, 60, 62])
Coverage(count=3, lowest=60, highest=64, gaps=2)
```
{% endraw %}
