---
title: format_size
parent: alto.ui.instrument_picker
api_module: alto.ui.instrument_picker
package: alto.ui
permalink: /api/alto.ui.instrument_picker/function-format_size/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def format_size(nbytes: int) -> str
```

{% endraw %}{% include api-source.html name="format_size" line=202 %}{% raw %}

</div>

Write a file size the way the instrument page shows it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `nbytes` | `int` | The size in bytes. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Megabytes with one decimal from a million bytes, otherwise whole kilobytes (at least 1). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     format_size(2_500_000),
...     format_size(500_000),
...     format_size(10),
... )
('2.5 MB', '500 KB', '1 KB')
```
{% endraw %}
