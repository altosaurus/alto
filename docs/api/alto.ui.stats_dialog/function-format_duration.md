---
title: format_duration
parent: alto.ui.stats_dialog
api_module: alto.ui.stats_dialog
package: alto.ui
permalink: /api/alto.ui.stats_dialog/function-format_duration/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def format_duration(seconds: float) -> str
```

{% endraw %}{% include api-source.html name="format_duration" line=132 %}{% raw %}

</div>

Write a length of time the way the statistics show it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `seconds` | `float` | The time in seconds. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Seconds under half a minute, then minutes, then hours and minutes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     format_duration(5),
...     format_duration(90),
...     format_duration(3000),
... )
('5 s', '2 min', '50 min')
>>> format_duration(3 * 3600 + 7 * 60)
'3 h 07 min'
```
{% endraw %}
